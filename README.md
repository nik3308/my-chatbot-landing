# Telegram Бот для сайта-визитки AI-решения

Этот бот предоставляет информацию о тарифах, услугах и сроках разработки ботов компании "AI-решения", а также собирает заявки от потенциальных клиентов.

## Функционал

- Предоставление информации о пакетах услуг
- Описание этапов разработки ботов
- Сбор контактных данных клиентов
- Уведомление администратора о новых заявках

## Структура проекта

```
telegram_bot/
├── main.py           # Основной файл бота
├── config.py         # Конфигурация (токены, настройки)
├── handlers.py       # Обработчики команд и сообщений
├── keyboards.py      # Клавиатуры и кнопки
├── database.py       # Работа с базой данных
├── content.py        # Контент и тексты сообщений
├── requirements.txt  # Зависимости
├── Procfile          # Файл для Heroku
├── runtime.txt       # Версия Python для Heroku
└── .env.example      # Пример файла с переменными окружения
```

## Установка и настройка

### Локальная разработка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/yourusername/ai-solutions-bot.git
cd ai-solutions-bot
```

2. Создайте виртуальное окружение и установите зависимости:
```bash
python -m venv venv
source venv/bin/activate  # для Linux/Mac
venv\Scripts\activate     # для Windows
pip install -r requirements.txt
```

3. Создайте файл `.env` на основе `.env.example` и заполните его:
```bash
cp .env.example .env
# Отредактируйте файл .env, добавив свои токены и настройки
```

4. Запустите бота:
```bash
python main.py
```

### Деплой на Heroku

1. Установите [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli) и войдите в аккаунт:
```bash
heroku login
```

2. Создайте приложение на Heroku:
```bash
heroku create your-app-name
```

3. Добавьте переменные окружения:
```bash
heroku config:set TELEGRAM_TOKEN=your_telegram_bot_token
heroku config:set ADMIN_USER_ID=your_telegram_user_id
heroku config:set HEROKU_APP_NAME=your-app-name
```

4. Добавьте базу данных PostgreSQL:
```bash
heroku addons:create heroku-postgresql:hobby-dev
```

5. Отправьте код на Heroku:
```bash
git push heroku main
```

## Настройка webhook

Для Telegram бота на Heroku необходимо настроить webhook. Это делается автоматически при запуске бота, если установлена переменная окружения `HEROKU_APP_NAME`.

## Обновление контента

Для обновления информации о пакетах услуг и этапах работы редактируйте файл `config.py`.

## Лицензия

MIT
