from bachelor_project.config import RAW_TESTING_DATA_DIR
from bachelor_project.ingestion import ingestion


def main():
    print("---ТЕСТ ЗАГРУЗКИ ДАННЫХ---")
    ingestion.load_data("2025-01-01", "2025-01-02", RAW_TESTING_DATA_DIR)
    print("Данные сохранены в директории", RAW_TESTING_DATA_DIR)


if __name__=="__main__":
    main()