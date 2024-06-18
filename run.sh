python crawler_generation.py \
    --pattern autocrawler \
    --dataset swde \
    --model ChatGPT \
    --seed_website 5 \
    --save_name ChatGPT_five \
    --overwrite True \
    --max_token 14000

python crawler_extraction.py \
    --pattern autocrawler \
    --dataset swde \
    --model ChatGPT_cul \
    --save_name ChatGPT_cul

python run_swde/evaluate.py --pattern autocrawler --model GPT4_8000_3


python crawler_generation.py \
    --pattern reflexion \
    --dataset klarna \
    --model GPT4 \
    --seed_website 1 \
    --save_name GPT4 \
    --max_token 100000

python crawler_extraction.py \
    --pattern reflexion \
    --dataset klarna \
    --model GPT4

python run_klarna/evaluate.py --pattern autocrawler --model ChatGPT_5