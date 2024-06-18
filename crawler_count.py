import glob
import json, os, sys
from tqdm import tqdm
from utils.html_utils import *
from module.stepback_crawler import StepbackCrawler
from module.reflexion_crawler import AutoCrawler

import argparse

parser = argparse.ArgumentParser()

parser.add_argument('--pattern', type=str, choices=['cot', 'reflexion', 'autocrawler'], help='Which type of crawler generation agent to use.')
parser.add_argument('--model', type=str, help='Backbone model')
parser.add_argument('--dataset', type=str, choices=['swde','ds1','extended_swde', 'klarna'], help='Which dataset to test.')
parser.add_argument('--seed_website', type=int)
parser.add_argument('--save_name', type=str)
parser.add_argument('--overwrite', type=bool, help='Whether overwrite the generated crawler.')
parser.add_argument('--max_token', type=int)

args = parser.parse_args()
print(args)

PATTERN = args.pattern
model = args.model
dataset = args.dataset
num_seed_website = args.seed_website
overwrite = args.overwrite
if args.max_token:
    max_token = args.max_token
else:
    max_token = 8000

print('max_token', max_token)

if model == 'GPT4':
    from utils.ms_api_copy import ms_gpt4 as chatgpt
elif model == 'ChatGPT':
    from utils.ms_api_copy import ms_chatgpt as chatgpt
elif model == 'Claude':
    from utils.claude3_api import claude_api as chatgpt
elif model == 'deepseek':
    from utils.custom_api import deepseek_33b_api as chatgpt
elif model == 'phi':
    from utils.custom_api import phi3_api as chatgpt
elif model == 'mixtral':
    from utils.custom_api import mixtral_87_api as chatgpt

if PATTERN == 'autocrawler':
    xe = StepbackCrawler(api=chatgpt)
else:
    xe = AutoCrawler(PATTERN, api=chatgpt)

if dataset == 'swde':
    from run_swde.task_prompt import swde_prompt as prompt
    SCHEMA = {
        'auto': ['model', 'price', 'engine', 'fuel_economy'],
        'book': ['title', 'author', 'isbn_13', 'publisher', 'publication_date'],
        'camera': ['model', 'price', 'manufacturer'],
        'job': ['title', 'company', 'location', 'date_posted'],
        'movie': ['title', 'director', 'genre', 'mpaa_rating'],
        'nbaplayer': ['name', 'team', 'height', 'weight'],
        'restaurant': ['name', 'address', 'phone', 'cuisine'],
        'university': ['name', 'phone', 'website', 'type']
    }
    DATA_HOME = '/mnt/data122/harryhuang/swde/sourceCode'

    if model == 'ChatGPT':
        filter_website = []
    else:
        filter_website = ['book-amazon']
    GROUND_TRUTH_HOME = '/mnt/data122/harryhuang/swde/sourceCode/groundtruth'

elif dataset == 'ds1':
    from run_ds1.task_prompt import ds1_prompt as prompt
    SCHEMA = {
        'book': ['title', 'author', 'price'],
        'e-commerce': ['title', 'price'],
        'hotel': ['title', 'price', 'address'],
        'movie': ['title', 'genre', 'actor']
    }
    DATA_HOME = '/mnt/data122/datasets/Web/FX-dataset/trainingset'
    if num_seed_website > 1:
        print('DS1 only have one seed websites in dataset.')
        num_seed_website = 1
    if model == 'ChatGPT':
        filter_website = ['shoppings_bestbuy', 'shoppings_pcworld', 'shoppings_uttings', 'shoppings_amazoncouk', 'shoppings_tesco', 'kayak', 'ratestogo', 'expedia', 'hotels', 'venere', 'rottentomatoes', 'metacritic', 'imdb']
    else:
        filter_website = []
elif dataset == 'extended_swde':
    from run_swde_et.schema import SCHEMA
    from run_swde_et.task_prompt import ex_swde_prompt as prompt
    DATA_HOME = '/mnt/data122/harryhuang/swde/sourceCode'
    if model == 'ChatGPT':
        filter_website = ['book-amazon', 'camera-onsale', 'camera-jr', 'camera-compsource', 'camera-buy', 'movie-metacritic', 'movie-rottentomatoes', 'nbaplayer-wiki', 'university-collegenavigator', 'university-matchcollege']
    else:
        filter_website = []
elif dataset == 'klarna':
    from run_klarna.task_prompt import klarna_prompt as prompt
    SCHEMA = {
        'product': ['name', 'price'],
    }
    filter_website = []
    DATA_HOME = '/mnt/data122/harryhuang/klarna_product_page_dataset_WTL_50k/train/US'

