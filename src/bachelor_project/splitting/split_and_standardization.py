from bachelor_project import config

import joblib
import pandas as pd
from sklearn.preprocessing import StandardScaler


def split(df):
    train = df[df.index < '2024-01-01']
    val = df[(df.index >= '2024-01-01') & (df.index < '2025-01-01')]
    test = df[df.index >= '2025-01-01']

    return train, val, test


def fit_transform(df):
    scaler = StandardScaler()
    index = df.index
    transformed = scaler.fit_transform(df.drop(['K'],axis=1).values)
    transformed = pd.DataFrame(data=transformed,columns=df.drop(['K'],axis=1).columns,index=index)

    joblib.dump(scaler, config.SCALER_DIR)
    return transformed.join(df[['K']])


def transform(df):
    scaler = joblib.load(config.SCALER_DIR)

    index = df.index
    transformed = scaler.transform(df.drop(['K'],axis=1).values)
    transformed = pd.DataFrame(data=transformed,columns=df.drop(['K'],axis=1).columns,index=index)

    return transformed.join(df[['K']])


def main():
    df = pd.read_csv(config.PREP_K_DATA_DIR)
    df['time'] = pd.to_datetime(df['time'])
    df = df.set_index('time')

    df = fit_transform(df)
    train, val, test = split(df)

    train.reset_index().to_csv(config.TRAIN_DATA, index=False)
    val.reset_index().to_csv(config.VAL_DATA, index=False)
    test.reset_index().to_csv(config.TEST_DATA, index=False)


if __name__=='__main__':
    main()