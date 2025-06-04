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

# Настройка расширенного логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
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

# Функция для инициализации после запуска
async def post_init(application: Application) -> None:
    """Выполняется после инициализации бота"""
    bot_info = await application.bot.get_me()
    logger.info("=" * 60)
    logger.info(f"✅ БОТ ЗАПУЩЕН УСПЕШНО!")
    logger.info(f"🤖 Имя: {bot_info.first_name}")
    logger.info(f"📱 Username: @{bot_info.username}")
    logger.info(f"🆔 ID: {bot_info.id}")
    logger.info(f"🌐 Режим: {'Webhook' if HEROKU_APP_NAME else 'Polling'}")
    logger.info("=" * 60)

def main() -> None:
    """Запускает бота."""
    logger.info("Начало инициализации бота")
    
    # Создаем приложение с post_init
    logger.info(f"Создаем приложение с токеном: {TOKEN[:5]}...{TOKEN[-5:]}")
    application = Application.builder().token(TOKEN).post_init(post_init).build()
    
    # Добавляем обработчики команд
    logger.info("Регистрируем обработчики команд")
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    
    # Создаем обработчик разговора для сбора заявки
    logger.info("Регистрируем ConversationHandler")
    conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(button_handler, pattern='^request$|^request_package_')
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
        per_message=False,
        persistent=False,
        name="request_conversation"
    )
    application.add_handler(conv_handler)
    
    # Добавляем обработчик для всех остальных кнопок
    logger.info("Регистрируем обработчик CallbackQueryHandler")
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Обработчик для текстовых сообщений (только для тех, что не в ConversationHandler)
    # Важно: этот обработчик должен быть последним!
    logger.info("Регистрируем обработчик текстовых сообщений")
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # Регистрируем обработчик ошибок
    async def error_handler(update, context):
        """Обработчик ошибок с подробным логированием"""
        logger.error(f"Возникла ошибка: {context.error}", exc_info=context.error)
        
        # Логируем детали обновления
        if update:
            if update.effective_user:
                logger.error(f"Пользователь: {update.effective_user.id} (@{update.effective_user.username})")
            if update.effective_message:
                logger.error(f"Сообщение: {update.effective_message.text}")
        
        # Пытаемся ответить пользователю
        if update and update.effective_message:
            try:
                await update.effective_message.reply_text(
                    "Извините, произошла ошибка при обработке вашего запроса. "
                    "Пожалуйста, попробуйте снова или используйте /start"
                )
            except Exception as e:
                logger.error(f"Ошибка при отправке сообщения об ошибке: {e}")
    
    application.add_error_handler(error_handler)
    
    # Запускаем бота
    if HEROKU_APP_NAME:
        logger.info(f"Обнаружена переменная HEROKU_APP_NAME: {HEROKU_APP_NAME}")
        # Формируем URL для webhook
        webhook_url = f"https://{HEROKU_APP_NAME}.herokuapp.com/{TOKEN}"
        logger.info(f"Запуск веб-хука на URL: {webhook_url}")
        
        # Запуск веб-хука для Heroku
        application.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=TOKEN,
            webhook_url=webhook_url,
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True  # Сбрасываем старые обновления
        )
    else:
        # Запуск в режиме polling для локальной разработки
        logger.warning("HEROKU_APP_NAME не установлен, запуск в режиме polling (локальная разработка)")
        application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True  # Сбрасываем старые обновления
        )

if __name__ == '__main__':
    logger.info("Запуск скрипта main.py")
    main()
