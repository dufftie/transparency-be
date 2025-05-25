import os


def get_db_address():
    db_config = {
        'host': os.getenv('DB_HOST'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'database': os.getenv('DB_NAME'),
        'sslmode': os.getenv('DB_SSL_MODE', 'require')
    }
    return f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}/{db_config['database']}?sslmode={db_config['sslmode']}"