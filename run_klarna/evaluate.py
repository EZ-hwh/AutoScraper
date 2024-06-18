import json
import glob, os, re
from collections import defaultdict
import argparse 
from bs4 import BeautifulSoup

parser = argparse.ArgumentParser()

parser.add_argument('--pattern', type=str, choices=['cot', 'reflexion', 'autocrawler'], help='Which type of crawler generation agent to use.')
parser.add_argument('--model', type=str, help='Backbone model')

SCHEMA = {
    'product': ['name', 'price'],
}

item_map = {
    'name': 'Name',
    'price': 'Price'
}

args = parser.parse_args()
print(args)

PATTERN = args.pattern
model = args.model

GROUND_TRUTH_HOME = '/mnt/data122/harryhuang/klarna_product_page_dataset_WTL_50k/train/US'
OUTPUT_HOME = f'dataset/klarna/{model}/{PATTERN}'

def load_value(html_content, item_name):
    # 使用BeautifulSoup解析HTML
    soup = BeautifulSoup(html_content, 'html.parser')

    # 查找所有klarna-ai-label属性为"Name"的节点
    name_nodes = soup.find_all(attrs={'klarna-ai-label': item_map[item_name]})
    
    result = []
    # 提取并打印每个节点的文本
    for node in name_nodes:
        result.append(node.text.strip())
    return result

def load_gt(file_path, schema_list):
    ground_truth = {a:{} for a in schema_list}
    for html_file in glob.glob(file_path):
        with open(html_file, 'r', errors='ignore') as f:
            html_content = f.read()
            page_index = html_file.split('/')[-2]
            for item in schema_list:
                ground_truth[item][page_index] = load_value(html_content, item)
    return ground_truth

def normalize(text):
    #print(text_list)
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&amp;', '&')
    text = text.replace('&quot;', '"')
    text = text.replace('&#39;', "'").replace('&apos;', "'")
    text = text.replace('&#150;', '–')
    text = text.replace('&nbsp;', ' ')
    text = text.replace('&#160;', ' ')
    text = text.replace('&#039;', "'")
    text = text.replace('&#34;', '"')
    text = text.replace('&reg;', '®')
    text = text.replace('&rsquo;','’')
    text = text.replace('&#8226;','•')
    text = text.replace('&ndash;','–')
    text = text.replace('&#x27;', "'")
    text = text.replace('&#40;', '(')
    text = text.replace('&#41;', ')')
    text = text.replace('&#47;','/')
    text = text.replace('&#43;','+')
    text = text.replace('&#035;','#')
    text = text.replace('&#38;', '&')
    text = text.replace('&eacute;', 'é')
    text = text.replace('&frac12;', '½')
    text = text.replace('  ', ' ')
    text = re.sub(r"\s+", "", text)
    return text.strip()

def normalize_list(text_list):
    return [normalize(text) for text in text_list if text and normalize(text)]

result_dict = {}
result_overall = {}
result_summary = {
    'Fully correct': 0,
    'Precision': 0,
    'Recall': 0,
    'Unexecute': 0,
    'Overestimate': 0,
    'Else': 0,
    'Total': 0,
    'Micro_p': 0.0,
    'Micro_r': 0.0,
    'Micro_f1': 0.0
}

for field in SCHEMA.keys():
    result_dict[field] = {}
    result_overall[field] = {}
    for website_path in glob.glob(os.path.join(OUTPUT_HOME, field, '*')):
        print(website_path)
        if f'_{PATTERN}.json' in website_path:
            continue
        website_name = website_path.split('/')[-1].replace('.json', '')
        result_dict[field][website_name] = {}

        ground_truth = load_gt(os.path.join(GROUND_TRUTH_HOME, website_name, '*', 'source.html'), SCHEMA[field])
        
        # for item in SCHEMA[field]:
        #     ground_truth[item] = load_file(filename)
        #print(ground_truth)

        with open(website_path, 'r') as f:
            predict_result = json.load(f)
        #print(predict_result)
        tp = defaultdict(int)
        tn = defaultdict(int)
        fp = defaultdict(int)

        for result in predict_result:
            page_index = result['page'].split('/')[-1].replace('.htm', '')
            result_dict[field][website_name][page_index] = {}
            for item in SCHEMA[field]:
                #print(result)
                result_dict[field][website_name][page_index][item] = {}
                pred = set(normalize_list(result[item]))
                gt = set(normalize_list(ground_truth[item][page_index]))
                result_dict[field][website_name][page_index][item]['pred'] = list(pred)
                result_dict[field][website_name][page_index][item]['ground_truth'] = list(gt)

                tp[item] += len(pred & gt)
                fp[item] += len(pred - gt)
                tn[item] += len(gt - pred)

        result_overall[field][website_name] = {}
        for item in SCHEMA[field]:
            p = (tp[item] + 1e-12) / (fp[item] + tp[item] + 1e-12)
            r = (tp[item] + 1e-12) / (tp[item] + tn[item] + 1e-12)
            f1 = (2 * p * r) / (p + r + 1e-12)
            result_overall[field][website_name][item] = {
                'Precision': round(p, 4),
                'Recall': round(r, 4),
                'F1': round(f1, 4),
                'TP': tp[item],
                'FP': fp[item],
                'TN': tn[item]
            }
            #print(p)
            if round(f1, 4) == 1.00:
                result_summary['Fully correct'] += 1
            elif (round(p, 4) == 1.00) and (round(r, 4) != 0.00):
                result_summary['Precision'] += 1
            elif (round(r, 4) == 1.00) and (round(p, 4) != 0.00):
                result_summary['Recall'] += 1
            elif (round(r, 4) == 0.00):
                result_summary['Unexecute'] += 1
            elif (round(p, 4) == 0.00):
                result_summary['Overestimate'] += 1
            else:
                result_summary['Else'] += 1
            result_summary['Total'] += 1
            result_summary['Micro_p'] += p
            result_summary['Micro_r'] += r
            result_summary['Micro_f1'] += f1

for key in result_summary.keys():
    if key != 'Total':
        result_summary[key] = round(result_summary[key] / result_summary['Total'], 4)

print(json.dumps(result_summary, indent=4))
with open(os.path.join(OUTPUT_HOME, 'result.json'), 'w') as f:
    json.dump(result_dict, f, ensure_ascii=False, indent=4)

with open(os.path.join(OUTPUT_HOME, 'result_overall.json'), 'w') as f:
    json.dump(result_overall, f, ensure_ascii=False, indent=4)

with open(os.path.join(OUTPUT_HOME, 'result_summary.json'), 'w') as f:
    json.dump(result_summary, f, ensure_ascii=False, indent=4)