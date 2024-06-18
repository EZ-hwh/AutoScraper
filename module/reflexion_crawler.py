from .prompt import *
import json, re
from lxml import etree, html
from utils.html_utils import simplify_html, find_common_ancestor
from utils.step import domlm_parse
from bs4 import BeautifulSoup

class AutoCrawler:
    '''
    AutoCrawler is a LLM-based agent, which generate different kinds of rule, such as Xpath, for information extraction and web proning.
    '''
    def __init__(self, 
                 pattern='xpath', 
                 simplify=True, 
                 verbose=True,
                 api=None,
                 error_max_times=15):
        """Initial an instance of Autocrawler, including setting the pattern of rule 

        Args:
            pattern (str, optional): Which kind of rule pattern will be used. **Options: ['reflexion', 'cot']**. Defaults to 'xpath'.
            simplify (bool, optional): Whether to simplify HTML before proprecessing. Defaults to True.
            verbose (bool, optional): Whether print the whole execution process. Defaults to True.
        """
        if api == None:
            raise ValueError("No api has been assigned!!")
        self.api = api
        if pattern not in ['reflexion', 'cot']:
            raise AssertionError("Pattern must be one of the following selection: reflexion, cot")
        self.rule_pattern = pattern
        self.is_simplify = simplify
        self.verbose = verbose
        self.prompter = Xpath_prompter()
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
                #res = eval(response)
                for match in matches:
                    res = json.loads(match) # type: ignore
                    for key in keys:
                        assert res[key]
                        if key == 'consistent':
                            assert res[key] in ['yes', 'no']
                    target = True
                    break
                if target:
                    break
            except:
                pass
        if target:
            return res
        else:
            return {key:"" for key in keys}
    
    def reflexion_generate(self, res, instruction, html_content, ground_truth=None, reflection_times=3):
        histories = []
        for reflection_index in range(reflection_times):
            if ground_truth:
                history = {
                    'thought': res['thought'],
                    'xpath': res['xpath'],
                    'result': str(self.extract_with_xpath(html_content, res['xpath']))
                }
                if self.verbose:
                    print(f'Reflexion {reflection_index}:')
                    print(json.dumps(history, indent=4))
                    print()

                histories.append(history)
                query = self.prompter.reflection_wr_prompt.format(instruction, ground_truth, json.dumps(histories, indent=4), html_content)

                res = self.request_parse(query, ['thought', 'consistent', 'value', 'xpath'])
                if self.verbose:
                    print(json.dumps(res, indent=4))
                if res['consistent'].lower() == 'yes':
                    break
            else:
                history = {
                    'expected value': res['value'],
                    'thought': res['thought'],
                    'xpath': res['xpath'],
                    'result': str(self.extract_with_xpath(html_content, res['xpath']))
                }
                if self.verbose:
                    print(f'Reflexion {reflection_index}:')
                    print(json.dumps(history, indent=4))
                    print()

                histories.append(history)
                query = self.prompter.reflection_prompt.format(instruction, json.dumps(histories, indent=4), html_content)
                res = self.request_parse(query, ['thought', 'consistent', 'value', 'xpath'])

                if self.verbose:
                    print(json.dumps(res, indent=4))
                if res['consistent'].lower() == 'yes':
                    break
        if res['consistent'] == 'yes':
            return res['xpath']
        else:
            return ''

    def generate_rule_html(self, 
                      instruction: str, 
                      html_content: str, 
                      ground_truth = None,
                      repeat_times = 1,
                      with_reflection=True, 
                      reflection_times=3) -> str:
        """Generate rule by asking LLM with an instruction and HTML code.

        Args:
            instruction (str): Task description
            html (str): HTML code
            repeat_times: number of repeating times for extraction. Defaults to 3
            with_reflection (bool, optional): Whether generate rule with reflection. Defaults to True.
            reflection_times (int, optional): Number of cycles for reflection module to fix the rule. Defaults to 3.

        Returns:
            dict: the generated rule and the corresponding thought, if the rule is empty, return empty strings.
                Example:{
                    "thought": "",
                    "xpath": "",
                }
        """
        if self.is_simplify:
            html_content = simplify_html(html_content)

        if ground_truth:
            query = f"{self.prompter.role_prompt}\n{self.prompter.crawler_wr_prompt.format(instruction, ground_truth, html_content)}"

            rule_list = []
            for index in range(repeat_times):
                if self.verbose:
                    print('*'*100)
                    print(f'Trial {index + 1} for generating {self.rule_pattern}.')
                    print()

                # An full execution for generating a rule
                res = self.request_parse(query, ['thought', 'xpath'])

                if self.rule_pattern in ['reflexion']:
                    rule_list.append(self.reflexion_generate(res, instruction, html_content, ground_truth))
                else:
                    rule_list.append(res['xpath'])
        else:
            query = f"{self.prompter.role_prompt}\n{self.prompter.crawler_prompt.format(instruction, html_content)}"

            rule_list = []
            for index in range(repeat_times):
                if self.verbose:
                    print('*'*100)
                    print(f'Trial {index + 1} for generating {self.rule_pattern}.')
                    print()

                # An full execution for generating a rule
                #print(query)
                res = self.request_parse(query, ['thought', 'value', 'xpath'])
                if self.rule_pattern in ['reflexion']:
                    rule_list.append(self.reflexion_generate(res, instruction, html_content))
                else:
                    rule_list.append(res['xpath'])

        # Choose one of the best rule from different generation trail.
        if repeat_times > 1:
            ret_dict = {}
            for xpath in rule_list:
                ret_dict[xpath] = self.extract_with_xpath(html_content, xpath)
            query = self.prompter.comparison_prompt.format(instruction, json.dumps(ret_dict, ensure_ascii=False, indent=4))
            if self.verbose:
                print('-'*50)
                print(f'Choose one of the best {self.rule_pattern} for a single HTML:')
                #print(query)
            res = self.request_parse(query, ['thought', 'xpath'])
            rule = res['xpath']
        else:
            rule = rule_list[0]
        if self.verbose:
            print(f'Generated {self.rule_pattern} for the webpage')
            print(self.rule_pattern, ':', res)
        return rule

    def generate_rule(self, instruction, html_content, ground_truth = None, max_token=8000):
        if self.is_simplify:
            html_content = simplify_html(html_content)
        #print(html_content)
        soup = BeautifulSoup(html_content, 'html.parser')
        subtree_list = domlm_parse(soup, max_token)
        print('Page split:', len(subtree_list))
        rule_list = []
        for sub_html in subtree_list:
            page_rule = self.generate_rule_html(instruction, sub_html, ground_truth)
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
                sub_extract_result['extracted result'] = self.extract_with_xpath(html_content, rule)
                extract_result.append(sub_extract_result)
            print(json.dumps(extract_result, ensure_ascii=False, indent=4))
            query = self.prompter.synthesis_prompt.format(instruction, json.dumps(extract_result, indent=4))
            res = self.request_parse(query, ['thought', 'xpath'])
            return res['xpath']
        else:
            return rule_list[0]
    
    def rule_synthesis(self, 
                       website_name: str,
                       seed_html_set: list[str], 
                       instruction: str, 
                       ground_truth = None,
                       max_token = 8000,
                       per_page_repeat_time=1) -> str:
        rule_list = []

        # Collect a rule from each seed webpage
        if ground_truth:
            for html, gt in zip(seed_html_set, ground_truth):
                page_rule = self.generate_rule(instruction, html, gt, max_token=max_token)
                rule_list.append(page_rule)
        else:
            for html in seed_html_set:
                page_rule = self.generate_rule(instruction, html, max_token=max_token)
                rule_list.append(page_rule)

        #rule_list = list(set(rule_list))
        print(rule_list)
        if len(seed_html_set) > 1:
            # Parse the webpage with each rule
            extract_result = []
            for rule in rule_list:
                
                sub_extract_result = {'xpath': rule, 'extracted result': []}
                
                for html in seed_html_set:
                    sub_extract_result['extracted result'].append(self.extract_with_xpath(html, rule))
                extract_result.append(sub_extract_result)

            if self.verbose:
                print('+' * 100)
                print(f"Systhesis rule for the website {website_name}")
                print(json.dumps(extract_result, ensure_ascii=False, indent=4))

            # Sythesis the rule
            query = self.prompter.synthesis_prompt.format(instruction, json.dumps(extract_result, indent=4))
            res = self.request_parse(query, ['thought', 'xpath'])
            if self.verbose:
                print(f'Systhesis rule:')
                print(res)
            return res['xpath']
        else:
            return rule_list[0]

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
                #return [item.text for item in ele.xpath(xpath)]
                return [item.strip() if isinstance(item, str) else item.text.strip() for item in ele.xpath(xpath)]
            else:
                return []
        except:
            return []