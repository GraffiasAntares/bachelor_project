from bachelor_project.configs import dir_config

import pandas as pd
import numpy as np


def add_derivative_features(df):
    """
    Адаптированная подготовка датасета с учетом вертикального профиля атмосферы 
    и динамической устойчивости (число Ричардсона).
    """
    data = df.copy()

    # ВЕРТИКАЛЬНАЯ ИНВЕРСИЯ
    inv_180_2 = data['temperature_180m'] - data['temperature_2m']
    inv_120_2 = data['temperature_120m'] - data['temperature_2m']
    inv_80_2 = data['temperature_80m'] - data['temperature_2m']

    data['max_inv'] = np.max([inv_80_2, inv_120_2, inv_180_2],axis=0)
    data['mean_inv'] = np.mean([inv_80_2, inv_120_2, inv_180_2],axis=0)
    data['grad_80_180_inv'] = inv_80_2 - inv_180_2
    data['inv_height'] = np.argmax([inv_80_2, inv_120_2, inv_180_2],axis=0)

    # Функция для расчета Ri между двумя высотами
    def calc_bulk_richardson_number(
        t_low, t_high,
        wind_speed_low, wind_dir_low,
        wind_speed_high, wind_dir_high,
        h_low, h_high
    ):
        """
        Bulk Richardson number между двумя уровнями.
    
        Вход:
        - t_low, t_high: температура
        - wind_speed_low/high: скорость ветра
        - wind_dir_low/high: направление ветра
        - h_low, h_high: высоты (m)
    
        Выход:
        - Ri_b: Bulk Richardson number
        """
    
        g = 9.81
        # --- высоты ---
        dz = h_high - h_low
        # --- температура (переход в K) ---
        theta_low = t_low + 273.15
        theta_high = t_high + 273.15
        theta_mean = (theta_low + theta_high) / 2.0
    
        dtheta = theta_high - theta_low
    
        # --- ветер: перевод в u,v ---
        def wind_to_uv(speed, direction_deg):
            rad = np.radians(direction_deg)
            u = speed * np.sin(rad)
            v = speed * np.cos(rad)
            return u, v
    
        u_low, v_low = wind_to_uv(wind_speed_low, wind_dir_low)
        u_high, v_high = wind_to_uv(wind_speed_high, wind_dir_high)
    
        # --- shear ---
        du = u_high - u_low
        dv = v_high - v_low
        shear = du**2 + dv**2
        # защита от деления на ноль / штиля
        shear = np.where(shear < 0.0001, 0.0001, shear)
        # --- Bulk Ri ---
        ri = (g / theta_mean) * (dtheta * dz) / shear
    
        return ri
    
    # Числа Ричардсона
    Ri_2_180 = calc_bulk_richardson_number(
        data['temperature_2m'], data['temperature_180m'],
        data['wind_speed_10m'], data['wind_direction_10m'],
        data['wind_speed_180m'], data['wind_direction_180m'],
        2, 180
    )
    Ri_2_120 = calc_bulk_richardson_number(
        data['temperature_2m'], data['temperature_120m'],
        data['wind_speed_10m'], data['wind_direction_10m'],
        data['wind_speed_120m'], data['wind_direction_120m'],
        2, 120
    )
    Ri_2_80 = calc_bulk_richardson_number(
        data['temperature_2m'], data['temperature_80m'],
        data['wind_speed_10m'], data['wind_direction_10m'],
        data['wind_speed_80m'], data['wind_direction_80m'],
        2, 80
    )

    data['max_Ri'] = np.max([Ri_2_80, Ri_2_120, Ri_2_180],axis=0)
    data['mean_Ri'] = np.mean([Ri_2_80, Ri_2_120, Ri_2_180],axis=0)
    data['grad_80_180_Ri'] = Ri_2_80 - Ri_2_180
    
    # Кодирование цикличных признаков
    # data['sin_month'] = np.sin(2 * np.pi * data['month'] / 12)
    # data['cos_month'] = np.cos(2 * np.pi * data['month'] / 12)
    # data['sin_hour'] = np.sin(2 * np.pi * data['hour'] / 24)
    # data['cos_hour'] = np.cos(2 * np.pi * data['hour'] / 24)
    # data['sin_DOY'] = np.sin(2 * np.pi * data['day_of_year'] / 365)
    # data['cos_DOY'] = np.cos(2 * np.pi * data['day_of_year'] / 365)

    data['sin_wind_direction_10m'] = np.sin(2 * np.pi * data['wind_direction_10m'] / 360)
    data['cos_wind_direction_10m'] = np.cos(2 * np.pi * data['wind_direction_10m'] / 360)

    data['wind_shear'] = data['wind_speed_180m'] - data['wind_speed_10m']
    
    return data.dropna()


def add_rolling_features(df):
    data = df.copy()

    for col in data.drop(['K'],axis=1).columns:
        # data[col+'_roll4'] = data[col].rolling(window=4).mean()
        # data[col+'_roll8'] = data[col].rolling(window=8).mean()
        # data[col+'_roll12'] = data[col].rolling(window=12).mean()
        data[col+'_roll24'] = data[col].rolling(window=24).mean()

    return data.dropna()


def get_features_and_save():
    ext_df = pd.read_csv(dir_config.PREP_K_DATA_DIR)
    ext_df['time'] = pd.to_datetime(ext_df['time'])
    ext_df = ext_df.set_index('time')

    ext_df = add_derivative_features(ext_df)
    ext_df = add_rolling_features(ext_df)
    
    ext_df = ext_df.reset_index()
    ext_df.to_csv(dir_config.FEATURES_DATA_DIR, index=False)
    

def main():
    get_features_and_save()


if __name__ == '__main__':
    main()




    