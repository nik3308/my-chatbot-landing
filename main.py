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

# Получение конфигурации из переменных окружения
BOT_TOKEN = os.getenv('BOT_TOKEN')
COMPANY_NAME = os.getenv('COMPANY_NAME', 'AI-решения')
MANAGER_PHONE = os.getenv('MANAGER_PHONE', '+7 (981) 685-36-38')
MANAGER_EMAIL_CONTACT = os.getenv('MANAGER_EMAIL_CONTACT', 'info@ai-solutions.ru')
WORK_HOURS = os.getenv('WORK_HOURS', 'ПН-ПТ с 9:00 до 18:00 МСК')
TELEGRAM_MANAGER = os.getenv('TELEGRAM_MANAGER', '@yourusername')

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в переменных окружения")

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Инициализация сервиса уведомлений
try:
    from notification_service import NotificationService
    notification_service = NotificationService()
    NOTIFICATIONS_AVAILABLE = True
    print("✅ Сервис уведомлений подключен")
except ImportError:
    print("⚠️ Сервис уведомлений недоступен - используем заглушку")
    NOTIFICATIONS_AVAILABLE = False
    
    class MockNotificationService:
        async def send_all_notifications(self, data):
            print(f"🔔 [MOCK] Уведомление: Новая заявка #{data['id']} - {data['name']}")
            return {"telegram": False, "email": False}
        
        async def send_daily_report(self):
            print("📊 [MOCK] Ежедневный отчет")
            return False
    
    notification_service = MockNotificationService()

