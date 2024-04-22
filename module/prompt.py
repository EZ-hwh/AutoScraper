
class Base_prompter:
    """Basic class for different prompter

    Returns:
        _type_: _description_
    """
    def __init__(self) -> None:
        self.role_prompt = "Suppose you're a web parser that is good at reading and understanding the HTML code and can give clear executable code on the brower."

class Xpath_prompter(Base_prompter):
    """_summary_
    """
    def __init__(self) -> None:
        super().__init__()
        # 用于第一次生成xpath
        self.crawler_prompt = '''Please read the following HTML code, and then return an Xpath that can recognize the element in the HTML matching the instruction below. 

Instruction: {0}

Here're some hints:
1. Do not output the xpath with exact value or element appears in the HTML.
2. Do not output the xpath that indicate multi node with different value. It would be appreciate to use more @class to identify different node that may share the same xpath expression.
3. If the HTML code doesn't contain the suitable information match the instruction, keep the xpath attrs blank.
4. Avoid using some string function such as 'substring()' and 'normalize-space()' to normalize the text in the node.
Please output in the following Json format:

{{
    "thought": "", # a brief thought of how to confirm the value and generate the xpath
    "value": "", # the value extracted from the HTML that match the instruction
    "xpath": "", # the xpath to extract the value
}}
Here's the HTML code:
```
{1}
```
'''

        self.crawler_wr_prompt = '''Please read the following HTML code, and then return an Xpath that can recognize the element in the HTML matching the instruction below. 

Instruction: {0}
The element value: {1}

Here're some hints:
1. Do not output the xpath with exact value or element appears in the HTML.
2. Do not output the xpath that indicate multi node with different value. It would be appreciate to use more @class to identify different node that may share the same xpath expression.
3. If the HTML code doesn't contain the suitable information match the instruction, keep the xpath attrs blank.
4. Avoid using some string function such as 'substring()' and 'normalize-space()' to normalize the text in the node.
Please output in the following Json format:

{{
    "thought": "", # a brief thought of how to generate the xpath
    "xpath": "", # the xpath to extract the value
}}
Here's the HTML code:
```
{2}
```
'''
        # 针对Xpath和单网页修改并生成对应正确的Xpath
        self.reflection_prompt = '''Here's the HTML extraction task:
Task description: Please read the following HTML code, and then return an Xpath that can recognize the element in the HTML matching the instruction below.
Instruction: {0}

We will offer some history about the thought and the extraction result. Please reflect on the history trajectory and adjust the xpath rule for better and more exact extraction. Here's some hints:
1. Judge whether the results in the history is consistent with the expected value. Please pay attention for the following case:
    1) Whether the extraction result contains some elements that is irrelevent
    2) Whether the crawler return a empty result
    3) The raw values containing redundant separators is considered as consistent because we will postprocess it.
2. Re-thinking the expected value and how to find it depend on xpath code
3. Generate a new or keep the origin xpath depend on the judgement and thinking following the hints:
    1. Do not output the xpath with exact value or element appears in the HTML.
    2. Do not output the xpath that indicate multi node with different value. It would be appreciate to use more @class and [num] to identify different node that may share the same xpath expression.
    3. If the HTML code doesn't contain the suitable information match the instruction, keep the xpath attrs blank.
    4. Avoid using some string function such as 'substring()' and 'normalize-space()' to normalize the text in the node.

Please output in the following json format:
{{
    "thought": "", # thought of why the xpaths in history are not work and how to adjust the xpath
    "consistent": "", # whether the extracted result is consistent with the expected value, return yes/no directly
    "value": "", # the value extracted from the HTML that match the task description
    "xpath": "", # a new xpath that is different from the xpath in the following history if not consistent
}}

And here's the history about the thought, xpath and result extracted by crawler.
{1}

Here's the HTML code:
```
{2}
```
'''

        self.reflection_wr_prompt = '''Here's the HTML extraction task:
Task description: Please read the following HTML code, and then return an Xpath that can recognize the element in the HTML matching the instruction below.
Instruction: {0}
The expected value: {1}

We will offer some history about the thought and the extraction result. Please reflect on the history trajectory and adjust the xpath rule for better and more exact extraction. Here's some hints:
1. Judge whether the results in the history is consistent with the expected value. Please pay attention for the following case:
    1) Whether the extraction result contains some elements that is irrelevent
    2) Whether the crawler return a empty result
    3) The raw values containing redundant separators is considered as consistent because we will postprocess it.
2. Re-thinking the expected value and how to find it depend on xpath code
3. Generate a new or keep the origin xpath depend on the judgement and thinking following the hints:
    1. Do not output the xpath with exact value or element appears in the HTML.
    2. Do not output the xpath that indicate multi node with different value. It would be appreciate to use more @class and [num] to identify different node that may share the same xpath expression.
    3. If the HTML code doesn't contain the suitable information match the instruction, keep the xpath attrs blank.
    4. Avoid using some string function such as 'substring()' and 'normalize-space()' to normalize the text in the node.

Please output in the following json format:
{{
    "thought": "", # thought of why the xpaths in history are not work and how to adjust the xpath
    "consistent": "", # whether the extracted result is consistent with the expected value, return yes/no directly
    "xpath": "", # a new xpath that is different from the xpath in the following history if not consistent
}}

And here's the history about the thought, xpath and result extracted by crawler.
{2}

Here's the HTML code:
```
{3}
```
'''
        self.crawl_w_history = '''Here's the HTML extraction task:
Task description: Please read the following HTML code, and then return an absolute Xpath that can recognize the element in the HTML matching the instruction below.
Instruction: {0}

We will offer some history about the thought and the extraction result. Please reflect on the history trajectory and adjust the xpath rule for better and more exact extraction. Here's some hints:
1. Re-thinking the expected value and how to find it depend on xpath code
2. Generate a new xpath to avoid the mistakes in history and thinking following the hints:
    1. Do not output the xpath with exact value or element appears in the HTML.
    2. Do not output the xpath that indicate multi node with different value. It would be appreciate to use xpath with @class and [num] to identify different node that may share the same xpath expression.
    3. If the HTML code doesn't contain the suitable information match the instruction, keep the xpath attrs blank.
    4. Avoid using some string function such as 'substring()' and 'normalize-space()' to normalize the text in the node.

Please output in the following json format:
{{
    "thought": "", # thought of why the xpaths in history are not work and how to adjust the xpath
    "value": "", # the value extracted from the HTML that match the task description
    "xpath": "", # a new xpath that is different from the xpath in the following history if not consistent
}}

And here's the history about the thought, xpath and result extracted by crawler.
{1}

Here's the HTML code:
```
{2}
```
'''
        self.simple_reflection_prompt = '''Here's the HTML extraction task:
Task description: Please read the following HTML code, and then return an absolute Xpath that can recognize the element in the HTML matching the instruction below.
Instruction: {0}

Here's some hints:
1. The result is the list of the elements that extracted with the xpath.
2. Judge whether the result contains irrelevant value. Please pay attention for the following case:
    1) Whether the extraction result contains some elements that is irrelevent, which means that the relevant is only considered in the element level, but not string level;
    2) Whether the crawler return a empty result;
    3) The raw values containing redundant separators is considered as consistent because we will postprocess it.

We will offer some history about the thought and the extraction result. Please choose an action below base on the history trajectory and the extraction condition.
1. 'Accept': If the extraction result is consistent with the expected value, meaning that the xpath works;
2. 'Re-generate': If the extraction result is none, which might meaning that the xpath fail to find the node, so it need to be re-generated;
3. 'Re-thinking': If the extraction result contains irrelevant values, meaning that the xpath is not perfect that might inadvertently include irrelevant values.
4. 'Backtracing': If the extraction result miss some value in the expected value, meaning the xpath is not perfect that might proning valuable part of the HTML.

Please output in the following json format:
{{
    "thought": "", # thought of why the xpaths in history are not work and how to adjust the xpath
    "action": "" # The action you choose, including: Accept, Re-generate, Re-thinking, Backtracing
}}

And here's the xpath and result extracted by crawler.
{1}
'''
        # 用于将在单个网页中生成的多个不同Xpath进行选择和合并
        self.synthesis_prompt = '''You're a perfect discriminator which is good at HTML understanding as well. Following the instruction, there are some Xpath written from several HTML and the corresponding result extracted from several HTML. Please choose one that can be best potentially adapted to the same extraction task on other webpage in the same websites. Here are the instruction of the task:
Instructions: {0}
The xpaths and the corresponding extracted results with different xpath on different webpage are as follow:
{1}

Please output the best xpath in the following Json format:
{{
    "thought": "" # brief thinking about which to choose
    "xpath": "" # the best xpath choosen from the candidates.
}}
'''
        self.seq_synthesis_prompt = '''You're a perfect discriminator which is good at HTML understanding as well. Following the instruction, there are some action sequence written from several HTML and the corresponding result extracted from several HTML. Please choose one that can be best potentially adapted to the same extraction task on other webpage in the same websites. Here are the instruction of the task:
Instructions: {0}
The action sequences and the corresponding extracted results with different sequence on different webpage are as follow:
{1}

Please output the best action sequence in the following Json format:
{{
    "thought": "" # brief thinking about which to choose
    "number": "" # the best action sequence choosen from the candidates, starts from 0.
}}
'''

