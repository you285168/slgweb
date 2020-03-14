import random
from hashlib import md5
import requests
import json
import logging

logger = logging.getLogger('wasteland')
BAIDU_TOKEN = ["en", "zh", "cht", "fra", "spa", "kor", "jp", "ru", "it", "pl", "nl", "de", "pt", "ara", "th", "vie"]
GOOGLE_TOKEN = []
APP_ID = "20161214000034044"
SEC_KEY = "n5nkbNxY5asmLilQ1oEy"
BAIDU_URL = "http://api.fanyi.baidu.com/api/trans/vip/translate"


def baidu_translate(text, language):
    if not language:
        language = 2
    if language in BAIDU_TOKEN:
        to = BAIDU_TOKEN[language]
    else:
        to = BAIDU_TOKEN[0]
    args = {
        'q': text,
        'appid': APP_ID,
        'salt': random.randint(10000, 99999),
        'from': 'auto',
        'to': to,
    }
    sign = APP_ID + text + str(args['salt']) + SEC_KEY
    args['sign'] = md5(sign.encode('utf8')).hexdigest()
    res = requests.post(BAIDU_URL, data=args)
    data = {}
    ret = json.loads(res.content)
    if not ret or 'error_code' in ret:
        logger.warning('baidu translate error {0}', res.content)
    else:
        data['from'] = ret['from']
        data['to'] = ret['to']
        if ret["trans_result"] and ret["trans_result"][0]["dst"]:
            data['text'] = ret['trans_result'][0]["dst"]
        else:
            data['text'] = text
    return data
