import requests

HOST = 'http://127.0.0.1:8000'


def post():
    post_data = {
        "title": "Selling an oil painting on canvas",
        "description": "Views of Italy",
        "owner": "Helen"
    }
    response = requests.post(f'{HOST}/ads', json=post_data)
    print(response.json())


# def get():
#     response = requests.get(f'{HOST}/ads/1')
#     print(response.json())
#
#
# def delete():
#     response = requests.delete(f'{HOST}/ads/1')
#     print(response.json())