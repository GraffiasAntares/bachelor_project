from bachelor_project import config
from bachelor_project.ingestion import ingestion


def main():
    print("---ТЕСТ ЗАГРУЗКИ ДАННЫХ---")

    ingestion.load_data("2025-01-01", 
                        "2025-01-02",
                        config.TEST_RAW_POLLUTION_DATA_DIR,
                        config.TEST_RAW_METEO_DATA_DIR)

    print("Данные сохранены в директориях: " \
          ,"\n", \
          config.TEST_RAW_POLLUTION_DATA_DIR \
          ,"\n", \
          config.TEST_RAW_METEO_DATA_DIR)


if __name__=="__main__":
    main()