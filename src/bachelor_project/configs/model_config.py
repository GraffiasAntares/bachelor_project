TARGET = 'K'
SELECTED_FEATURES = [
    'temperature_2m_roll24',
    'wind_speed_10m',
    'mean_Ri',
    'max_Ri',
    'pressure_msl_roll24',
    'max_inv_roll24',
    'wind_speed_180m'
]

RF_PARAM_GRID = {
        'n_estimators': [10, 50, 100, 150, 200],
        'max_depth': [6, 10, 15, None],
        'min_samples_leaf': [4, 8, 15],
        'max_features': ['sqrt', 'log2', 0.25, 0.4]
    }
# RF_PARAM_GRID = {
#         'n_estimators': [10],
#         'max_depth': [6],
#         'min_samples_leaf': [4],
#         'max_features': ['sqrt', 'log2', 0.25, 0.4]
#     }