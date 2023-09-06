import json

with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

SECRET_KEY = config['NICE']['SECRET_KEY']
NICE_API_URL = config['NICE']['API_URL']
NICE_CLIENT_ID = config['NICE']['CLIENT_ID']
NICE_PRODUCT_ID = config['NICE']['PRODUCT_ID']
ACCESS_TOKEN = config['NICE']['ACCESS_TOKEN']

CLIENTS = config['CLIENTS']
