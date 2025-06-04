import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# Импорт наших модулей
from models import create_tables
from database_service import DatabaseService

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Получение токена из переменных окружения
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в переменных окружения")

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Состояния для FSM
class ContactForm(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()

# Данные о пакетах услуг
PACKAGES_DATA = {
    "basic": {
        "name": "Базовый пакет",
        "price": "85 000₽",
        "description": "Простой бот для приема заявок",
        "features": [
            "✅ Базовые сценарии диалогов",
            "✅ Простое меню навигации", 
            "✅ Сбор контактных данных",
            "✅ Передача заявок менеджеру"
        ],
        "timeline": "7 рабочих дней"
    },
    "advanced": {
        "name": "Продвинутый пакет", 
        "price": "150 000₽",
        "description": "Умный бот с ИИ и интеграциями",
        "features": [
            "✅ ИИ-консультант с обучением",
            "✅ Интеграция с CRM системами",
            "✅ Расширенная аналитика",
            "✅ Автоматическая квалификация лидов"
        ],
        "timeline": "7-10 рабочих дней"
    },
    "premium": {
        "name": "Премиум-пакет",
        "price": "250 000₽", 
        "description": "Комплексное решение с автоматизацией",
        "features": [
            "✅ Полная автоматизация процессов",
            "✅ Множественные интеграции",
            "✅ Админ-панель управления",
            "✅ Расширенная поддержка 2 месяца"
        ],
        "timeline": "10-14 рабочих дней"
    }
}

# Этапы разработки
DEVELOPMENT_STAGES = [
    "1️⃣ **Анализ (1-2 дня)**: Изучаем ваши процессы, клиентов и цели. Составляем сценарии диалогов.",
    "2️⃣ **Разработка (3-4 дня)**: Программируем логику, настраиваем интеграции с вашими системами.",
    "3️⃣ **Тестирование (1-2 дня)**: Проверяем все сценарии, обучаем бота правильным ответам.",
    "4️⃣ **Запуск (1 день)**: Запускаем бота, обучаем вашу команду работе с системой."
]

def get_main_menu():
    """Создает главное меню бота"""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="📦 Пакеты услуг", callback_data="packages"))
    builder.add(InlineKeyboardButton(text="🔧 Этапы разработки", callback_data="stages"))
    builder.add(InlineKeyboardButton(text="📝 Оставить заявку", callback_data="contact"))
    builder.adjust(1)
    return builder.as_markup()

def get_packages_menu():
    """Создает меню выбора пакетов"""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="💫 Базовый", callback_data="package_basic"))
    builder.add(InlineKeyboardButton(text="⭐ Продвинутый", callback_data="package_advanced"))
    builder.add(InlineKeyboardButton(text="💎 Премиум", callback_data="package_premium"))
    builder.add(InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main"))
    builder.adjust(1)
    return builder.as_markup()

def get_back_menu():
    """Создает меню с кнопкой назад"""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🔙 Главное меню", callback_data="back_to_main"))
    return builder.as_markup()

def get_contact_menu():
    """Создает меню для раздела заявки"""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="📞 Оставить контакт", callback_data="start_contact"))
    builder.add(InlineKeyboardButton(text="🔙 Главное меню", callback_data="back_to_main"))
    builder.adjust(1)
    return builder.as_markup()

async def register_user(message_or_callback):
    """Регистрирует или обновляет пользователя в базе данных"""
    user = message_or_callback.from_user
    DatabaseService.get_or_create_user(
        telegram_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name
    )

@dp.message(CommandStart())
async def start_handler(message: types.Message):
    """Обработчик команды /start"""
    # Регистрируем пользователя
    await register_user(message)
    
    # Логируем действие
    DatabaseService.log_user_action(
        telegram_id=message.from_user.id,
        action="start"
    )
    
    welcome_text = (
        "🤖 Привет! Я автоматизированный помощник компании **\"AI-решения\"**!\n\n"
        "Помогу вам:\n"
        "• 📋 Узнать о наших пакетах услуг по созданию чат-ботов\n"
        "• 🔧 Понять этапы разработки\n"
        "• 💰 Определить стоимость вашего проекта\n"
        "• 📞 Связаться с нашим менеджером\n\n"
        "**Что вас интересует?** 👇"
    )
    
    await message.answer(
        welcome_text,
        reply_markup=get_main_menu(),
        parse_mode="Markdown"
    )

