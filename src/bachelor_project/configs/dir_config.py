from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent.parent.parent.parent
DATA_DIR = PROJECT_DIR / "src" / "bachelor_project" / "data" 
MODEL_DIR = PROJECT_DIR / "src" / "bachelor_project" / "model" 

RAW_POLLUTION_DATA_DIR = DATA_DIR / "raw" / "pollution.csv"
RAW_METEO_DATA_DIR = DATA_DIR / "raw" / "meteo.csv"

PREP_K_DATA_DIR = DATA_DIR / "preprocessed" / "k_dataset.csv"
PREP_METEO_AND_POLUTTION_DATA_DIR = DATA_DIR / "preprocessed" / "preprocessed_meteo_and_pollution.csv"

FEATURES_DATA_DIR = DATA_DIR / "features" / "features.csv"

SCALER_DIR = MODEL_DIR / "scaler.pkl"

TRAIN_DATA = DATA_DIR / "train" / "train.csv"
VAL_DATA = DATA_DIR / "val" / "val.csv"
TEST_DATA = DATA_DIR / "test" / "test.csv"

TEST_RAW_POLLUTION_DATA_DIR = DATA_DIR / "raw" / "test_pollution.csv"
TEST_RAW_METEO_DATA_DIR = DATA_DIR / "raw" / "test_meteo.csv"

FEATURES_IMPORTANCE_DIR = MODEL_DIR / "features_importance.png"