import glob
import json, os, sys
from tqdm import tqdm
from utils.html_utils import *
from module.stepback_crawler import StepbackCrawler
from module.reflexion_crawler import AutoCrawler
from module.prompt import *

from utils.ms_api_copy import ms_chatgpt as chatgpt
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
    from utils.ms_api_copy import ms_gpt4 as chatgpt
elif model == 'ChatGPT':
    from utils.ms_api_copy import ms_chatgpt as chatgpt

if PATTERN == 'autocrawler':
    xe = StepbackCrawler(api=chatgpt)
    extract = xe.extract_with_sequence
else:
    xe = AutoCrawler(PATTERN, api=chatgpt)
    extract = xe.extract_with_xpath

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
    if model == 'ChatGPT':
        filter_website = ['shoppings_bestbuy', 'shoppings_pcworld', 'shoppings_uttings', 'shoppings_amazoncouk', 'shoppings_tesco', 'kayak', 'ratestogo', 'expedia', 'hotels', 'venere', 'rottentomatoes', 'metacritic', 'imdb']
    else:
        filter_website = []
elif dataset == 'extended_swde':
    from run_swde_et.schema import SCHEMA
    DATA_HOME = '/mnt/data122/harryhuang/swde/sourceCode'
    if model == 'ChatGPT':
        filter_website = ['book-amazon', 'camera-onsale', 'camera-jr', 'camera-compsource', 'camera-buy', 'movie-metacritic', 'movie-rottentomatoes', 'nbaplayer-wiki', 'university-collegenavigator', 'university-matchcollege']
    else:
        filter_website = []
OUTPUT_HOME = f'dataset/{dataset}/{model}/{PATTERN}'


for field in SCHEMA.keys():
    if not os.path.exists(os.path.join(OUTPUT_HOME, field)):
        os.makedirs(os.path.join(OUTPUT_HOME, field))

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

    for website_path in weblist:
        if dataset in ['extended_swde', 'swde']:
            website_name = website_path.split('/')[-1].split('(')[0]
        elif dataset == 'ds1':
            website_name = website_path.split('/')[-1].replace(f'{field}_','').replace(f'_{fake_item}.html','')
        #print(website_name)
        if os.path.exists(os.path.join(OUTPUT_HOME, field, website_name) + '.json'):
            continue
        
        xpath_rule = {}
        # sorted(webpage_list)
        print(os.path.join(OUTPUT_HOME, field, website_name) + f'_{PATTERN}.json')
        if not os.path.exists(os.path.join(OUTPUT_HOME, field, website_name) + f'_{PATTERN}.json'):
            continue
        with open(os.path.join(OUTPUT_HOME, field, website_name) + f'_{PATTERN}.json', 'r') as f:
            xpath_rule = json.load(f)

        # Rule execution
        result_list = []
        
        # web_index = webpage.split('/')[-1].replace('.htm','')
        if dataset in ['swde', 'extended_swde']:
            webpage_list = glob.glob(os.path.join(website_path, '*'))
            sorted(webpage_list)
            for webpage in tqdm(webpage_list[:100]):
                web_index = webpage.split('/')[-1].replace('.htm','')

                with open(webpage, 'r', errors='ignore') as f:
                    html = f.read()
                
                new_res = {'page': web_index}
                for item in SCHEMA[field]:
                    item_value = extract(html, xpath_rule[item])
                    new_res[item] = item_value

                    #print(item, item_value)
                result_list.append(new_res)
        elif dataset == 'ds1':
            with open(website_path, 'r', errors='ignore') as f:
                html = f.read()
            
            new_res = {'page': 0}
            for item in SCHEMA[field]:
                item_value = extract(html, xpath_rule[item])
                new_res[item] = item_value

            result_list.append(new_res)

        with open(os.path.join(OUTPUT_HOME, field, website_name) + '.json', 'w') as f:
            json.dump(result_list, f, indent=4)
    