@dp.callback_query(F.data == "back_to_main")
async def back_to_main(callback: types.CallbackQuery):
    """Возврат в главное меню"""
    await register_user(callback)
    
    welcome_text = (
        "🤖 **Главное меню**\n\n"
        "Выберите интересующий вас раздел:"
    )
    
    await callback.message.edit_text(
        welcome_text,
        reply_markup=get_main_menu(),
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data == "packages") 
async def show_packages(callback: types.CallbackQuery):
    """Показывает пакеты услуг"""
    await register_user(callback)
    
    # Логируем просмотр пакетов
    DatabaseService.log_user_action(
        telegram_id=callback.from_user.id,
        action="view_packages"
    )
    
    packages_text = (
        "📦 **Наши пакеты услуг**\n\n"
        "Выберите оптимальный пакет для вашего бизнеса.\n"
        "Все боты окупаются за 1-3 месяца! 💰\n\n"
        "**Какой пакет вас интересует?**"
    )
    
    await callback.message.edit_text(
        packages_text,
        reply_markup=get_packages_menu(),
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("package_"))
async def show_package_details(callback: types.CallbackQuery):
    """Показывает детали конкретного пакета"""
    await register_user(callback)
    
    package_type = callback.data.replace("package_", "")
    package = PACKAGES_DATA.get(package_type)
    
    if not package:
        await callback.answer("Пакет не найден", show_alert=True)
        return
    
    # Логируем просмотр конкретного пакета
    DatabaseService.log_user_action(
        telegram_id=callback.from_user.id,
        action="view_package_details",
        data={"package": package_type}
    )
    
    features_text = "\n".join(package["features"])
    
    package_text = (
        f"💼 **{package['name']}**\n\n"
        f"💰 **Стоимость**: {package['price']}\n"
        f"⏱ **Срок разработки**: {package['timeline']}\n\n"
        f"**Что входит:**\n{features_text}\n\n"
        f"📝 {package['description']}\n\n"
        f"**Хотите узнать больше или оставить заявку?**"
    )
    
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="📝 Оставить заявку", callback_data=f"contact_package_{package_type}"))
    builder.add(InlineKeyboardButton(text="📦 Другие пакеты", callback_data="packages"))
    builder.add(InlineKeyboardButton(text="🔙 Главное меню", callback_data="back_to_main"))
    builder.adjust(1)
    
    await callback.message.edit_text(
        package_text,
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data == "stages")
async def show_stages(callback: types.CallbackQuery):
    """Показывает этапы разработки"""
    await register_user(callback)
    
    # Логируем просмотр этапов
    DatabaseService.log_user_action(
        telegram_id=callback.from_user.id,
        action="view_stages"
    )
    
    stages_text = (
        "🔧 **Этапы разработки чат-бота**\n\n"
        "**Стандартный срок разработки — 7 рабочих дней** ⚡\n\n"
    )
    
    stages_text += "\n\n".join(DEVELOPMENT_STAGES)
    
    stages_text += (
        "\n\n✨ **От идеи до работающего бота — всего неделя!**\n"
        "💎 Консультация и расчет стоимости — **бесплатно**"
    )
    
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="📦 Посмотреть пакеты", callback_data="packages"))
    builder.add(InlineKeyboardButton(text="📝 Оставить заявку", callback_data="contact"))
    builder.add(InlineKeyboardButton(text="🔙 Главное меню", callback_data="back_to_main"))
    builder.adjust(1)
    
    await callback.message.edit_text(
        stages_text,
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data == "contact")
async def show_contact_info(callback: types.CallbackQuery):
    """Показывает информацию о заявке"""
    await register_user(callback)
    await handle_contact_request(callback, package_interest=None)

@dp.callback_query(F.data.startswith("contact_package_"))
async def show_contact_info_with_package(callback: types.CallbackQuery):
    """Показывает информацию о заявке с предвыбранным пакетом"""
    await register_user(callback)
    package_type = callback.data.replace("contact_package_", "")
    await handle_contact_request(callback, package_interest=package_type)

async def handle_contact_request(callback: types.CallbackQuery, package_interest: str = None):
    """Обрабатывает запрос на оставление заявки"""
    telegram_id = callback.from_user.id
    
    # Проверяем, подавал ли пользователь уже заявку
    has_application = DatabaseService.has_user_submitted_application(telegram_id)
    
    if has_application:
        contact_text = (
            "📋 **У вас уже есть активная заявка!**\n\n"
            "Наш менеджер обязательно с вами свяжется.\n"
            "Если хотите обновить данные или уточнить детали, "
            "можете оставить новую заявку.\n\n"
            "**Оставить новую заявку?**"
        )
    else:
        contact_text = (
            "📝 **Оставить заявку**\n\n"
            "Для оформления заявки нам понадобятся ваши контактные данные.\n"
            "Наш менеджер свяжется с вами в рабочее время для:\n\n"
            "• 💰 Расчета точной стоимости проекта\n"
            "• 📋 Обсуждения технических деталей\n"
            "• ⏱ Согласования сроков разработки\n"
            "• 🎯 Составления индивидуального предложения\n\n"
        )
        
        if package_interest:
            package_name = PACKAGES_DATA.get(package_interest, {}).get("name", "")
            contact_text += f"📦 **Интересующий пакет**: {package_name}\n\n"
        
        contact_text += "**Готовы оставить контакт?**"
    
    # Сохраняем интерес к пакету в состоянии
    if package_interest:
        await callback.message.bot.session.close()  # Закрываем сессию перед сохранением
        DatabaseService.save_dialog_state(
            telegram_id=telegram_id,
            state="package_interest",
            data={"package": package_interest}
        )
    
    builder = InlineKeyboardBuilder()
    button_text = "📞 Обновить контакт" if has_application else "📞 Оставить контакт"
    builder.add(InlineKeyboardButton(text=button_text, callback_data="start_contact"))
    builder.add(InlineKeyboardButton(text="🔙 Главное меню", callback_data="back_to