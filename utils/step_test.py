import os,sys,json
import requests
from bs4 import BeautifulSoup,NavigableString,Tag,Comment
from tqdm import tqdm
import multiprocessing
from collections import Counter, defaultdict

#add_attr = False

def pre_tokenize(s):
    return s

add_attr = ['href'] 
class_list = {}
import os,argparse,collections,re,json

html_tag = []

class Dom_TreeNode:
    def __init__(self, index, findex):
        self.str = ''
        self.children = []
        self.index = index
        self.father = findex
        self.tokens = []
        self.attr = {}
        self.text = ''
    
    def get_children(self): return self.children
    def get_index(self): return self.index
    def get_str(self): return self.str
    def get_father(self): return self.father
    def append_children(self, index): self.children.append(index)
    def get_tokens(self): return self.tokens
    def set_str(self, strx): self.str = strx
    def set_text(self, text): self.text = text
    def get_text(self): return self.text
    def set_tokens(self, tokens): self.tokens = tokens
    def set_tag(self, tag): self.tag = tag
    def get_tag(self): return self.tag
    def set_attr(self, attrs): self.attr = attrs 
    def get_attr(self): return self.attr

def node_counter(node):
    c = Counter([i.name for i in node.contents if isinstance(i, Tag)])
    return c

def build_dom_tree(node, tot_node, father_index, node_list, attrs):
    node_index = tot_node
    new_node = Dom_TreeNode(tot_node, father_index)
    tot_node = tot_node + 1
    node_str = ''
    if set(node.attrs.keys()) & set(attrs):
        new_node.set_attr({x:y for x,y in node.attrs.items() if x in attrs})

    for child in node.contents:
        if isinstance(child, NavigableString):
            if len(child.strip()) > 0:
                text_node = Dom_TreeNode(tot_node, node_index)
                tot_node = tot_node + 1
                text_node.set_tag('text')
                text_node.set_str(child.strip())
                node_list.append(text_node)
                new_node.append_children(tot_node - 1)

        elif isinstance(child, Tag) and child.name not in ['script', 'style']:
            child_index, tot_node = build_dom_tree(child, tot_node, node_index, node_list, attrs)
            if child_index == -1:
                continue
            new_node.append_children(child_index)

    new_node.set_tag(node.name)

    new_node.set_str(node_str)
    node_list.append(new_node)
    return new_node.get_index(), tot_node

def build_tree(html, attrs=[]):
    tot_node = 0
    node_list = []
    html = html.replace('&nbsp;',' ')
    html = html.replace('&lt;', '<')
    html = html.replace('&gt;', '>')
    soup = BeautifulSoup(html, 'html.parser')
    for element in soup(text=lambda text: isinstance(text, Comment)):
        element.extract()
    [s.extract() for s in soup('script')]
    [s.extract() for s in soup('style')]
    [s.extract() for s in soup('textarea')]
    build_dom_tree(soup.html, tot_node, -1, node_list, attrs=attrs)
    node_list = sorted(node_list, key=lambda x:x.get_index())
    return node_list

def get_max_index(parse_tree, index): # get the max index of the subtree (must tag node not text node)
    if len(parse_tree[index].get_children()) == 0:
        return index
    else:
        return get_max_index(parse_tree, parse_tree[index].get_children()[-1])

def web2tree(html_content, attrs=[]):
    parse_tree = build_tree(html_content, attrs=attrs)
    return parse_tree

def attrs_dict2str(attrs):
    attrs_str = ''
    for key in attrs.keys():
        attrs_str += f' {key}="{attrs[key]}"'
    return attrs_str

def tree2text(node_list, index, simplify=True, add_tags = True):
    text = ''
    text_len = 0
    node = node_list[index]
    is_leaf = True # if the node is a leaf node
    # valid_child = 0
    #print(len(node_list))
    for child_idx in node.get_children():
        #print(child_idx)
        if node_list[child_idx].get_tag() != 'text':
            is_leaf = False
        child_seq, child_text_len = tree2text(node_list, child_idx, simplify, add_tags)
        # if child_text_len > 0:
        #     valid_child += 1
        text = text + ' ' + child_seq.strip() + ' '
        text_len += child_text_len

    text_len += len(node.get_str())

    # if (not add_tags) or (node.get_tag() == 'text') or (simplify and text_len == 0) or (simplify and valid_child <= 1 and not is_leaf):
    #     text = text + f" {node.get_str()} "
    # else:
    if node.get_tag() == 'text':
        text = text + f" {node.get_str()} "
    else:
        text = f"<{node.get_tag() + attrs_dict2str(node.get_attr())}> " + text + f" {node.get_str()} </{node.get_tag()}>"
    
    node_list[index].set_text(text)
    node_list[index].set_tokens(list(text))
    return text, text_len

