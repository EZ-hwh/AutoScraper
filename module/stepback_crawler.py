import json, re
from lxml import etree, html
from utils.html_utils import simplify_html, find_common_ancestor, get_absolute_xpath
from utils.step import domlm_parse
from bs4 import BeautifulSoup

role_prompt = '''Suppose you're a web parser that is good at reading and understanding the HTML code and can give clear executable code on the brower.'''
crawler_prompt = '''Please read the following HTML code, and then return an Xpath that can recognize the element in the HTML matching the instruction below. 

Instruction: {0}

Here're some hints:
1. Do not output the xpath with exact value or element appears in the HTML.
2. Do not output the xpath that indicate multi node with different value. It would be appreciate to use more @class to identify different node that may share the same xpath expression.
3. If the HTML code doesn't contain the suitable information match the instruction, keep the xpath and value attrs blank.
4. Avoid using some string function such as 'substring()' and 'normalize-space()' to normalize the text in the node.
Please output in the following Json format:
{{
    "thought": "", # a brief thought of how to confirm the value and generate the xpath
    "value": "", # the value extracted from the HTML that match the instruction, if there is no data, keep it blank
    "xpath": "" # a workable xpath to extract the value in the HTML
}}
Here's the HTML code:
```
{1}
```
'''

crawler_wr_prompt = '''Please read the following HTML code, and then return an Xpath that can recognize the element in the HTML matching the instruction below. 

Instruction: {0}
The element value: {1}

Here're some hints:
1. Do not output the xpath with exact value or element appears in the HTML.
2. Do not output the xpath that indicate multi node with different value. It would be appreciate to use more @class to identify different node that may share the same xpath expression.
3. If the HTML code doesn't contain the suitable information match the instruction, keep the xpath and value attrs blank.
4. Avoid using some string function such as 'substring()' and 'normalize-space()' to normalize the text in the node.
Please output in the following Json format:
{{
    "thought": "", # a brief thought of how to confirm the value and generate the xpath
    "xpath": "" # a workable xpath to extract the value in the HTML
}}
Here's the HTML code:
```
{2}
```
'''

stepback_prompt = '''Your main task is to judge whether the following HTML code contains all the expected value, which is recognized beforehand.
Instruction: {0}
And here's the value: {1}
The HTML code is as follow:
```
{2}
```

Please output your judgement in the following Json format:
{{
    "thought": "", # a brief thinking about whether the HTML code contains expected value
    "judgement": "" # whether the HTML code contains all extracted value. Return yes/no directly.
}}
'''

judgement_prompt = '''Your main task is to judge whether the extracted value is consistent with the expected value, which is recognized beforehand. Please pay attention for the following case:
    1) If the extracted result contains some elements that is not in expected value, or contains empty value, it is not consistent.
    2) The raw values containing redundant separators is considered as consistent because we can postprocess it.

The extracted value is: {0}
The expected value is: {1}

Please output your judgement in the following Json format:
{{
    "thought": "", # a brief thinking about whether the extracted value is consistent with the expected value
    "judgement": "" # return yes/no directly
}}
'''

synthesis_prompt = '''You're a perfect discriminator which is good at HTML understanding as well. Following the instruction, there are some action sequence written from several HTML and the corresponding result extracted from several HTML. Please choose one that can be best potentially adapted to the same extraction task on other webpage in the same websites. Here are the instruction of the task:
Instructions: {0}
The action sequences and the corresponding extracted results with different sequence on different webpage are as follow:
{1}

Please output the best action sequence in the following Json format:
{{
    "thought": "" # brief thinking about which to choose
    "number": "" # the best action sequence choosen from the candidates, starts from 0. If there is none, output 0.
}}
'''

