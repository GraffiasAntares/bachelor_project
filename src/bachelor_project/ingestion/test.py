from bachelor_project.configs import dir_config
from bachelor_project.ingestion import ingestion


def main():
    print("---ТЕСТ ЗАГРУЗКИ ДАННЫХ---")

    ingestion.load_data("2025-01-01", 
                        "2025-01-02",
                        dir_config.TEST_RAW_POLLUTION_DATA_DIR,
                        dir_config.TEST_RAW_METEO_DATA_DIR)

    print("Данные сохранены в директориях: " \
          ,"\n", \
          dir_config.TEST_RAW_POLLUTION_DATA_DIR \
          ,"\n", \
          dir_config.TEST_RAW_METEO_DATA_DIR)


if __name__=="__main__":
    main()