import urllib.request
import json, yaml
import pymsteams
import time, datetime
import feedparser

"""
JVNから新着情報を取得

"""
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
        message.text('新しい情報は入ってきていません。【JVN】')
        message.send()
        break
    message_title += ' - [' + entry['category']['label'] + '] 【JVN】'
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


"""
IPAのRSSから記事更新情報を取得
RSSフィードは日付が逆順なので箱にいれてソートしてからセンド
"""
url = 'https://www.ipa.go.jp/security/rss/alert.rdf'
cont = feedparser.parse(url)
no_news = True
entries_container = []
for entry in cont['entries']:
    entry_date = datetime.datetime.fromisoformat(entry['updated'])
    if entry_date >= datetime.datetime.now() - datetime.timedelta(days=1):
        no_news = False
        message_title = entry['title'] + '【IPA】'
        message_text = '更新日：' + entry_date.strftime('%Y-%m-%d %H:%M:%S') + '</br>'
        message_text += "[関連情報](" + entry['link'] + ")"
        entries_container.append({'entry_date': entry_date, 'message_title': message_title, 'message_text': message_text})

entries_container = sorted(entries_container, key=lambda x: x['entry_date'])

if no_news:
    message = pymsteams.connectorcard(webhook_url)
    message.text('新しい情報は入ってきていません。【IPA】')
    message.send()

for entry in entries_container:
    message = pymsteams.connectorcard(webhook_url)
    message.title(entry['message_title'])
    message.text(entry['message_text'])
    message.send()
    time.sleep(1)