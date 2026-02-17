# config.py

class Config:
    # Настройки подключения к PostgreSQL
    DB_HOST = "localhost"
    DB_NAME = "research_portfolio"
    DB_USER = "postgres"
    DB_PASSWORD = "postgres"  # Измените на ваш пароль!
    DB_PORT = "5432"

    # Пути к файлам
    MD_FOLDER = "portfolio_md"
    REPORTS_FOLDER = "reports"

    # Подключение без указания кодировки (psycopg2 сам определит)
    @classmethod
    def get_db_connection_string(cls):
        return f"host={cls.DB_HOST} dbname={cls.DB_NAME} user={cls.DB_USER} password={cls.DB_PASSWORD} port={cls.DB_PORT}"

    @classmethod
    def get_db_params(cls):
        return {
            'host': cls.DB_HOST,
            'database': cls.DB_NAME,
            'user': cls.DB_USER,
            'password': cls.DB_PASSWORD,
            'port': cls.DB_PORT
        }