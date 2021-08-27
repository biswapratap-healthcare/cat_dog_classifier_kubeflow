import base64
import json
import requests
from datetime import datetime


# handle = "localhost"
handle = "34.93.174.195"


def fetch():
    # d_date = datetime.today().strftime('%Y-%m-%d').split('-')
    d_date = "2021-08-25".split('-')
    year = d_date[0]
    month = d_date[1]
    day = d_date[2]
    from_date = str(year) + '-' + str(month) + '-' + str(day)
    to_date = from_date
    url = "http://" + handle + ":7000/get_data_from_to"
    r = requests.post(url, data={'from': from_date, 'to': to_date})
    content = json.loads(r.content)
    td = list()
    for _id, value in content.items():
        data = base64.b64decode(value['Image'])
        td.append([value['Label'], data])
    return td
