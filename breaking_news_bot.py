import urllib.request
import json
import pymsteams
import time
import yaml

with open('stopItem.yaml') as f:
    yml = yaml.safe_load(f)
    stop_item = yml['stopItem']
    start_item = str(stop_item + 1)
    webhook_url = yml['webhookUrl']
url = 'https://jvndb.jvn.jp/myjvn?method=getAlertList&feed=hnd&ft=json&datePublished=2021&startItem=' + start_item
res = urllib.request.urlopen(url)
cont = json.loads(res.read().decode('utf8'))
for entry in cont['feed']['entry']:
    message = pymsteams.connectorcard(webhook_url)
    message_title = entry['title']
    if message_title == '該当する注意警戒情報はありません。':
        message.text('新しい情報は入ってきていません。')
        message.send()
        break
    message_title += ' - [' + entry['category']['label'] + ']'
    message_text = '公開日：' + entry['published'][:10] + '</br>'
    message_text += '更新日：' + entry['update'][:10] + '</br>'
    message_text += "[関連情報](" + entry['sec:items'][0]['sec:item']['sec:link'] + ")"
    message.title(message_title)
    message.text(message_text)
    message.send()
    stop_item += 1
    time.sleep(1)

with open('stopItem.yaml', 'w') as f:
    yml = {'stopItem': stop_item, 'webhookUrl': webhook_url}
    yaml.safe_dump(yml, f)