def web2text(html_content, simplify=True, prettify = True, add_tags = True, attrs=[]):
    parse_tree = web2tree(html_content, attrs=attrs)
    text, text_len = tree2text(parse_tree, 0, simplify=simplify, add_tags=add_tags)
    if prettify:
        soup = BeautifulSoup(text, 'html.parser')
        text = soup.prettify()
    return text

def fit_tree(parse_tree, index, curr_len, valid_index, max_len=1024):
    node = parse_tree[index]
    is_leaf = len(node.get_children()) == 1
    curr_text = ''
    #print(index)
    if curr_len + len(node.get_tokens()) <= max_len and valid_index < index:
        curr_text = curr_text + node.get_text()
        curr_len += len(node.get_tokens())
        return curr_text, curr_len, get_max_index(parse_tree, index)
    elif not is_leaf:
        #print(node.get_children())
        curr_len += len(node.get_tokens()) - sum([len(parse_tree[child].get_tokens()) for child in node.get_children()])
        #print(curr_len)
        for index, child in enumerate(node.get_children()):
            if (index == 0 and len(parse_tree[child].get_children()) <= 1):
                curr_text = curr_text + parse_tree[child].get_text()
                curr_len += len(parse_tree[child].get_tokens())
                valid_index = max(valid_index, get_max_index(parse_tree, child))
                continue

            if valid_index >= get_max_index(parse_tree, child):
                continue
            if parse_tree[child].get_tag() == 'text':
                if curr_len + len(parse_tree[child].get_tokens()) <= max_len:
                    curr_text = curr_text + parse_tree[child].get_text()
                    curr_len += len(node.get_tokens())
                    valid_index = parse_tree[child].get_index()
                else:
                    curr_text = curr_text + node.get_text()
                    return curr_text, curr_len, valid_index
                    #return curr_text, curr_len, get_max_index(parse_tree, index)
            else:
                child_curr_text, curr_len, valid_index = fit_tree(parse_tree, child, curr_len, valid_index, max_len)
                #print(curr_text)
                if valid_index < get_max_index(parse_tree, child):
                    curr_text = f' <{node.get_tag()}> ' + curr_text + child_curr_text + f' </{node.get_tag()}>'
                    return curr_text, curr_len, valid_index
                else:
                    curr_text = curr_text + child_curr_text
                    #curr_text = curr_text + f' <{node.get_tag()}> ' + child_curr_text + f' </{node.get_tag()}>'
        curr_text = f' <{node.get_tag()}> ' + curr_text + f' </{node.get_tag()}>'
        return curr_text, curr_len, valid_index
    # if leaf: abondon all the subtree
    return curr_text, curr_len, valid_index

def domlm_parser(parse_tree, max_len=1024):
    curr_text, curr_len, valid_index = 0, 0, -1
    while valid_index < len(parse_tree) - 1:
        curr_text, curr_len, valid_index = fit_tree(parse_tree, 0, 0, valid_index, max_len)
        yield curr_text
    return 

def domlm_dataset(html_content, max_len=1024, simplify=True, prettify = True, add_tags = True, attrs=[]):
    parse_tree = build_tree(html_content, attrs=attrs)
    tree2text(parse_tree, 0)
    answer = [] 
    for text in domlm_parser(parse_tree, max_len):
        answer.append(text)
    return answer

if __name__ == '__main__':
    from html_utils import simplify_html
    html_content = """<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Document</title>
    </head>
    <body>
        <header>
            <h1>Welcome to My Website</h1>
            <nav>
                <ul>
                    <li><a href="#home">Home</a></li>
                    <li><a href="#about">About</a></li>
                    <li><a href="#services">Services</a></li>
                    <li><a href="#contact">Contact</a></li>
                </ul>
            </nav>
        </header>
        <main>
            
        </main>
        <footer>
            <p>Copyright © 2023. All Rights Reserved.</p>
        </footer>
    </body>
    </html>
    """
    html_content = simplify_html(html_content)
    parse_tree = build_tree(html_content)
    for index, item in enumerate(build_tree(html_content)):
        text, _ = tree2text(parse_tree, index)
        print('-'*50)
        print(parse_tree[index].get_text())
    print(domlm_dataset(html_content=html_content, max_len=100))