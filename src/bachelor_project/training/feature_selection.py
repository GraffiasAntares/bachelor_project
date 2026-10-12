from bachelor_project.configs import model_config
from bachelor_project.configs import dir_config

import itertools

import mlflow
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score
from sklearn.inspection import permutation_importance
from sklearn.model_selection import TimeSeriesSplit, RandomizedSearchCV

from tqdm import tqdm


def cross_validation(run_name, estimator, features, target):
    tscv = TimeSeriesSplit(n_splits=5)
    with mlflow.start_run(run_name=run_name, nested=True):
        mean_training_r2 = 0
        mean_validation_r2 = 0
        for train_idxs, val_idxs in tscv.split(features):
            estimator.fit(features[train_idxs], target[train_idxs])
            train_pred = estimator.predict(features[train_idxs])
            val_pred = estimator.predict(features[val_idxs])
            train_r2 = r2_score(target[train_idxs], train_pred)
            val_r2 = r2_score(target[val_idxs], val_pred)

            mean_training_r2 += train_r2 / tscv.get_n_splits()
            mean_validation_r2 += val_r2 / tscv.get_n_splits()

        mlflow.log_params(estimator.get_params())
        mlflow.log_metric('training_r2', mean_training_r2)
        mlflow.log_metric('validation_r2', mean_validation_r2)
    
    return estimator, mean_training_r2, mean_validation_r2


def cv_tuning_model(estimator, grid, features, target):
    with mlflow.start_run(run_name="tuning", nested=True):

        # Прогоны с разными гиперпараметрами
        tscv = TimeSeriesSplit(n_splits=5)
        tuning = RandomizedSearchCV(estimator=estimator,
                                    param_distributions=grid,
                                    n_iter=100,
                                    cv=tscv,
                                    refit=True,
                                    scoring='r2')
        tuning.fit(features, target)

        return tuning.best_estimator_, tuning.best_params_


def iterative_train(model, features, target, features_order, iters=None):
    if not iters: iters = len(features)
    metrics = {
        'num_of_features': [*range(1,iters+1)],
        'training_r2': []
    }
    with mlflow.start_run(run_name="simplification", nested=True):
        # Прогоны с разным количеством признаков
        for feat_i in metrics['num_of_features']:
            with mlflow.start_run(run_name=f'RF_f{feat_i}', nested=True):
                feats = features_order[:feat_i]
                model.fit(features[feats],target)

                pred = model.predict(features[feats])
                
                train_r2 = r2_score(target, pred)            

                mlflow.log_params(params=model.get_params())
                mlflow.log_param(key="num_of_features", value=feat_i)
                mlflow.log_metric(key="training_r2", value=train_r2)

                metrics['training_r2'].append(train_r2)

    return metrics


def save_selected_features(features, save_path):
    path = Path(save_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(
            {"features": features},
            file,
            ensure_ascii=False,
            indent=4,
        )


def save_feature_importance_graph(verification_df, iterative_metrics, save_path):
    fig, axes = plt.subplots(
        nrows=1,
        ncols=2,
        figsize=(15, 9),
        layout="constrained",
    )

    ax_im, ax_pi= axes.flat

    ax_im.plot(iterative_metrics['num_of_features'], iterative_metrics['training_r2'], 'o-', label='train')
    ax_im.set_xlabel('Количество признаков')
    ax_im.set_ylabel('R2')
    ax_im.set_title('R2 от количества признаков')
    ax_im.set_xticks(iterative_metrics['num_of_features'][::1])
    ax_im.legend()
    ax_im.grid()

    ax_pi.barh(verification_df['Feature'].iloc[:10][::-1],verification_df['Importance'].iloc[:10][::-1])
    ax_pi.set_title('Топ 10 признаков по важности')
    ax_pi.set_xlabel('Важность признаков')

    fig.savefig(save_path)


def run_selection():

    mlflow.set_tracking_uri("http://127.0.0.1:5000")
    mlflow.set_experiment("feature_selection_by_random_forest")
    mlflow.sklearn.autolog(max_tuning_runs=10)
    
    train = pd.read_csv(dir_config.TRAIN_DATA).set_index('time')
    val = pd.read_csv(dir_config.VAL_DATA).set_index('time')
    training_dataset = pd.concat([train, val])

    target = model_config.TARGET
    features = training_dataset.drop([target],axis=1).columns
    
    model, params = cv_tuning_model(RandomForestRegressor(), model_config.RF_PARAM_GRID,
                                    training_dataset[features], training_dataset[target])
    
    result = permutation_importance(
        model, training_dataset[features], training_dataset[target], 
        scoring='r2', 
        n_repeats=10, 
        random_state=42, 
        n_jobs=-1
    )

    # Формируем итоговый топ
    verification_df = pd.DataFrame({
        'Feature': features,
        'Importance': result.importances_mean,
        'Importance_Std': result.importances_std
    }).sort_values(by='Importance', ascending=False)

    iterative_metrics = iterative_train(RandomForestRegressor(**params),
                              training_dataset[features], 
                              training_dataset[target],
                              features_order=verification_df['Feature'].values,
                              iters=20)

    for num_of_features, metric_value in enumerate(iterative_metrics['training_r2']):
        if metric_value / iterative_metrics['training_r2'][-1] >= 0.95:
            num_of_features += 1
            break
    
    selected_features = list(verification_df['Feature'].values[:num_of_features])

    save_selected_features(selected_features, dir_config.FEATURE_SELECTION_ARTIFACTS_DIR)
    save_feature_importance_graph(verification_df, iterative_metrics, dir_config.FEATURES_IMPORTANCE_DIR)


def main():
    run_selection()


if __name__=='__main__':
    main()