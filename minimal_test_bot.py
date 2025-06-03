#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import sys
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG,
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Получение токена и настроек
TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TOKEN:
    logger.error("TELEGRAM_TOKEN не найден в переменных окружения!")
    sys.exit(1)

PORT = int(os.environ.get("PORT", "8443"))
HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME")
ADMIN_USER_ID = os.environ.get("ADMIN_USER_ID")

# Обработчики
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user = update.effective_user
    logger.info(f"Получена команда /start от пользователя {user.id} (@{user.username})")
    
    try:
        await update.message.reply_text(
            "👋 Привет! Я работаю!\n\n"
            "Доступные команды:\n"
            "/start - Начать работу\n"
            "/test - Тестовая команда\n"
            "/info - Информация о боте\n\n"
            "Или просто напиши мне что-нибудь!"
        )
        logger.info(f"Отправлен ответ пользователю {user.id}")
    except Exception as e:
        logger.error(f"Ошибка при отправке ответа: {e}")

async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Тестовая команда"""
    logger.info(f"Получена команда /test от пользователя {update.effective_user.id}")
    await update.message.reply_text("✅ Тестовая команда работает!")

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Информация о боте"""
    logger.info(f"Получена команда /info от пользователя {update.effective_user.id}")
    
    info_text = f"""
ℹ️ <b>Информация о боте</b>

🤖 Имя бота: {context.bot.name}
🆔 ID бота: {context.bot.id}
👤 Username: @{context.bot.username}

🌐 Режим работы: {'Webhook (Heroku)' if HEROKU_APP_NAME else 'Polling (локально)'}
"""
    
    if HEROKU_APP_NAME:
        info_text += f"📍 Приложение: {HEROKU_APP_NAME}\n"
    
    await update.message.reply_html(info_text)

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Эхо-ответ на текстовые сообщения"""
    text = update.message.text
    user = update.effective_user
    logger.info(f"Получено сообщение: '{text}' от пользователя {user.id} (@{user.username})")
    
    response = f"🔄 Вы написали: {text}\n\n💬 Длина сообщения: {len(text)} символов"
    await update.message.reply_text(response)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок"""
    logger.error(f"Произошла ошибка: {context.error}", exc_info=context.error)
    
    # Отправляем уведомление администратору
    if ADMIN_USER_ID:
        try:
            error_message = f"⚠️ Ошибка в боте!\n\n{str(context.error)}"
            await context.bot.send_message(chat_id=ADMIN_USER_ID, text=error_message)
        except:
            pass
    
    # Отправляем сообщение пользователю
    if update and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "😔 Извините, произошла ошибка. Попробуйте еще раз позже."
            )
        except:
            pass

async def post_init(application: Application) -> None:
    """Функция, выполняемая после инициализации бота"""
    bot_info = await application.bot.get_me()
    logger.info(f"✅ Бот запущен успешно!")
    logger.info(f"   Имя: {bot_info.first_name}")
    logger.info(f"   Username: @{bot_info.username}")
    logger.info(f"   ID: {bot_info.id}")
    
    # Отправляем уведомление администратору о запуске
    if ADMIN_USER_ID:
        try:
            await application.bot.send_message(
                chat_id=ADMIN_USER_ID,
                text=f"🚀 Бот @{bot_info.username} запущен успешно!"
            )
        except Exception as e:
            logger.error(f"Не удалось отправить уведомление администратору: {e}")

def main():
    """Запускает бота"""
    logger.info("=" * 50)
    logger.info("Запуск бота...")
    logger.info(f"Токен: {TOKEN[:10]}...{TOKEN[-5:]}")
    logger.info(f"Heroku App: {HEROKU_APP_NAME or 'Не указано (локальный режим)'}")
    logger.info(f"Порт: {PORT}")
    logger.info("=" * 50)
    
    # Создаем приложение
    application = Application.builder().token(TOKEN).post_init(post_init).build()

    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("test", test))
    application.add_handler(CommandHandler("info", info))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    
    # Добавляем обработчик ошибок
    application.add_error_handler(error_handler)
    
    # Запускаем бота
    if HEROKU_APP_NAME:
        # Webhook для Heroku
        webhook_url = f"https://{HEROKU_APP_NAME}.herokuapp.com/{TOKEN}"
        logger.info(f"Запуск в режиме Webhook")
        logger.info(f"Webhook URL: {webhook_url}")
        
        # Запускаем webhook
        application.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=TOKEN,
            webhook_url=webhook_url,
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True  # Сбрасываем старые обновления
        )
    else:
        # Polling для локальной разработки
        logger.info("Запуск в режиме Polling (локальная разработка)")
        application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True  # Сбрасываем старые обновления
        )

if __name__ == "__main__":
    main()
