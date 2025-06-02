#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    filters, 
    CallbackQueryHandler, 
    ConversationHandler
)
from handlers import (
    start_command,
    help_command,
    handle_text,
    button_handler,
    get_name,
    get_phone,
    cancel,
    NAME,
    PHONE
)
from database import initialize_database

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Получение токена из переменных окружения
TOKEN = os.environ.get("TELEGRAM_TOKEN", "YOUR_TOKEN_HERE")
PORT = int(os.environ.get("PORT", "8443"))
HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME")

def main() -> None:
    """Запускает бота."""
    # Инициализация базы данных
    initialize_database()
    
    # Создаем приложение
    application = Application.builder().token(TOKEN).build()
    
    # Создаем обработчик разговора для сбора заявки
    conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(button_handler, pattern='^request$|^request_package_'),
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text)
        ],
        states={
            NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_name),
                CallbackQueryHandler(cancel, pattern='^cancel_request$')
            ],
            PHONE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone),
                CallbackQueryHandler(cancel, pattern='^cancel_request$')
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel),
            CallbackQueryHandler(cancel, pattern='^cancel_request$')
        ]
    )

    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(conv_handler)
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Обработчик для текстовых сообщений, которые не обрабатываются ConversationHandler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # Запускаем бота
    if HEROKU_APP_NAME:
        # Запуск веб-хука для Heroku
        application.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=TOKEN,
            webhook_url=f"https://{HEROKU_APP_NAME}.herokuapp.com/{TOKEN}"
        )
        logger.info(f"Бот запущен в режиме webhook на Heroku")
    else:
        # Запуск в режиме polling для локальной разработки
        application.run_polling()
        logger.info("Бот запущен в режиме polling")

if __name__ == '__main__':
    main()