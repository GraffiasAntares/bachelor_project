import argparse
import requests
from pathlib import Path

import openmeteo_requests
import pandas as pd
import requests_cache

from retry_requests import retry
from datetime import date, timedelta
from tqdm import tqdm


# ----------------------------------------------------------
# Импорт данных о загрязнении воздуха
# ----------------------------------------------------------

def get_pm25_daily_data(date):
    
    time_begin = date.isoformat() + ' 00:00:00'
    time_end = (date+timedelta(1)).isoformat() + ' 00:00:00'

    req = requests.get(
        'http://air.krasn.ru/api/2.0/data',
            params={
              'time_begin': time_begin,
              'time_end': time_end,
              'time_interval': 'hour',
              'projects': '9'
            }
    ).json()
    
    if req['status']['message'] != 'OK':
        raise Exception('Status is not ok')

    df = pd.DataFrame(req['data'])
    df['time'] = pd.to_datetime(df['time'])
    df_date = pd.DataFrame({'time': pd.date_range(time_begin,time_end,freq='1h',inclusive='left')})
    groups = []
    for site, group in df.groupby('site'):
        sub = pd.merge(group, df_date, on='time', how='right')
        sub ['site'] = [site for _ in range(sub.shape[0])]
        groups.append(sub)
    
    df = pd.concat(groups)
    df = df.rename(columns={'time': 'date'})
    
    df["date"] = (
        pd.to_datetime(df["date"])
        .dt.tz_localize("Asia/Krasnoyarsk")
        .dt.tz_convert("UTC")
    )
    
    return df[['date','site','pm25']].sort_values(by=['date','site']).reset_index(drop=True)

def get_pm25_data(start_date, end_date, progress=False):
    start_date = date(*map(int,start_date.split('-')))
    end_date = date(*map(int,end_date.split('-')))
    delta = (end_date - start_date).days
    data = []

    if progress: loop = tqdm(range(delta))
    else: loop = range(delta)

    for _ in loop:
        daily = get_pm25_daily_data(start_date)
        data.append(daily)
        start_date += timedelta(1)

    return pd.concat(data).reset_index(drop=True)


# ----------------------------------------------------------
# Импорт данных погоды
# ----------------------------------------------------------

def get_historical_weather_data(
        start_date: str, # "YYYY-MM-DD"
        end_date: str    # "YYYY-MM-DD"
        ) -> dict:

    # Учитываем, что данные open-meteo привязаны к временю Гринвича 
    # (7 часов данных находятся в предыдущем дне)
    start_date = (date(*map(int,start_date.split('-'))) - timedelta(1)).isoformat()
    
    cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)

    url = "https://historical-forecast-api.open-meteo.com/v1/forecast"
    data_columns = [
        'temperature_2m',
        'relative_humidity_2m', 
        'pressure_msl',
        'surface_pressure',
        'temperature_80m',
        'temperature_120m',
        'temperature_180m',
        'wind_speed_10m',
        'wind_speed_80m',
        'wind_speed_120m',
        'wind_speed_180m',
        'wind_direction_10m',
        'wind_direction_80m',
        'wind_direction_120m',
        'wind_direction_180m',
        'precipitation', 
        'shortwave_radiation'
    ]
    params = {
        "latitude": 56.0267,
        "longitude": 92.9077,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": data_columns,
        "wind_speed_unit": "ms",
    }
    responses = openmeteo.weather_api(url, params = params)
    response = responses[0]
   
    # print(f"Timezone difference to GMT+0: {response.UtcOffsetSeconds()}s")
    
    hourly = response.Hourly()

    hourly_data = {
        "date": pd.date_range(
            start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
    		end =  pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
    		freq = pd.Timedelta(seconds = hourly.Interval()),
    		inclusive = "left"
        )
    }
    for i, col in enumerate(data_columns):
        hourly_data[col] = hourly.Variables(i).ValuesAsNumpy()
        
    hourly_dataframe = pd.DataFrame(data = hourly_data)
    df_date = pd.DataFrame({'date': pd.date_range(start_date,end_date,freq='1h',inclusive='left')})
    df_date['date'] = pd.to_datetime(df_date['date'], utc=True)

    df = pd.merge(hourly_dataframe, df_date,on='date', how='right')
    
    return df


# ----------------------------------------------------------
# Объединение данных
# ----------------------------------------------------------

def merge_2data_frames(df1, df2):
    df = pd.merge(df1, df2, on='date')
    df['date'] = pd.to_datetime(df['date']).dt.tz_convert('Asia/Krasnoyarsk')
    return df


# ----------------------------------------------------------
# Создание файла с мета-данными
# ----------------------------------------------------------

def create_meta(timestamp, start_date, end_date):
    pass


# ----------------------------------------------------------
# Пайплайн загрузки
# ----------------------------------------------------------

def load_data(start_date: str, #YYYY-MM-DD
              end_date: str,   #YYYY-MM-DD
              path: str):
    
    df_pollution = get_pm25_data(start_date, end_date)
    df_weather = get_historical_weather_data(start_date, end_date)
    merge_2data_frames(df_pollution, df_weather).to_csv(path, index=False)

    
def main():
    parser = argparse.ArgumentParser()
    path = Path(__file__).resolve().parent.parent / 'data' / 'raw' / 'meteo_and_pollution.csv'
    parser.add_argument("start_date", help="Начало выборки")
    parser.add_argument("end_date", help="Конец выборки")    
    args = parser.parse_args()

    print("Скачивание данных загрязнения...")
    df_pollution = get_pm25_data(args.start_date, args.end_date, True)

    print("Скачивание метео-данных...")
    df_weather = get_historical_weather_data(args.start_date, args.end_date)

    print("Объединение данных...")
    df = pd.merge(df_pollution, df_weather, on='date')
    df['date'] = pd.to_datetime(df['date']).dt.tz_convert('Asia/Krasnoyarsk')
    
    df.to_csv(path, index=False)
    print("Данные сохранены в директории", path)

if __name__=='__main__':
    main()