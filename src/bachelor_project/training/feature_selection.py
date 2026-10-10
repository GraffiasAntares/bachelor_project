from bachelor_project.configs import model_config
from bachelor_project.configs import dir_config

import itertools

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from tqdm import tqdm
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score
from sklearn.inspection import permutation_importance


def run_selection():
    X_train = pd.read_csv(dir_config.TRAIN_DATA).set_index('time').drop([model_config.TARGET],axis=1)
    y_train = pd.read_csv(dir_config.TRAIN_DATA).set_index('time')[model_config.TARGET]

    X_val = pd.read_csv(dir_config.VAL_DATA).set_index('time').drop([model_config.TARGET],axis=1)
    y_val = pd.read_csv(dir_config.VAL_DATA).set_index('time')[model_config.TARGET]

    param_grid = model_config.RF_PARAM_GRID
    keys, values = zip(*param_grid.items())
    experiments = [dict(zip(keys, v)) for v in itertools.product(*values)]
    
    best_r2_val = -float('inf')
    best_params = None
    results_history = []
    
    print(f"Запуск перебора {len(experiments)} комбинаций...")
    
    for params in tqdm(experiments):
        rf = RandomForestRegressor(**params, random_state=42, n_jobs=-1)
        
        rf.fit(X_train, y_train)
        
        preds_train = rf.predict(X_train)
        preds_val = rf.predict(X_val)
        
        r2_train = r2_score(y_train, preds_train)
        r2_val = r2_score(y_val, preds_val)
        
        results_history.append({
            'params': params,
            'r2_train': r2_train,
            'r2_val': r2_val,
            'gap': r2_train - r2_val
        })
        
        if r2_val > best_r2_val:
            best_r2_val = r2_val
            best_params = params
    
    print("\n=== ОПТИМИЗАЦИЯ ЗАВЕРШЕНА ===")
    print(f"Лучшие параметры: {best_params}")
    print(f"Максимальный R2 на Валидации: {best_r2_val:.4f}")

    best_rf = RandomForestRegressor(**best_params, random_state=42, n_jobs=-1)
    best_rf.fit(X_train, y_train)

    result = permutation_importance(
        best_rf, X_train, y_train, 
        scoring='r2', 
        n_repeats=10, 
        random_state=42, 
        n_jobs=-1
    )

    rf_r2 = []
    feat_num = []
    
    # Формируем итоговый топ
    verification_df = pd.DataFrame({
        'Feature': X_train.columns,
        'Importance_Mean': result.importances_mean,
        'Importance_Std': result.importances_std
    }).sort_values(by='Importance_Mean', ascending=False)

    for feat_i in range(1,21):
        print(feat_i,end=' ')
        model = RandomForestRegressor(**best_params)
        feats = verification_df['Feature'].iloc[:feat_i]
        model.fit(X_train[feats],y_train)
        val_pred = model.predict(X_val[feats])
        
        rf_r2.append(r2_score(y_val,val_pred))
        feat_num.append(feat_i)


    fig, axes = plt.subplots(
        nrows=1,
        ncols=2,
        figsize=(15, 9),
        layout="constrained",
    )
    ax_rd, ax_pi= axes.flat

    ax_rd.plot(feat_num, rf_r2,'o-')
    ax_pi.set_title('Значение R2 от признаков')
    ax_rd.set_xlabel('Количество признаков')
    ax_rd.set_ylabel('R2')
    ax_rd.set_xticks(feat_num[::1])
    ax_rd.grid()

    ax_pi.barh(verification_df['Feature'].iloc[:10][::-1],verification_df['Importance_Mean'].iloc[:10][::-1])
    ax_pi.set_title('Топ 10 признаков по важности')
    ax_pi.set_xlabel('Важность признаков')

    fig.savefig(dir_config.FEATURES_IMPORTANCE_DIR)

    plt.show()


def main():
    run_selection()


if __name__=='__main__':
    main()