class Selector_prompter(Base_prompter):
    def __init__(self) -> None:
        super().__init__()
        # 用于第一次生成CSS selector
        self.crawler_prompt = '''Please read the following HTML code, and then return an CSS selector that can recognize the element in the HTML matching the instruction below.

Instruction: {0}
Please output in the following Json format:

{{
    "thought": "", # a brief thought of how to confirm the value and generate the css selector
    "value": "", # the value extracted from the HTML that match the instruction
    "selector": "", # the css selector to extract the value
}}
Here's the HTML code:
```
{1}
```
'''
        self.reflection_prompt = '''Here's the HTML extraction task:
Task description: Please read the following HTML code, and then return an CSS selector that can recognize the element in the HTML matching the instruction below.
Instruction: {0}
We will offer some history about the thought and the extraction result. Please reflect on the history trajectory and adjust the css selector rule for better and more exact extraction. Here's some hints:
1. Judge whether the extracted value in the history is consistent with the expected value. Please pay attention for the following case:
    1) Whether the extraction result contains some elements that is irrelevent
    2) Whether the crawler return a empty result
    3) The raw values containing redundant separators is considered as consistent because we will postprocess it
2. Re-thinking the expected value and how to find it depend on css selector code
3. Generate a new or keep the origin selector depend on the judgement and thinking following the hints:
    1. Do not output the selector with exact value or element appears in the HTML.
    2. Do not output the selector that indicate multi node with different value.
    3. If the HTML code doesn't contain the suitable information match the instruction, keep the css selector attrs blank.

Please output in the following json format:
{{
    "thought": "", # thought of why the css selectors in history are not work and how to adjust the css selector code
    "consistent": "", # whether the extracted value is consistent with the expected value, return yes/no directly
    "value": "", # the value extracted from the HTML that match the task description
    "selector": "", # if the extracted value is consistent, fill in with the selector in the history, otherwise fill in a selector that is different from the ones in the following history
}}

And here's the history about the thought, css selector and result extracted by crawler.
{1}


Here's the HTML code:
```
{2}
```
'''

        # 用于将在单个网页中生成的多个不同Selector进行选择和合并
        self.comparison_prompt = '''You're a perfect discriminator which is good at HTML understanding as well. Following the instruction, there are some CSS Selector written from an HTML and the corresponding result extracted from the HTML. Please choose one that can be best potentially adapted to the same extraction task on other webpage in the same websites. Here are the instruction of the task:
Instructions: {0}
The selectors and the corresponding extracted results are as follow:
{1}

Please output the best selector in the following Json format:
{{
    "thought": "" # brief thinking about which to choose
    "selector": "" # the best css selector choosen from the candidates.
}}
'''
        # Rule Synthesis
        self.synthesis_prompt = '''You're a perfect discriminator which is good at HTML understanding as well. Following the instruction, there are some CSS selector written from several HTML and the corresponding result extracted from several HTML. Please choose one that can be best potentially adapted to the same extraction task on other webpage in the same websites. Here are the instruction of the task:
Instructions: {0}
The selectors and the corresponding extracted results with different selectors on different webpage are as follow:
{1}

Please output the best selector in the following Json format:
{{
    "thought": "" # brief thinking about which to choose
    "selector": "" # the best selector choosen from the candidates.
}}
'''

