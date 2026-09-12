import requests
import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry

# ----------------------------------------------------------
# Импорт данных о загрязнении воздуха
# ----------------------------------------------------------
def day_(day):
    if day < 1 or day > 31:
        raise ValueError
    elif day < 10:
        return '0'+f'{day}'
    elif day >= 10:
        return str(day)

def month_(month):
    if month < 1 or month > 12:
        raise ValueError
    elif month < 10:
        return '0'+f'{month}'
    elif month >= 10:
        return str(month)

def pollution_day_data(year, month, day):
    time_begin = '20'+str(year)+'-'+month_(month)+'-'+day_(day)+' 00:00:00'
    time_end = '20'+str(year)+'-'+month_(month)+'-'+day_(day)+' 23:00:00'

    req = requests.get(
        'http://air.krasn.ru/api/2.0/data',
            params={
              'time_begin': str(time_begin),
              'time_end': str(time_end),
              'time_interval': 'hour',
              'projects': '9'
            }
    ).json()
    
    if req['status']['message'] != 'OK':
        raise Exception('Status is not ok')
    else:
        return req
        
def get_big_data(year_begin, year_end):
    data = []
    perc = 0
    while year_begin < year_end:
        for month in range(1, 12+1):
            for day in range(1, 28+1):
                req = pollution_day_data(year_begin, month, day)
                data.append(req)
        # print(f'{year_begin}:{month}', req['status']['message'])
            perc += 8.33
            print(f'{year_begin} {perc}%')
        year_begin += 1
    return data

def to_DataFrame(big_data):
    big_arr = [[data['data'] for data in big_data][i] for i in range(len(big_data))]
    new_big_arr = [day[i] for day in big_arr for i in range(len(day))]
    return pd.DataFrame(data=new_big_arr)


# ----------------------------------------------------------
# Импорт данных о погоде
# ----------------------------------------------------------

def get_weather_data(
        start_date: str,
        end_date: str
        ) -> dict:
    
    pass