# Состояния для FSM
class ContactForm(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()

class AdminCommands(StatesGroup):
    waiting_for_broadcast_message = State()

# Данные о пакетах услуг - ОБНОВЛЕНО
PACKAGES_DATA = {
    "start": {
        "name": "🚀 Старт",
        "price": "20 000₽",
        "description": "Базовый бот для приема заявок и консультаций",
        "features": [
            "✅ Сбор контактных данных клиентов",
            "✅ Простое меню навигации",
            "✅ Передача заявок менеджеру",
            "✅ Базовые сценарии диалогов",
            "✅ Подходит для стартапов и малого бизнеса"
        ],
        "timeline": "3-5 рабочих дней"
    },
    "business": {
        "name": "💼 Бизнес",
        "price": "50 000₽",
        "description": "Бот с расширенным функционалом для растущего бизнеса",
        "features": [
            "✅ Квалификация заявок",
            "✅ Консультации по товарам и услугам",
            "✅ Интеграция с CRM (AmoCRM, Битрикс24)",
            "✅ Базовая аналитика и отчеты",
            "✅ Автоматические уведомления"
        ],
        "timeline": "5-7 рабочих дней"
    },
    "professional": {
        "name": "⭐ Профи",
        "price": "100 000₽",
        "description": "Умный бот с ИИ и полной автоматизацией",
        "features": [
            "✅ ИИ-консультант с обучением на ваших данных",
            "✅ Множественные интеграции (CRM, календари, оплата)",
            "✅ Система онлайн-записи с календарем",
            "✅ Расширенная аналитика и отчеты",
            "✅ Автоматические напоминания клиентам",
            "✅ Программа лояльности"
        ],
        "timeline": "7-10 рабочих дней"
    },
    "corporate": {
        "name": "💎 Корпоративный",
        "price": "150 000₽",
        "description": "Комплексное решение для крупного бизнеса",
        "features": [
            "✅ Полная автоматизация всех процессов",
            "✅ Интеграция со всеми корпоративными системами",
            "✅ Админ-панель с детальными отчетами",
            "✅ Многоуровневая программа лояльности",
            "✅ Расширенная поддержка 3 месяца",
            "✅ Приоритетная техподдержка 24/7",
            "✅ Обучение команды работе с системой"
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
    builder.add(InlineKeyboardButton(text="📝 Быстрая заявка", callback_data="quick_contact"))
    builder.add(InlineKeyboardButton(text="👨‍💻 Связь с менеджером", callback_data="manager_contact"))
    builder.add(InlineKeyboardButton(text="💼 О компании", callback_data="about"))
    builder.adjust(1)
    return builder.as_markup()

def get_packages_menu():
    """Создает меню выбора пакетов"""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🚀 Старт (20 000₽)", callback_data="package_start"))
    builder.add(InlineKeyboardButton(text="💼 Бизнес (50 000₽)", callback_data="package_business"))
    builder.add(InlineKeyboardButton(text="⭐ Профи (100 000₽)", callback_data="package_professional"))
    builder.add(InlineKeyboardButton(text="💎 Корпоративный (150 000₽)", callback_data="package_corporate"))
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

def is_admin_chat(chat_id: int) -> bool:
    """Проверяет, является ли чат админским"""
    admin_chat_id = os.getenv('ADMIN_CHAT_ID')
    return admin_chat_id and str(chat_id) == admin_chat_id

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
    await register_user(message)
    
    DatabaseService.log_user_action(
        telegram_id=message.from_user.id,
        action="start"
    )
    
    user_name = message.from_user.first_name or "друг"
    welcome_text = (
        f"👋 Привет, {user_name}! Добро пожаловать в **{COMPANY_NAME}**!\n\n"
        
        "🤖 **Я помогу вам:**\n"
        "• Узнать о пакетах разработки ботов\n"
        "• Рассчитать стоимость вашего проекта\n"
        "• Понять этапы создания бота\n"
        "• Соединить с нашим менеджером\n\n"
        
        "💡 **Консультация и расчет стоимости — бесплатно!**\n\n"
        
        "🎯 **Что вас интересует?**"
    )
    
    await message.answer(
        welcome_text,
        reply_markup=get_main_menu(),
        parse_mode="Markdown"
    )

@dp.message(Command("getchatid"))
async def get_chat_id(message: types.Message):
    """Получает chat.id для настройки уведомлений"""
    chat_info = (
        f"📋 **Информация о чате:**\n\n"
        f"🆔 **Chat ID**: `{message.chat.id}`\n"
        f"📝 **Название**: {message.chat.title or 'Личный чат'}\n"
        f"👥 **Тип**: {message.chat.type}\n"
        f"👤 **Ваш ID**: `{message.from_user.id}`\n\n"
        f"🔧 **Для настройки уведомлений используйте:**\n"
        f"`export ADMIN_CHAT_ID=\"{message.chat.id}\"`"
    )
    
    await message.answer(chat_info, parse_mode="Markdown")
    logging.info(f"CHAT INFO: ID={message.chat.id}, Type={message.chat.type}, Title={message.chat.title}")

# Админские команды
@dp.message(Command("admin"))
async def admin_commands(message: types.Message):
    """Админские команды (только для админ чата)"""
    if is_admin_chat(message.chat.id):
        admin_text = (
            "🔧 **АДМИНСКИЕ КОМАНДЫ**\n\n"
            "/stats - Статистика заявок\n"
            "/report - Отчет за сегодня\n"
            "/getchatid - Получить ID чата\n"
            "/test - Тест уведомлений\n\n"
            "🔗 Веб-админка доступна по IP сервера"
        )
        await message.answer(admin_text, parse_mode="Markdown")

@dp.message(Command("stats"))
async def admin_stats(message: types.Message):
    """Статистика для админа"""
    if is_admin_chat(message.chat.id):
        try:
            total_apps = DatabaseService.get_applications_count()
            recent_apps = DatabaseService.get_recent_applications(limit=10)
            
            package_stats = {'start': 0, 'business': 0, 'professional': 0, 'corporate': 0, 'none': 0}
            for app in recent_apps:
                if app.package_interest:
                    package_stats[app.package_interest] = package_stats.get(app.package_interest, 0) + 1
                else:
                    package_stats['none'] += 1
            
            stats_text = (
                f"📊 **СТАТИСТИКА БОТА**\n\n"
                f"📋 **Всего заявок**: {total_apps}\n\n"
                f"📦 **По пакетам**:\n"
                f"• Старт: {package_stats['start']}\n"
                f"• Бизнес: {package_stats['business']}\n"
                f"• Профи: {package_stats['professional']}\n"
                f"• Корпоративный: {package_stats['corporate']}\n"
                f"• Без пакета: {package_stats['none']}\n\n"
                f"🔔 **Уведомления**: {'✅ Включены' if NOTIFICATIONS_AVAILABLE else '❌ Отключены'}"
            )
            
            await message.answer(stats_text, parse_mode="Markdown")
        except Exception as e:
            await message.answer(f"❌ Ошибка получения статистики: {e}")

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

@dp.callback_query(F.data == "manager_contact")
async def show_manager_contact(callback: types.CallbackQuery):
    """Показывает контакты менеджера"""
    await register_user(callback)
    
    DatabaseService.log_user_action(
        telegram_id=callback.from_user.id,
        action="view_manager_contact"
    )
    
    contact_text = (
        f"👨‍💻 **ПРЯМАЯ СВЯЗЬ С МЕНЕДЖЕРОМ**\n\n"
        
        f"📱 **Telegram**: {TELEGRAM_MANAGER}\n"
        f"📞 **Телефон**: {MANAGER_PHONE}\n"
        f"📧 **Email**: {MANAGER_EMAIL_CONTACT}\n\n"
        
        f"⏰ **Рабочее время**: {WORK_HOURS}\n\n"
        
        "🚀 **При обращении напишите:**\n"
        "• Что вас интересует (пакет, функционал)\n"
        "• Ваша сфера деятельности\n"
        "• Примерный бюджет\n\n"
        
        "⚡ **Ответим в течение 1 часа в рабочее время!**"
    )
    
    builder = InlineKeyboardBuilder()
    manager_username = TELEGRAM_MANAGER.replace('@', '')
    builder.add(InlineKeyboardButton(text=f"💬 Написать {TELEGRAM_MANAGER}", url=f"https://t.me/{manager_username}"))
    builder.add(InlineKeyboardButton(text="📝 Оставить заявку через бота", callback_data="quick_contact"))
    builder.add(InlineKeyboardButton(text="🔙 Главное меню", callback_data="back_to_main"))
    builder.adjust(1)
    
    await callback.message.edit_text(
        contact_text,
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data == "quick_contact")
async def show_quick_contact(callback: types.CallbackQuery):
    """Быстрая заявка"""
    await register_user(callback)
    await handle_contact_request(callback, package_interest=None)

@dp.callback_query(F.data == "about")
async def show_about(callback: types.CallbackQuery):
    """О компании"""
    await register_user(callback)
    
    DatabaseService.log_user_action(
        telegram_id=callback.from_user.id,
        action="view_about"
    )
    
    about_text = (
        f"💼 **О КОМПАНИИ {COMPANY_NAME.upper()}**\n\n"
        
        "🎯 **Наша специализация:**\n"
        "• Разработка Telegram-ботов любой сложности\n"
        "• Интеграция с CRM, базами данных, API\n"
        "• ИИ-консультанты и чат-боты\n"
        "• Автоматизация бизнес-процессов\n\n"
        
        "📊 **Наши показатели:**\n"
        "• 50+ успешных проектов\n"
        "• Средняя окупаемость бота: 1-3 месяца\n"
        "• Поддержка 24/7\n"
        "• 100% выполнение в срок\n\n"
        
        "🛠 **Технологии:**\n"
        "• Python, aiogram, FastAPI\n"
        "• PostgreSQL, MongoDB\n"
        "• OpenAI GPT, Claude, Gemini\n"
        "• Docker, VPS\n\n"
        
        "✨ **Почему выбирают нас:**\n"
        "• Бесплатная консультация\n"
        "• Фиксированная стоимость\n"
        "• Гарантия на все работы\n"
        "• Обучение вашей команды"
    )
    
    await callback.message.edit_text(
        about_text,
        reply_markup=get_back_menu(),
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data == "packages") 
async def show_packages(callback: types.CallbackQuery):
    """Показывает пакеты услуг"""
    await register_user(callback)
    
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
    builder.add(InlineKeyboardButton(text="💬 Связаться напрямую", callback_data="manager_contact"))
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
    builder.add(InlineKeyboardButton(text="📝 Оставить заявку", callback_data="quick_contact"))
    builder.add(InlineKeyboardButton(text="💬 Связаться напрямую", callback_data="manager_contact"))
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
    
    has_application = DatabaseService.has_user_submitted_application(telegram_id)
    
    if has_application:
        contact_text = (
            "📋 **У вас уже есть активная заявка!**\n\n"
            "Наш менеджер обязательно с вами свяжется в рабочее время.\n"
            "Если хотите обновить данные или уточнить детали, "
            "можете оставить новую заявку.\n\n"
            f"⏰ **Рабочее время**: {WORK_HOURS}\n\n"
            "**Хотите оставить новую заявку?**"
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
        
        contact_text += f"⏰ **Рабочее время**: {WORK_HOURS}\n\n**Готовы оставить контакт?**"
    
    if package_interest:
        DatabaseService.save_dialog_state(
            telegram_id=telegram_id,
            state="package_interest",
            data={"package": package_interest}
        )
    
    builder = InlineKeyboardBuilder()
    button_text = "📞 Обновить контакт" if has_application else "📞 Оставить контакт"
    builder.add(InlineKeyboardButton(text=button_text, callback_data="start_contact"))
    builder.add(InlineKeyboardButton(text="💬 Связаться напрямую", callback_data="manager_contact"))
    builder.add(InlineKeyboardButton(text="🔙 Главное меню", callback_data="back_to_main"))
    builder.adjust(1)
    
    await callback.message.edit_text(
        contact_text,
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data == "start_contact")
async def start_contact_collection(callback: types.CallbackQuery, state: FSMContext):
    """Начинает сбор контактных данных"""
    await register_user(callback)
    
    DatabaseService.log_user_action(
        telegram_id=callback.from_user.id,
        action="start_contact_form"
    )
    
    await state.set_state(ContactForm.waiting_for_name)
    
    contact_text = (
        "👤 **Как к вам обращаться?**\n\n"
        "Напишите ваше имя:"
    )
    
    await callback.message.edit_text(
        contact_text,
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.message(ContactForm.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    """Обрабатывает ввод имени"""
    await register_user(message)
    
    name = message.text.strip() if message.text else ""
    
    if len(name) < 2:
        await message.answer(
            "😊 Пожалуйста, введите корректное имя (не менее 2 символов):"
        )
        return
    
    await state.update_data(name=name)
    await state.set_state(ContactForm.waiting_for_phone)
    
    phone_text = (
        f"📞 **Отлично, {name}!**\n\n"
        "Теперь укажите ваш номер телефона:\n"
        "Например: +7 (999) 123-45-67"
    )
    
    await message.answer(phone_text, parse_mode="Markdown")

@dp.message(ContactForm.waiting_for_phone)
async def process_phone(message: types.Message, state: FSMContext):
    """Обрабатывает ввод телефона"""
    await register_user(message)
    
    phone = message.text.strip() if message.text else ""
    
    if len(phone) < 10 or not any(char.isdigit() for char in phone):
        await message.answer(
            "📞 Пожалуйста, введите корректный номер телефона.\n"
            "Например: +7 (999) 123-45-67 или 89991234567"
        )
        return
    
    data = await state.get_data()
    name = data.get("name")
    telegram_id = message.from_user.id
    
    dialog_state, dialog_data = DatabaseService.get_dialog_state(telegram_id)
    package_interest = dialog_data.get("package") if dialog_data else None
    
    try:
        application = DatabaseService.create_application(
            telegram_id=telegram_id,
            name=name,
            phone=phone,
            package_interest=package_interest
        )
        
        DatabaseService.update_user_contact_data(telegram_id, name, phone)
        
        DatabaseService.log_user_action(
            telegram_id=telegram_id,
            action="submit_application",
            data={
                "application_id": application.id,
                "name": name,
                "phone": phone,
                "package_interest": package_interest
            }
        )
        
        application_data = {
            'id': application.id,
            'name': name,
            'phone': phone,
            'package_interest': package_interest,
            'user_id': telegram_id,
            'created_at': application.created_at.strftime('%d.%m.%Y %H:%M')
        }
        
        asyncio.create_task(notification_service.send_all_notifications(application_data))
        
        DatabaseService.clear_dialog_state(telegram_id)
        
        success_text = (
            f"✅ **Спасибо, {name}!**\n\n"
            "Ваша заявка принята! 🎉\n\n"
            f"📋 **Ваши данные:**\n"
            f"👤 Имя: {name}\n"
            f"📞 Телефон: {phone}\n"
        )
        
        if package_interest:
            package_name = PACKAGES_DATA.get(package_interest, {}).get("name", "")
            success_text += f"📦 Интересующий пакет: {package_name}\n"
        
        success_text += (
            f"\n🆔 **Номер заявки**: #{application.id}\n\n"
            f"💼 Наш менеджер свяжется с вами в рабочее время "
            f"для обсуждения вашего проекта.\n\n"
            f"⏰ **Рабочее время**: {WORK_HOURS}\n\n"
            f"📞 **Экстренная связь**: {MANAGER_PHONE}\n"
            f"📧 **Email**: {MANAGER_EMAIL_CONTACT}\n\n"
            f"🚀 **Следующие шаги**:\n"
            f"• Менеджер изучит ваш запрос\n"
            f"• Подготовит персональное предложение\n"
            f"• Свяжется для уточнения деталей\n"
            f"• Составит план разработки"
        )
        
        logging.info(
            f"🆕 НОВАЯ ЗАЯВКА #{application.id}\n"
            f"👤 Имя: {name}\n"
            f"📞 Телефон: {phone}\n"
            f"📦 Пакет: {package_interest or 'не указан'}\n"
            f"🆔 Telegram ID: {telegram_id}\n"
            f"⏰ Время: {application.created_at}"
        )
        
    except Exception as e:
        logging.error(f"Ошибка при сохранении заявки: {e}")
        success_text = (
            f"❌ **Извините, {name}!**\n\n"
            "Произошла ошибка при сохранении заявки.\n"
            "Пожалуйста, попробуйте позже или свяжитесь с нами напрямую.\n\n"
            f"📞 **Контакты для связи:**\n"
            f"• Телефон: {MANAGER_PHONE}\n"
            f"• Email: {MANAGER_EMAIL_CONTACT}\n\n"
            f"⏰ **Рабочее время**: {WORK_HOURS}"
        )
    
    await message.answer(
        success_text,
        reply_markup=get_back_menu(),
        parse_mode="Markdown"
    )
    
    await state.clear()

@dp.message()
async def universal_message_handler(message: types.Message):
    """Универсальный обработчик сообщений"""
    await register_user(message)
    
    logging.info(f"MESSAGE: Chat={message.chat.id}, User={message.from_user.id}, Text='{message.text[:50] if message.text else 'No text'}...'")
    
    if message.chat.type in ['group', 'supergroup'] and message.text and 'debug' in message.text.lower():
        debug_info = (
            f"🐛 **DEBUG INFO:**\n"
            f"Chat ID: `{message.chat.id}`\n"
            f"User ID: `{message.from_user.id}`\n"
            f"Message ID: {message.message_id}\n"
            f"Chat Type: {message.chat.type}\n"
            f"Admin Chat: {'✅' if is_admin_chat(message.chat.id) else '❌'}"
        )
        await message.answer(debug_info, parse_mode="Markdown")
        return
    
    if message.chat.type == 'private':
        DatabaseService.log_user_action(
            telegram_id=message.from_user.id,
            action="unknown_message",
            data={"text": (message.text or "")[:100]}
        )
        
        unknown_text = (
            "🤔 Извините, я не понимаю эту команду.\n\n"
            "Я могу помочь вам:\n"
            "• 📦 Узнать о пакетах услуг\n"
            "• 🔧 Изучить этапы разработки\n" 
            "• 📝 Оставить заявку на разработку бота\n"
            "• 💬 Связаться с менеджером напрямую\n\n"
            "**Выберите нужный раздел:**"
        )
        
        await message.answer(
            unknown_text,
            reply_markup=get_main_menu(),
            parse_mode="Markdown"
        )

async def main():
    """Основная функция запуска бота"""
    print("🤖 Инициализация базы данных...")
    
    try:
        create_tables()
        print("✅ База данных инициализирована")
        
        await bot.delete_webhook(drop_pending_updates=True)
        print("✅ Webhook удален, переключаемся на polling")
        
        print(f"🤖 Бот для {COMPANY_NAME} запущен и готов к работе!")
        print("📊 Статистика:")
        print(f"   • Всего заявок: {DatabaseService.get_applications_count()}")
        
        admin_chat_id = os.getenv('ADMIN_CHAT_ID')
        manager_telegram = os.getenv('TELEGRAM_MANAGER', '@yourusername')
        
        print("🔧 Настройки:")
        print(f"   • Админ чат: {'✅' if admin_chat_id else '❌'}")
        print(f"   • Менеджер: {manager_telegram}")
        print(f"   • Телефон: {MANAGER_PHONE}")
        print(f"   • Email: {MANAGER_EMAIL_CONTACT}")
        
        await dp.start_polling(bot)
        
    except Exception as e:
        logging.error(f"Ошибка при запуске бота: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
