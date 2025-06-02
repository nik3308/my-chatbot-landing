import os
import logging
import psycopg2
from datetime import datetime
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def get_connection():
    """Создает соединение с базой данных."""
    # Получаем URL базы данных из переменных окружения
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        logger.warning("DATABASE_URL не найден в переменных окружения")
        return None
    
    # Для Heroku PostgreSQL, необходимо заменить postgresql:// на postgres://
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    try:
        return psycopg2.connect(database_url)
    except Exception as e:
        logger.error(f"Ошибка подключения к базе данных: {e}")
        return None

def initialize_database():
    """Инициализирует базу данных, создавая необходимые таблицы."""
    conn = get_connection()
    if not conn:
        logger.warning("Не удалось подключиться к базе данных для инициализации.")
        return False
    
    try:
        with conn.cursor() as cur:
            # Создание таблицы для хранения заявок
            cur.execute('''
                CREATE TABLE IF NOT EXISTS requests (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    username TEXT,
                    name TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    package TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
            logger.info("База данных успешно инициализирована")
            return True
    except Exception as e:
        logger.error(f"Ошибка при инициализации базы данных: {e}")
        return False
    finally:
        conn.close()

def save_request(user_id, username, name, phone, package=None):
    """Сохраняет заявку в базу данных."""
    conn = get_connection()
    if not conn:
        logger.warning("Не удалось подключиться к базе данных для сохранения заявки.")
        return False
    
    try:
        with conn.cursor() as cur:
            cur.execute(
                '''
                INSERT INTO requests (user_id, username, name, phone, package)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
                ''',
                (user_id, username, name, phone, package)
            )
            request_id = cur.fetchone()[0]
            conn.commit()
            logger.info(f"Заявка успешно сохранена с ID: {request_id}")
            return request_id
    except Exception as e:
        logger.error(f"Ошибка при сохранении заявки: {e}")
        return False
    finally:
        conn.close()

def get_all_requests():
    """Получает все заявки из базы данных."""
    conn = get_connection()
    if not conn:
        logger.warning("Не удалось подключиться к базе данных для получения заявок.")
        return []
    
    try:
        with conn.cursor() as cur:
            cur.execute('SELECT * FROM requests ORDER BY created_at DESC')
            return cur.fetchall()
    except Exception as e:
        logger.error(f"Ошибка при получении заявок: {e}")
        return []
    finally:
        conn.close()

# Инициализация базы данных при импорте модуля
if __name__ != "__main__":
    try:
        initialize_database()
    except Exception as e:
        logger.error(f"Ошибка при автоматической инициализации базы данных: {e}")
