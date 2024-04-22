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
parser.add_argument('--dataset', type=str, choices=['swde','ds1','extended_swde'], help='Which dataset to test.')
parser.add_argument('--seed_website', type=int)
parser.add_argument('--save_name', type=str)
parser.add_argument('--overwrite', type=bool, help='Whether overwrite the generated crawler.')

args = parser.parse_args()
print(args)

PATTERN = args.pattern
model = args.model
dataset = args.dataset
num_seed_website = args.seed_website
overwrite = args.overwrite

if model == 'GPT4':
    from utils.api import chatgpt
elif model == 'ChatGPT':
    from utils.ms_api_copy import ms_chatgpt as chatgpt

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
        filter_website = ['book-amazon', 'camera-onsale', 'camera-jr', 'camera-compsource', 'camera-buy', 'movie-metacritic', 'movie-rottentomatoes', 'nbaplayer-wiki', 'university-collegenavigator', 'university-matchcollege']
    else:
        filter_website = []
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
    
OUTPUT_HOME = f'dataset/{dataset}/{model}'

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
    #print(weblist)
    for website_path in weblist:
        if dataset in ['extended_swde', 'swde']:
            website_name = website_path.split('/')[-1].split('(')[0]
        elif dataset == 'ds1':
            website_name = website_path.split('/')[-1].replace(f'{field}_','').replace(f'_{fake_item}.html','')
        print('-'*200)
        print(website_name)

        if website_name in filter_website:
            continue

        if os.path.exists(os.path.join(OUTPUT_HOME, PATTERN, field, website_name) + f'_{PATTERN}.json'):
            continue
        webpage_list = glob.glob(os.path.join(website_path, '*'))
        xpath_rule = {}
        html_list = []

        if dataset in ['swde', 'extended_swde']:
            sorted(webpage_list)
            for html_page in webpage_list[:num_seed_website]:
                with open(html_page, 'r') as f:
                    html_list.append(f.read())
        elif dataset == 'ds1':
            with open(website_path, 'r', errors='ignore') as f:
                html_list.append(f.read())

        for item in SCHEMA[field]:
            print('-'*150)
            instruction = f"{prompt[field]['meta']} {prompt[field][item]} {prompt['meta']}"
            print(instruction)
            xpath_rule[item] = xe.rule_synthesis(website_name, html_list, instruction)
        
        with open(os.path.join(OUTPUT_HOME, PATTERN, field, website_name) + f'_{PATTERN}.json', 'w') as f:
            json.dump(xpath_rule, f, indent=4)