if args.save_name:
    OUTPUT_HOME = f'dataset/{dataset}/{args.save_name}'
else:
    OUTPUT_HOME = f'dataset/{dataset}/{model}'

def load_file(filename):
    result_dict = {}
    with open(filename, 'r') as f:
        for index, line in enumerate(f.readlines()):
            if index <= 1: 
                continue
            item_list = line.strip().split('\t')
            #print(item_list)
            result_dict[item_list[0]] = item_list[2 : 2+int(item_list[1])]
    return result_dict

for field in SCHEMA.keys():
    if not os.path.exists(os.path.join(OUTPUT_HOME, PATTERN, field)):
        os.makedirs(os.path.join(OUTPUT_HOME, PATTERN, field))

    if dataset == 'swde':
        weblist = glob.glob(os.path.join(DATA_HOME, field, '*'))
    elif dataset == 'ds1':
        fake_item = SCHEMA[field][0]
        weblist = glob.glob(os.path.join(DATA_HOME, field, fake_item, '*'))
    elif dataset == 'extended_swde':
        field0, field1 = field.split('-')
        #print(os.path.join(DATA_HOME, field0, field1))
        weblist = glob.glob(os.path.join(DATA_HOME, field0, field))
        weblist = [os.path.join(DATA_HOME, field0, field)]
    elif dataset == 'klarna':
        weblist = glob.glob(os.path.join(DATA_HOME, '*'))

    #print(weblist)
    for website_path in weblist:
        if dataset in ['extended_swde', 'swde']:
            website_name = website_path.split('/')[-1].split('(')[0]
        elif dataset == 'ds1':
            website_name = website_path.split('/')[-1].replace(f'{field}_','').replace(f'_{fake_item}.html','')
        elif dataset == 'klarna':
            website_name = website_path.split('/')[-1]
        
        print('-'*200)
        print(website_name)
        print(os.path.join(OUTPUT_HOME, PATTERN, field, website_name) + f'_{PATTERN}.json')
        if (website_name in filter_website) or (not overwrite and os.path.exists(os.path.join(OUTPUT_HOME, PATTERN, field, website_name) + f'_{PATTERN}.json')):
            continue

        if dataset in ['swde', 'extended_swde', 'ds1']:
            webpage_list = glob.glob(os.path.join(website_path, '*'))
        elif dataset == 'klarna':
            webpage_list = glob.glob(os.path.join(website_path, '*', 'source.html'))
        xpath_rule = {}
        html_list = []
        html_index = []
        if dataset in ['swde', 'extended_swde']:
            sorted(webpage_list)
            long_website = False
            for html_page in webpage_list[:num_seed_website]:
                with open(html_page, 'r') as f:
                    # For skipping
                    html = f.read()
                    # if num_tokens_from_string(simplify_html(html), "cl100k_base") < 10000:
                    #     long_website = True
                    #     break
                    html_list.append(html)
                    html_index.append(html_page.split('/')[-1].replace('.htm',''))
            if long_website:
                print('SKIP')
                continue
        elif dataset == 'ds1':
            with open(website_path, 'r', errors='ignore') as f:
                html_list.append(f.read())
        elif dataset == 'klarna':
            sorted(webpage_list)
            if len(webpage_list) <= num_seed_website:
                print(f'Website {website_name} contains less or equal than {num_seed_website} pages.')
                continue
            long_website = False
            for html_page in webpage_list[:num_seed_website]:
                with open(html_page, 'r') as f:
                    html = f.read()
                    html_list.append(html)
                    if model == 'ChatGPT':
                        if num_tokens_from_string(simplify_html(html), "cl100k_base") > 15000:
                            print(f'Website {website_name} contains HTML longer than 15000.')
                            long_website = True
                            break
                    elif model in ['deepseek','GPT4','phi']:
                        if num_tokens_from_string(simplify_html(html), "cl100k_base") > 31000:
                            print(f'Website {website_name} contains HTML longer than 32000.')
                            long_website = True
                            break
            if long_website:
                continue

        for item in SCHEMA[field]:
            print('-'*150)
            if dataset == 'swde':
                filename = os.path.join(GROUND_TRUTH_HOME, field, f'{website_name}-{item}.txt')
                ground_truth = load_file(filename)

            instruction = f"{prompt[field]['meta']} {prompt[field][item]} {prompt['meta']}"
            print(instruction)
                
            xpath_rule[item] = xe.rule_synthesis(website_name, html_list, instruction, max_token=max_token)
        
        with open(os.path.join(OUTPUT_HOME, PATTERN, field, website_name) + f'_{PATTERN}.json', 'w') as f:
            json.dump(xpath_rule, f, indent=4)