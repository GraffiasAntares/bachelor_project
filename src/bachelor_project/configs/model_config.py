TARGET = 'K'

RF_PARAM_GRID = {
        'n_estimators': [10, 50, 100, 200],
        'max_depth': [6, 10, 15],
        'min_samples_leaf': [4, 8, 15],
        'max_features': ['sqrt', 'log2', 0.25, 0.4],
    }

KAN_TRAIN_CONFIG = {
    'epochs': 5,
    'learning_rate': 1,
    'lambd': 0.001,
    'scheduler_patience': 5,
    'auto_save': False
}

KAN_PARAMS = {
    'grid': 8
}