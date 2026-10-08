from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent.parent

RAW_DATA_DIR = PROJECT_DIR / "src" / "bachelor_project" / "data" / "raw" / "meteo_and_pollution.csv"
RAW_TESTING_DATA_DIR = PROJECT_DIR / "src" / "bachelor_project" / "data" / "raw" / "test.csv"


if __name__=="__main__":
    print("PROJECT_DIR:", PROJECT_DIR)
    print("RAW_DATA_DIR:", RAW_DATA_DIR)
    print("RAW_TESTING_DATA_DIR:", RAW_DATA_DIR)