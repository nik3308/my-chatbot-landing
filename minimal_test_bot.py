#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Получение токена и настроек
TOKEN = os.environ.get("TELEGRAM_TOKEN")
PORT = int(os.environ.get("PORT", "8443"))
HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME")

# Обработчики
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    logger.info(f"Получена команда /start от пользователя {update.effective_user.id}")
    await update.message.reply_text("👋 Привет! Я работаю! Напиши мне что-нибудь.")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Эхо-ответ на текстовые сообщения"""
    logger.info(f"Получено сообщение: '{update.message.text}' от пользователя {update.effective_user.id}")
    await update.message.reply_text(f"Вы написали: {update.message.text}")

def main():
    """Запускает бота"""
    # Создаем приложение
    app = Application.builder().token(TOKEN).build()

    # Добавляем обработчики
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Обработчик ошибок
    async def error_handler(update, context):
        logger.error(f"Ошибка: {context.error}")
    
    app.add_error_handler(error_handler)
    
    # Запускаем бота
    if HEROKU_APP_NAME:
        # Используем простой путь "webhook"
        webhook_url = f"https://{HEROKU_APP_NAME}.herokuapp.com/webhook"
        logger.info(f"Запуск webhook на URL: {webhook_url}")
        app.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path="webhook",  # Простой путь
            webhook_url=webhook_url
        )
    else:
        logger.info("Запуск в режиме polling")
        app.run_polling()

if __name__ == "__main__":
    main()