class Code_prompter(Base_prompter):
    def __init__(self) -> None:
        super().__init__()
        # 用于第一次生成Code
        self.crawler_prompt = '''Please read the following HTML code, and then return an python code that can recognize the element in the HTML matching the instruction below.

Instruction: {0}
Here're some hints:
1. The code you provide only consist of the following components
    1) Import the package you need to use
    2) Define the extraction code as a function called 'extract_value', with one parameters 'HTML', so that we can input html with the parameters. The output of the function is the extraction result.
    3) Don't generate other parts of the code

Please write the code with the following Json format. At the same time, it is necessary to ensure that the output can be parsed by json.load()
{{
    "thought": "", # a brief thought of how to confirm the value and generate the css selector
    "value": "", # the value extracted from the HTML that match the instruction
    "code": "", # the python code to extract the value
}}

Here's the HTML code:
```
{1}
```
'''
        self.reflection_prompt = '''Here's the HTML extraction task:
Task description: Please read the following HTML code, and then return an python code that can recognize the element in the HTML matching the instruction below.
Instruction: {0}
We will offer some history about the thought and the extraction result. Please reflect on the history trajectory and adjust the python code for better and more exact extraction. Here's some hints:
1. Judge whether the extracted value in the history is consistent with the expected value. Please pay attention for the following case:
    1) Whether the extraction result contains some elements that is irrelevent
    2) Whether the crawler return a empty result
2. Re-thinking the expected value and how to find it depend on python code
3. Generate a new or keep the origin code depend on the judgement in step 1 and thinking following the hints:
    1. Do not output the code that extract the element with exact value or element appears in the HTML.
    2. Do not output the code that indicate multi node with different value.
    3. If the HTML code doesn't contain the suitable information match the instruction, keep the code attrs blank.

Please output in the following json format:
{{
    "thought": "", # thought of why the codes in history do not work and how to adjust the python code
    "consistent": "", # whether the extracted value is consistent with the expected value, return yes/no directly
    "value": "", # the value extracted from the HTML that match the task description
    "code": "", # if the extracted value is consistent, fill in with the python code in the history, otherwise fill in a python code that is different from the ones in the following history
}}

And here's the history about the thought, code and result extracted by crawler.
{1}


Here's the HTML code:
```
{2}
```
'''
        # 用于将在单个网页中生成的多个不同Python code进行选择和合并
        self.comparison_prompt = '''You're a perfect discriminator which is good at HTML understanding as well. Following the instruction, there are some code written from an HTML and the corresponding result extracted from the HTML. Please choose one that can be best potentially adapted to the same extraction task on other webpage in the same websites. Here are the instruction of the task:
Instructions: {0}
The codes and the corresponding extracted results are as follow:
{1}

Please output the best code in the following Json format:
{{
    "thought": "" # brief thinking about which to choose
    "code": "" # the best code choosen from the candidates.
}}
'''
        self.synthesis_prompt = '''You're a perfect discriminator which is good at HTML understanding as well. Following the instruction, there are some python code written from several HTML and the corresponding result extracted from several HTML. Please choose one that can be best potentially adapted to the same extraction task on other webpage in the same websites. Here are the instruction of the task:
Instructions: {0}
The code and the corresponding extracted results with different codes on different webpage are as follow:
{1}

Please output the best code in the following Json format:
{{
    "thought": "" # brief thinking about which to choose
    "code": "" # the best code choosen from the candidates.
}}
'''

class DownTop_prompter(Base_prompter):
    """_summary_

    Args:
        Base_prompter (_type_): _description_
    """
    def __init__(self) -> None:
        super().__init__()
        self.position_prompt = """Please read the following HTML code, and then return result that appear in the HTML matching the instruction below. 
Instructions: {0}
Here's the HTML code:
{{
    "thought": "", # a brief thought of how to confirm the value
    "value": "", # the value extracted from the HTML that match the instruction
}}
Please output in the following Json format:
```
{1}
```
"""