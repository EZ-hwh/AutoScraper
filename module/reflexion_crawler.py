from .prompt import *
import json, re
from lxml import etree, html
from utils.html_utils import simplify_html, find_common_ancestor

class AutoCrawler:
    '''
    AutoCrawler is a LLM-based agent, which generate different kinds of rule, such as Xpath, CSS Selector, code for information extraction and web proning.
    '''
    def __init__(self, 
                 pattern='xpath', 
                 simplify=True, 
                 verbose=True,
                 api=None,
                 error_max_times=15):
        """Initial an instance of Autocrawler, including setting the pattern of rule 

        Args:
            pattern (str, optional): Which kind of rule pattern will be used. **Options: ['xpath', 'selector', 'code']**. Defaults to 'xpath'.
            simplify (bool, optional): Whether to simplify HTML before proprecessing. Defaults to True.
            verbose (bool, optional): Whether print the whole execution process. Defaults to True.
        """
        if api == None:
            raise ValueError("No api has been assigned!!")
        self.api = api
        if pattern not in ['reflexion', 'selector', 'code', 'cot']:
            raise AssertionError("Pattern must be one of the following selection: reflexion, selector, code, cot")
        self.rule_pattern = pattern
        self.is_simplify = simplify
        self.verbose = verbose
        if self.rule_pattern in ['reflexion', 'cot']:
            self.prompter = Xpath_prompter()
        elif self.rule_pattern == 'selector':
            self.prompter = Selector_prompter()
        else:
            self.prompter = Code_prompter()
        self.error_max_times = error_max_times

    def request_parse(self, 
                      query: str, 
                      html: str,
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
                if self.rule_pattern == 'reflexion':
                    history = {
                        'thought': res['thought'],
                        'xpath': res['xpath'],
                        'result': str(self.extract_with_xpath(html_content, res['xpath']))
                    }
                elif self.rule_pattern == 'selector':
                    history = {
                        'thought': res['thought'],
                        'selector': res['selector'],
                        'result': str(self.extract_with_selector(html_content, res['selector']))
                    }
                else:
                    history = {
                        'thought': res['thought'],
                        'code': res['code'],
                        'result': str(self.extract_with_code(html_content, res['code']))
                    }
                if self.verbose:
                    print(f'Reflexion {reflection_index}:')
                    print(json.dumps(history, indent=4))
                    print()

                histories.append(history)
                query = self.prompter.reflection_wr_prompt.format(instruction, ground_truth, json.dumps(histories, indent=4), html_content)

                if self.rule_pattern in ['selector', 'code']:
                    res = self.request_parse(query, html_content, ['thought', 'consistent', self.rule_pattern])
                else:
                    res = self.request_parse(query, html_content, ['thought', 'consistent', 'xpath'])
                if self.verbose:
                    print(json.dumps(res, indent=4))
                if res['consistent'].lower() == 'yes':
                    break
            else:
                if self.rule_pattern == 'reflexion':
                    history = {
                        'expected value': res['value'],
                        'thought': res['thought'],
                        'xpath': res['xpath'],
                        'result': str(self.extract_with_xpath(html_content, res['xpath']))
                    }
                elif self.rule_pattern == 'selector':
                    history = {
                        'expected value': res['value'],
                        'thought': res['thought'],
                        'selector': res['selector'],
                        'result': str(self.extract_with_selector(html_content, res['selector']))
                    }
                else:
                    history = {
                        'expected value': res['value'],
                        'thought': res['thought'],
                        'code': res['code'],
                        'result': str(self.extract_with_code(html_content, res['code']))
                    }
                if self.verbose:
                    print(f'Reflexion {reflection_index}:')
                    print(json.dumps(history, indent=4))
                    print()

                histories.append(history)
                query = self.prompter.reflection_prompt.format(instruction, json.dumps(histories, indent=4), html_content)

                if self.rule_pattern in ['selector', 'code']:
                    res = self.request_parse(query, html_content, ['thought', 'consistent', self.rule_pattern])
                else:
                    res = self.request_parse(query, html_content, ['thought', 'consistent', 'xpath'])

                if self.verbose:
                    print(json.dumps(res, indent=4))
                if res['consistent'].lower() == 'yes':
                    break
        if res['consistent'] == 'yes':
            if self.rule_pattern == 'reflexion':
                return res['xpath']
            elif self.rule_pattern == 'selector':
                return res['selector']
            else:
                return res['code']
        else:
            return ''

    def generate_rule(self, 
                      instruction: str, 
                      html_content: str, 
                      ground_truth = None,
                      repeat_times = 3,
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
                #print(query)
                if self.rule_pattern in ['selector', 'code']:
                    res = self.request_parse(query, html_content, ['thought', self.rule_pattern])
                elif self.rule_pattern in ['reflexion', 'cot']:
                    res = self.request_parse(query, html_content, ['thought', 'xpath'])

                if self.rule_pattern in ['reflexion', 'selector', 'code']:
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
                if self.rule_pattern in ['xpath', 'selector', 'code']:
                    res = self.request_parse(query, html_content, ['thought', 'value', self.rule_pattern])
                else:
                    res = self.request_parse(query, html_content, ['thought', 'value', 'xpath'])

                if self.rule_pattern in ['reflexion', 'selector', 'code']:
                    rule_list.append(self.reflexion_generate(res, instruction, html_content))
                else:
                    rule_list.append(res['xpath'])

        # Choose one of the best rule from different generation trail.
        if repeat_times > 1:
            ret_dict = {}
            for xpath in rule_list:
                if self.rule_pattern in ['reflexion', 'cot']:
                    ret_dict[xpath] = self.extract_with_xpath(html_content, xpath)
                elif self.rule_pattern == 'selector':
                    ret_dict[xpath] = self.extract_with_selector(html_content, xpath)
                elif self.rule_pattern == 'code':
                    ret_dict[xpath] = self.extract_with_code(html_content, xpath)
            query = self.prompter.comparison_prompt.format(instruction, json.dumps(ret_dict, ensure_ascii=False, indent=4))
            if self.verbose:
                print('-'*50)
                print(f'Choose one of the best {self.rule_pattern} for a single HTML:')
                #print(query)
            res = self.request_parse(query, html_content, ['thought', self.rule_pattern])
            if self.rule_pattern in ['reflexion', 'cot']:
                rule = res['xpath']
            elif self.rule_pattern == 'selector':
                rule = res['selector']
            else:
                rule = res['code']
        else:
            rule = rule_list[0]
        if self.verbose:
            print(f'Generated {self.rule_pattern} for the webpage')
            print(self.rule_pattern, ':', res)
        return rule
    
    def rule_synthesis(self, 
                       website_name: str,
                       seed_html_set: list[str], 
                       instruction: str, 
                       ground_truth = None,
                       per_page_repeat_time=1) -> str:
        rule_list = []

        # Collect a rule from each seed webpage
        if ground_truth:
            for html, gt in zip(seed_html_set, ground_truth):
                page_rule = self.generate_rule(instruction, html, gt, repeat_times=per_page_repeat_time)
                rule_list.append(page_rule)
        else:
            for html in seed_html_set:
                page_rule = self.generate_rule(instruction, html, repeat_times=per_page_repeat_time)
                rule_list.append(page_rule)

        #rule_list = list(set(rule_list))
        print(rule_list)
        if len(seed_html_set) > 1:
            # Parse the webpage with each rule
            extract_result = []
            for rule in rule_list:
                if self.rule_pattern in ['selector', 'code']:
                    sub_extract_result = {self.rule_pattern: rule, 'extracted result':[]}
                elif self.rule_pattern in ['reflexion', 'cot']:
                    sub_extract_result = {'xpath': rule, 'extracted result': []}
                else:
                    if not rule or rule[0] == False:
                        continue
                    sub_extract_result = {'rule':rule[1], 'extracted result':[]}
                for html in seed_html_set:
                    if self.rule_pattern in ['reflexion', 'cot']:
                        sub_extract_result['extracted result'].append(self.extract_with_xpath(html, rule))
                    elif self.rule_pattern == 'selector':
                        sub_extract_result['extracted result'].append(self.extract_with_selector(html, rule))
                    elif self.rule_pattern == 'code':
                        sub_extract_result['extracted result'].append(self.extract_with_code(html, rule))
                extract_result.append(sub_extract_result)

            if self.verbose:
                print('+' * 100)
                print(f"Systhesis rule for the website {website_name}")
                print(json.dumps(extract_result, ensure_ascii=False, indent=4))

            # Sythesis the rule
            if self.rule_pattern in ['selector', 'code']:
                query = self.prompter.synthesis_prompt.format(instruction, json.dumps(extract_result, indent=4))
                res = self.request_parse(query, seed_html_set[0], ['thought', self.rule_pattern])
            elif self.rule_pattern in ['reflexion', 'cot']:
                query = self.prompter.synthesis_prompt.format(instruction, json.dumps(extract_result, indent=4))
                res = self.request_parse(query, seed_html_set[0], ['thought', 'xpath'])
            if self.verbose:
                print(f'Systhesis rule:')
                print(res)

            if self.rule_pattern in ['reflexion', 'cot']:
                return res['xpath']
            elif self.rule_pattern == 'selector':
                return res['selector']
            elif self.rule_pattern == 'code':
                return res['code']
            else:
                return rule_list[eval(res['number'])]
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
                return [item if isinstance(item, str) else item.text for item in ele.xpath(xpath)]
            else:
                return []
        except:
            return []
        
    def extract_with_seq(self,
                         html_content:str,
                         xpath_seq:str) -> list[str]:
        if self.is_simplify:
            html_content = simplify_html(html_content)
        if xpath_seq == []:
            return []
        else:
            for xpath, action in xpath_seq:
                ele = etree.HTML(html_content)
                if action == 'Accept':
                    return [item if isinstance(item, str) else item.text for item in ele.xpath(xpath)]
                elif action == 'Re-thinking':
                    html_content = find_common_ancestor(html_content, xpath)
                elif action == 'Re-generate':
                    pass

    def extract_with_selector(self, 
                              html_content: str,
                              selector:str) -> list[str]:
        """CSS Selector parser

        Args:
            html_content (str): text of HTML
            selector (str): the string of CSS selector

        Returns:
            list[str]: result list extracted by css selector
        """
        if self.is_simplify:
            html_content = simplify_html(html_content)
        if selector.strip():
            tree = html.fromstring(html_content)
            #return [item.text for item in ele.xpath(xpath)]
            #print([item if isinstance(item, str) else item.text for item in tree.cssselect(selector)])
            return [item if isinstance(item, str) else item.text for item in tree.cssselect(selector)]
        else:
            return []

    def extract_with_code(self,
                          html_content: str,
                          code: str) -> list[str]:
        """Code parser

        Args:
            html_content (str): _description_
            code (str): _description_

        Returns:
            list[str]: _description_
        """

        if self.is_simplify:
            html_content = simplify_html(html_content)

        if code.strip():
            #print(code)
            exec(code, globals())
            extracted_value = extract_value(html_content)
            return extracted_value
        else:
            return []