class StepbackCrawler:
    def __init__(self,
                 simplify=True,
                 verbose=True,
                 api=None,
                 error_max_times=15):

        if api == None:
            raise ValueError("No api has been assigned!!")
        self.api = api
        self.is_simplify = simplify
        self.verbose = verbose
        self.error_max_times = error_max_times

    def request_parse(self, 
                      query: str,
                      keys: list[str] = []) -> dict[str, str]:
        """A safe and reliable call to LLMs, which confirm that the output can be parsed by json.loads().

        Args:
            query (str): the query to prompt the LLM
            html (str): the HTML text for 

        Returns:
            str: a dict parsed from the output of LLM
        """
        pattern = r'\{.*?\}'
        target = False
        for _ in range(self.error_max_times):
            response = self.api(query)
            matches = re.findall(pattern, response, re.DOTALL)
            try:
                for match in matches:
                    res = json.loads(match) # type: ignore
                    for key in keys:
                        assert res[key]
                    target = True
                if target:
                    break
            except:
                pass
        if target:
            #print(res)
            return res
        else:
            return {key:"" for key in keys}
        
    def generate_sequence_html(self,
                          instruction: str,
                          html_content: str,
                          ground_truth=None):

        action_sequence = []

        for _ in range(5):
            print(len(html_content))
            # Generate xpath & result
            if ground_truth:
                query = f'{role_prompt}/n{crawler_wr_prompt.format(instruction, ground_truth, html_content)}'
                res = self.request_parse(query, ['thought', 'xpath'])
                
                # Extract with xpath
                results = self.extract_with_xpath(html_content, res['xpath'])
                value = ground_truth
                xpath = res['xpath']

                print('-' * 50)
                print(value)
                print(results)
                print(xpath)

                if value == '':
                    return action_sequence

                query = f'{role_prompt}/n{judgement_prompt.format(str(results), value)}'

                res = self.request_parse(query, ['thought', 'judgement'])

                print(json.dumps(res, ensure_ascii=False, indent=4))
                if res['judgement'].lower() == 'yes':
                    action_sequence.append(xpath)
                    return action_sequence
            else:
                query = f'{role_prompt}/n{crawler_prompt.format(instruction, html_content)}'
                res = self.request_parse(query, ['thought', 'value', 'xpath'])
                
                # Extract with xpath
                results = self.extract_with_xpath(html_content, res['xpath'])
                value = res['value']
                xpath = res['xpath']

                print('-' * 50)
                print(value)
                print(results)
                print(xpath)

                if value == '':
                    return action_sequence

                query = f'{role_prompt}/n{judgement_prompt.format(str(results), value)}'

                res = self.request_parse(query, ['thought', 'judgement'])

                print(json.dumps(res, ensure_ascii=False, indent=4))
                if res['judgement'].lower() == 'yes':
                    action_sequence.append(xpath)
                    return action_sequence
            
            # Stepback
            while True:
                new_html_content = find_common_ancestor(html_content, xpath)
                query = f'{role_prompt}/n{stepback_prompt.format(instruction, value, new_html_content)}'
                res = self.request_parse(query, ['thought', 'judgement'])
                if res['judgement'] == 'yes' or new_html_content == html_content:
                    action_sequence.append(xpath)
                    break
                else:
                    xpath += '/..'

            # Forward
            # while True:
            #     new_html_content = find_common_ancestor(html_content, xpath)
            #     query = f'{role_prompt}/n{stepback_prompt.format(instruction, value, new_html_content)}'
            #     res = self.request_parse(query, ['thought', 'judgement'])
            #     if res['judgement'] == 'yes':
            #         action_sequence.append(xpath)
            #         break
            #     else:
            #         xpath += '/..'
            html_content = new_html_content
        return action_sequence

    def generate_sequence(self, instruction, html_content, ground_truth = None, max_token=8000):
        if self.is_simplify:
            html_content = simplify_html(html_content)
        #print(html_content)
        soup = BeautifulSoup(html_content, 'html.parser')
        subtree_list = domlm_parse(soup, max_token)
        print('Page split:', len(subtree_list))
        rule_list = []
        for sub_html in subtree_list:
            page_rule = self.generate_sequence_html(instruction, sub_html, ground_truth)
            rule_list.append(page_rule)
        
        if len(subtree_list) > 1:
            valid_answer = False
            for rule in rule_list:
                if rule != []:
                    valid_answer = True
            if not valid_answer:
                return []
            extract_result = []
            for rule in rule_list:
                sub_extract_result = {'rule':rule}
                sub_extract_result['extracted result'] = self.extract_with_sequence(html_content, rule)
                extract_result.append(sub_extract_result)
            print(json.dumps(extract_result, ensure_ascii=False, indent=4))
            query = synthesis_prompt.format(instruction, json.dumps(extract_result, indent=4))
            res = self.request_parse(query, ['thought', 'number'])
            try:
                return rule_list[eval(res['number'])]
            except:
                return rule_list[0]
        else:
            return rule_list[0]

    def rule_synthesis(self, 
                       website_name: str,
                       seed_html_set: list[str], 
                       instruction: str, 
                       ground_truth = None,
                       max_token = 8000,
                       per_page_repeat_time=1):
        rule_list = []

        # Collect a rule from each seed webpage
        if ground_truth:
            for html_content, gt in zip(seed_html_set, ground_truth):
                page_rule = self.generate_sequence(instruction, html_content, gt, max_token=max_token)
                rule_list.append(page_rule)
        else:
            for html_content in seed_html_set:
                page_rule = self.generate_sequence(instruction, html_content, max_token=max_token)
                rule_list.append(page_rule)

        #rule_list = list(set(rule_list))
        print(rule_list)
        if len(seed_html_set) > 1:
            valid_answer = False
            for rule in rule_list:
                if rule != []:
                    valid_answer = True
            if not valid_answer:
                return []
            extract_result = []
            for rule in rule_list:
                sub_extract_result = {'rule':rule, 'extracted result':[]}
                for html_content in seed_html_set:
                    sub_extract_result['extracted result'].append(self.extract_with_sequence(html_content, rule))
                extract_result.append(sub_extract_result)
            print('+' * 100)
            print(f"Systhesis rule for the website {website_name}")
            print(json.dumps(extract_result, ensure_ascii=False, indent=4))
            query = synthesis_prompt.format(instruction, json.dumps(extract_result, indent=4))
            res = self.request_parse(query, ['thought', 'number'])
            try:
                return rule_list[eval(res['number'])]
            except:
                return rule_list[0]
        else:
            return rule_list[0]
        
    def rule_synthesis_cul(self, 
                       website_name: str,
                       seed_html_set: list[str], 
                       instruction: str, 
                       ground_truth = None,
                       max_token = 8000,
                       per_page_repeat_time=1):
        rule_list_set = []
        rule_list = []

        # Collect a rule from each seed webpage
        if ground_truth:
            for html_content, gt in zip(seed_html_set, ground_truth):
                page_rule = self.generate_sequence(instruction, html_content, gt, max_token=max_token)
                rule_list.append(page_rule)
        else:
            for html_content in seed_html_set:
                page_rule = self.generate_sequence(instruction, html_content, max_token=max_token)
                rule_list.append(page_rule)

        #rule_list = list(set(rule_list))
        print(rule_list)
        for webnum in range(2, len(seed_html_set) + 1):
            valid_answer = False
            for rule in rule_list[:webnum]:
                if rule != []:
                    valid_answer = True
            if not valid_answer:
                return []
            extract_result = []
            for rule in rule_list[:webnum]:
                sub_extract_result = {'rule':rule, 'extracted result':[]}
                for html_content in seed_html_set[:webnum]:
                    sub_extract_result['extracted result'].append(self.extract_with_sequence(html_content, rule))
                extract_result.append(sub_extract_result)
            print('+' * 100)
            print(f"Systhesis rule for the website {website_name}")
            print(json.dumps(extract_result, ensure_ascii=False, indent=4))
            query = synthesis_prompt.format(instruction, json.dumps(extract_result, indent=4))
            res = self.request_parse(query, ['thought', 'number'])
            try:
                rule_list_set.append(rule_list[eval(res['number'])])
            except:
                rule_list_set.append(rule_list[0])
        return rule_list_set
        
    def extract_with_xpath(self, 
                           html_content:str, 
                           xpath:str) -> list[str]:
        """Xpath Parser

        Args:
            html_content (str): text of HTML
            xpath (str): the string of xpath

        Returns:
            list[str]: result extracted by xpath
        """
        if self.is_simplify:
            html_content = simplify_html(html_content)
        try:
            if xpath.strip():
                ele = etree.HTML(html_content) # type: ignore
                return [item.strip() if isinstance(item, str) else item.text.strip() for item in ele.xpath(xpath)]
            else:
                return []
        except:
            return []
        
    def extract_with_sequence(self,
                              html_content:str,
                              sequence:str):
        if self.is_simplify:
            html_content = simplify_html(html_content)
        if sequence == []:
            return []
        else:
            tot_len = len(sequence)
            for index, xpath in enumerate(sequence):
                if index != tot_len - 1:
                    try:
                        html_content = find_common_ancestor(html_content, xpath)
                    except:
                        pass
                else:
                    return self.extract_with_xpath(html_content, xpath)