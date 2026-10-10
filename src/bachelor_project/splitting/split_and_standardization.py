from bachelor_project.configs import dir_config

import joblib
import pandas as pd
from sklearn.preprocessing import StandardScaler


def split(df):
    train = df[df.index.year == 2023]
    val = df[df.index.year == 2024]
    test = df[df.index.year == 2025]
    
    return train, val, test


def fit_transform(df):
    scaler = StandardScaler()
    index = df.index
    transformed = scaler.fit_transform(df.drop(['K'],axis=1).values)
    transformed = pd.DataFrame(data=transformed,columns=df.drop(['K'],axis=1).columns,index=index)

    joblib.dump(scaler, dir_config.SCALER_DIR)
    return transformed.join(df[['K']])


def transform(df):
    scaler = joblib.load(dir_config.SCALER_DIR)

    index = df.index
    transformed = scaler.transform(df.drop(['K'],axis=1).values)
    transformed = pd.DataFrame(data=transformed,columns=df.drop(['K'],axis=1).columns,index=index)

    return transformed.join(df[['K']])


def main():
    df = pd.read_csv(dir_config.FEATURES_DATA_DIR)
    df['time'] = pd.to_datetime(df['time'])
    df = df.set_index('time')
    
    df = fit_transform(df)
    train, val, test = split(df)

    train.reset_index().to_csv(dir_config.TRAIN_DATA, index=False)
    val.reset_index().to_csv(dir_config.VAL_DATA, index=False)
    test.reset_index().to_csv(dir_config.TEST_DATA, index=False)


if __name__=='__main__':
    main()