from bachelor_project.configs import dir_config
from bachelor_project.configs import model_config

import json

import mlflow
import pandas as pd
import torch
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from torch import nn
from kan import KAN


class SigmoidKAN(KAN):
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
    
    def __call__(self, x):
        return F.sigmoid(super().__call__(x))


class KDataset(Dataset):
    def __init__(self, data, features, target):
        self.X = torch.tensor(data[features].values, dtype=torch.float32)
        self.y = torch.tensor(data[target].values, dtype=torch.float32)

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]


def load_features_and_target():
    with open(dir_config.SELECTED_FEATURES_DIR, 'r', encoding='utf-8') as f:
        features = json.load(f)['features']
    target = model_config.TARGET

    return features, target


def load_data(path):
    data = pd.read_csv(path).set_index('time')
    return data


def get_dataloader(batch_size=64, shuffle=False):
    train = load_data(dir_config.TRAIN_DATA)
    val = load_data(dir_config.VAL_DATA)
    
    features, target = load_features_and_target()
    
    dataset = KDataset(data=pd.concat([train, val]),
                       features=features,
                       target=target)

    dataloader = DataLoader(dataset=dataset,
                            batch_size=batch_size,
                            shuffle=shuffle)

    return dataloader


def train():
    mlflow.enable_system_metrics_logging()
    mlflow.set_experiment('kan_training')

    epochs   = model_config.KAN_TRAIN_CONFIG['epochs']
    lambd    = model_config.KAN_TRAIN_CONFIG['lambd']
    lr       = model_config.KAN_TRAIN_CONFIG['learning_rate']
    patience = model_config.KAN_TRAIN_CONFIG['scheduler_patience']

    model = SigmoidKAN(width=[len(load_features_and_target()[0]),
                              len(load_features_and_target()[0])//2,
                              1],
                       **model_config.KAN_PARAMS)
    training_dataset = get_dataloader()

    criterion = nn.MSELoss()
    optimizer = torch.optim.LBFGS(model.parameters(), lr=lr, line_search_fn='strong_wolfe')
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=patience)

    with mlflow.start_run():
        mlflow.log_params({
            **model_config.KAN_TRAIN_CONFIG,
            'width': model.width,
            'grid_size': model.grid,
        })
        for epoch in range(epochs):
            model.train()
            for X, y in training_dataset:
                def closure():
                    optimizer.zero_grad()
                    pred = model(X)
                    loss = criterion(pred, y)
                    reg_loss = model.reg('edge_forward_spline_n',1.0,1.0,1.0,1.0)
                    total_loss = loss + lambd * reg_loss
                    total_loss.backward()
                    
                    return total_loss
                
                loss = criterion(model(X),y)
                optimizer.step(closure)
                scheduler.step(loss)

                model_info = mlflow.pytorch.log_model(
                    pytorch_model=model,
                    name=f"checkpoint-{epoch}",
                    step=epoch,
                    input_example=X[:5].numpy(),
                )

                mlflow.log_metric(
                    key="train_RMSE",
                    value=loss**0.5,
                    step=epoch,
                    model_id=model_info.model_id,
                )

        # return model


def main():
    train()


if __name__ == '__main__':
    main()