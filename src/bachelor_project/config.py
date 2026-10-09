from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent.parent

RAW_POLLUTION_DATA_DIR = PROJECT_DIR / "src" / "bachelor_project" / "data" / "raw" / "pollution.csv"
RAW_METEO_DATA_DIR = PROJECT_DIR / "src" / "bachelor_project" / "data" / "raw" / "meteo.csv"

TEST_RAW_POLLUTION_DATA_DIR = PROJECT_DIR / "src" / "bachelor_project" / "data" / "raw" / "test_pollution.csv"
TEST_RAW_METEO_DATA_DIR = PROJECT_DIR / "src" / "bachelor_project" / "data" / "raw" / "test_meteo.csv"


if __name__=="__main__":
    print("PROJECT_DIR:", PROJECT_DIR)

    print("RAW_POLLUTION_DATA_DIR:", RAW_POLLUTION_DATA_DIR)
    print("RAW_METEO_DATA_DIR:", RAW_METEO_DATA_DIR)
    
    print("TEST_RAW_POLLUTION_DATA_DIR:", TEST_RAW_POLLUTION_DATA_DIR)
    print("TEST_RAW_METEO_DATA_DIR:", TEST_RAW_METEO_DATA_DIR)