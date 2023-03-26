import requests

for i in range(0,3):
    requests.post('https://api.miragari.com/fast/fastChat', json={'question': [{'role': 'user', 'content': '你好'}]})
    print(i)


