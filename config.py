import os
from dotenv import load_dotenv

# Загрузка переменных окружения из файла .env
load_dotenv()

# Telegram
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
ADMIN_USER_ID = os.environ.get("ADMIN_USER_ID")  # ID администратора для получения уведомлений о заявках

# Контент с сайта
COMPANY_NAME = "AI-решения"
COMPANY_WEBSITE = "https://nik3308.github.io/lending/"

# Пакеты услуг (из сайта)
PACKAGES = {
    "basic": {
        "name": "Базовый пакет",
        "price": "30,000 руб.",
        "includes": "Простой бот с базовыми функциями",
        "deadline": "7-10 дней"
    },
    "advanced": {
        "name": "Продвинутый пакет",
        "price": "50,000 руб.",
        "includes": "Расширенный функционал, интеграции с API",
        "deadline": "14-20 дней"
    },
    "premium": {
        "name": "Премиум пакет",
        "price": "100,000 руб.",
        "includes": "Полный комплекс услуг, интеграции, аналитика",
        "deadline": "30-40 дней"
    }
}

# Этапы разработки
DEVELOPMENT_STAGES = [
    {
        "name": "Анализ требований",
        "description": "Определяем ваши потребности и цели"
    },
    {
        "name": "Проектирование",
        "description": "Разрабатываем структуру и логику бота"
    },
    {
        "name": "Разработка",
        "description": "Пишем код и создаем функционал"
    },
    {
        "name": "Тестирование",
        "description": "Проверяем работу и исправляем ошибки"
    },
    {
        "name": "Внедрение",
        "description": "Запускаем бота в рабочую среду"
    },
    {
        "name": "Поддержка",
        "description": "Обеспечиваем стабильную работу и обновления"
    }
]