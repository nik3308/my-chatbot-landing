#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import sys
from telegram import Update
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

# Настройка расширенного логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG,
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Получение токена из переменных окружения
TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TOKEN:
    logger.error("TELEGRAM_TOKEN не найден в переменных окружения!")
    sys.exit(1)

PORT = int(os.environ.get("PORT", "8443"))
HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME")

def main() -> None:
    """Запускает бота."""
    logger.info("Начало инициализации бота")
    
    # Инициализация базы данных
    try:
        initialize_database()
        logger.info("База данных инициализирована успешно")
    except Exception as e:
        logger.error(f"Ошибка при инициализации базы данных: {e}")
        logger.warning("Продолжаем без базы данных")
    
    # Создаем приложение
    logger.info(f"Создаем приложение с токеном: {TOKEN[:5]}...{TOKEN[-5:]}")
    application = Application.builder().token(TOKEN).build()
    
    # Добавляем обработчики команд
    logger.info("Регистрируем обработчики команд")
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    
    # Создаем обработчик разговора для сбора заявки
    logger.info("Регистрируем ConversationHandler")
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
        ],
        per_message=False
    )
    application.add_handler(conv_handler)
    
    # Добавляем обработчик для кнопок (для тех, что не в ConversationHandler)
    logger.info("Регистрируем обработчик CallbackQueryHandler")
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Обработчик для текстовых сообщений вне ConversationHandler
    # Важно: этот обработчик должен быть после ConversationHandler
    logger.info("Регистрируем обработчик текстовых сообщений")
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # Регистрируем обработчик ошибок
    async def error_handler(update, context):
        logger.error(f"Возникла ошибка: {context.error}")
        
        if update and update.effective_message:
            try:
                await update.effective_message.reply_text(
                    "Извините, произошла ошибка при обработке вашего запроса. Пожалуйста, попробуйте снова."
                )
            except Exception as e:
                logger.error(f"Ошибка при отправке сообщения об ошибке: {e}")
    
    application.add_error_handler(error_handler)
    
    # Запускаем бота
    if HEROKU_APP_NAME:
        # Формируем URL для webhook
        webhook_url = f"https://{HEROKU_APP_NAME}.herokuapp.com/{TOKEN}"
        logger.info(f"Запуск веб-хука на URL: {webhook_url}")
        
        # Запуск веб-хука для Heroku
        application.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=TOKEN,
            webhook_url=webhook_url
        )
    else:
        # Запуск в режиме polling для локальной разработки
        logger.info("Запуск в режиме polling (локальная разработка)")
        application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    logger.info("Запуск скрипта main.py")
    main()
