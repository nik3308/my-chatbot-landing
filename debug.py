#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Скрипт для отладки и проверки работоспособности телеграм бота
"""

import os
import sys
import asyncio
import logging
from dotenv import load_dotenv
from telegram import Bot
from telegram.error import TelegramError

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)

async def check_bot():
    """Проверяет базовую работоспособность бота"""
    
    # 1. Проверка наличия токена
    token = os.environ.get("TELEGRAM_TOKEN")
    if not token:
        logger.error("❌ TELEGRAM_TOKEN не найден в переменных окружения!")
        logger.info("Создайте файл .env и добавьте туда:")
        logger.info("TELEGRAM_TOKEN=ваш_токен_от_BotFather")
        return False
    
    logger.info(f"✅ Токен найден: {token[:5]}...{token[-5:]}")
    
    # 2. Проверка валидности токена
    try:
        bot = Bot(token=token)
        bot_info = await bot.get_me()
        logger.info(f"✅ Бот подключен успешно!")
        logger.info(f"   Имя бота: @{bot_info.username}")
        logger.info(f"   ID бота: {bot_info.id}")
        logger.info(f"   Имя: {bot_info.first_name}")
    except TelegramError as e:
        logger.error(f"❌ Ошибка подключения к Telegram API: {e}")
        logger.info("Проверьте правильность токена!")
        return False
    except Exception as e:
        logger.error(f"❌ Неожиданная ошибка: {e}")
        return False
    
    # 3. Проверка webhook (если на Heroku)
    heroku_app_name = os.environ.get("HEROKU_APP_NAME")
    if heroku_app_name:
        logger.info(f"🌐 Обнаружено имя приложения Heroku: {heroku_app_name}")
        
        try:
            webhook_info = await bot.get_webhook_info()
            expected_url = f"https://{heroku_app_name}.herokuapp.com/{token}"
            
            if webhook_info.url:
                logger.info(f"✅ Webhook установлен: {webhook_info.url}")
                if webhook_info.url != expected_url:
                    logger.warning(f"⚠️  Ожидаемый URL: {expected_url}")
                    logger.warning("   URL webhook отличается от ожидаемого!")
                
                if webhook_info.last_error_message:
                    logger.error(f"❌ Последняя ошибка webhook: {webhook_info.last_error_message}")
                    logger.error(f"   Время ошибки: {webhook_info.last_error_date}")
            else:
                logger.warning("⚠️  Webhook не установлен!")
                logger.info("   Попытка установить webhook...")
                
                try:
                    success = await bot.set_webhook(expected_url)
                    if success:
                        logger.info("✅ Webhook установлен успешно!")
                    else:
                        logger.error("❌ Не удалось установить webhook")
                except Exception as e:
                    logger.error(f"❌ Ошибка при установке webhook: {e}")
                    
        except Exception as e:
            logger.error(f"❌ Ошибка при проверке webhook: {e}")
    else:
        logger.info("🖥️  Режим локальной разработки (polling)")
    
    # 4. Проверка переменных окружения
    logger.info("\n📋 Проверка переменных окружения:")
    
    admin_id = os.environ.get("ADMIN_USER_ID")
    if admin_id:
        logger.info(f"✅ ADMIN_USER_ID: {admin_id}")
    else:
        logger.warning("⚠️  ADMIN_USER_ID не установлен (уведомления администратору не будут отправляться)")
    
    db_url = os.environ.get("DATABASE_URL")
    if db_url:
        logger.info("✅ DATABASE_URL установлен")
    else:
        logger.warning("⚠️  DATABASE_URL не установлен (заявки не будут сохраняться в БД)")
    
    # 5. Проверка импортов
    logger.info("\n📦 Проверка импортов:")
    try:
        import telegram
        logger.info(f"✅ python-telegram-bot версия: {telegram.__version__}")
        
        import psycopg2
        logger.info(f"✅ psycopg2 установлен")
        
        import dotenv
        logger.info(f"✅ python-dotenv установлен")
        
    except ImportError as e:
        logger.error(f"❌ Ошибка импорта: {e}")
        logger.info("   Выполните: pip install -r requirements.txt")
    
    return True

async def test_message():
    """Отправляет тестовое сообщение администратору"""
    token = os.environ.get("TELEGRAM_TOKEN")
    admin_id = os.environ.get("ADMIN_USER_ID")
    
    if not token:
        logger.error("❌ Токен не найден!")
        return
        
    if not admin_id:
        logger.warning("⚠️  ADMIN_USER_ID не установлен, тестовое сообщение не будет отправлено")
        return
    
    try:
        bot = Bot(token=token)
        await bot.send_message(
            chat_id=admin_id,
            text="🤖 Тестовое сообщение от бота!\n\nЕсли вы видите это сообщение, значит бот работает корректно."
        )
        logger.info("✅ Тестовое сообщение отправлено администратору!")
    except Exception as e:
        logger.error(f"❌ Ошибка при отправке тестового сообщения: {e}")
        logger.info("   Проверьте правильность ADMIN_USER_ID")

async def main():
    """Основная функция"""
    logger.info("🔍 Начинаем диагностику бота...\n")
    
    success = await check_bot()
    
    if success:
        logger.info("\n✅ Базовая проверка пройдена успешно!")
        
        # Спрашиваем, отправить ли тестовое сообщение
        if os.environ.get("ADMIN_USER_ID"):
            logger.info("\nХотите отправить тестовое сообщение администратору? (y/n)")
            answer = input().lower()
            if answer == 'y':
                await test_message()
    else:
        logger.error("\n❌ Обнаружены проблемы! Исправьте их перед запуском бота.")
    
    logger.info("\n📝 Рекомендации:")
    logger.info("1. Убедитесь, что файл .env создан и содержит правильные данные")
    logger.info("2. Проверьте, что токен получен от @BotFather")
    logger.info("3. Для получения вашего Telegram ID используйте @userinfobot")
    logger.info("4. При деплое на Heroku убедитесь, что все переменные окружения установлены")

if __name__ == "__main__":
    asyncio.run(main())
