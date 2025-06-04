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

@dp.message(CommandStart())
async def start_handler(message: types.Message):
    """Обработчик команды /start"""
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
    package_type = callback.data.replace("package_", "")
    package = PACKAGES_DATA.get(package_type)
    
    if not package:
        await callback.answer("Пакет не найден", show_alert=True)
        return
    
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
    builder.add(InlineKeyboardButton(text="📝 Оставить заявку", callback_data="contact"))
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
    contact_text = (
        "📝 **Оставить заявку**\n\n"
        "Для оформления заявки нам понадобятся ваши контактные данные.\n"
        "Наш менеджер свяжется с вами в рабочее время для:\n\n"
        "• 💰 Расчета точной стоимости проекта\n"
        "• 📋 Обсуждения технических деталей\n"
        "• ⏱ Согласования сроков разработки\n"
        "• 🎯 Составления индивидуального предложения\n\n"
        "**Готовы оставить контакт?**"
    )
    
    await callback.message.edit_text(
        contact_text,
        reply_markup=get_contact_menu(),
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data == "start_contact")
async def start_contact_collection(callback: types.CallbackQuery, state: FSMContext):
    """Начинает сбор контактных данных"""
    await state.set_state(ContactForm.waiting_for_name)
    
    contact_text = (
        "👤 **Как к вам обращаться?**\n\n"
        "Напишите ваше имя:"
    )
    
    # Удаляем клавиатуру для ввода текста
    await callback.message.edit_text(
        contact_text,
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.message(ContactForm.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    """Обрабатывает ввод имени"""
    name = message.text.strip()
    
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
    phone = message.text.strip()
    
    # Базовая проверка формата телефона
    if len(phone) < 10 or not any(char.isdigit() for char in phone):
        await message.answer(
            "📞 Пожалуйста, введите корректный номер телефона.\n"
            "Например: +7 (999) 123-45-67 или 89991234567"
        )
        return
    
    # Получаем сохраненные данные
    data = await state.get_data()
    name = data.get("name")
    
    # Здесь в будущем будет сохранение в БД
    # Пока просто логируем
    logging.info(f"Новая заявка: {name} - {phone}")
    
    success_text = (
        f"✅ **Спасибо, {name}!**\n\n"
        "Ваша заявка принята! 🎉\n\n"
        f"📋 **Ваши данные:**\n"
        f"👤 Имя: {name}\n"
        f"📞 Телефон: {phone}\n\n"
        "💼 Наш менеджер свяжется с вами в рабочее время "
        "для обсуждения вашего проекта.\n\n"
        "**Рабочее время**: ПН-ПТ с 9:00 до 18:00 МСК ⏰"
    )
    
    await message.answer(
        success_text,
        reply_markup=get_back_menu(),
        parse_mode="Markdown"
    )
    
    # Очищаем состояние  
    await state.clear()

@dp.message()
async def unknown_message(message: types.Message):
    """Обработчик неизвестных сообщений"""
    unknown_text = (
        "🤔 Извините, я не понимаю эту команду.\n\n"
        "Я могу помочь вам:\n"
        "• 📦 Узнать о пакетах услуг\n"
        "• 🔧 Изучить этапы разработки\n" 
        "• 📝 Оставить заявку на разработку бота\n\n"
        "**Выберите нужный раздел:**"
    )
    
    await message.answer(
        unknown_text,
        reply_markup=get_main_menu(),
        parse_mode="Markdown"
    )

async def main():
    """Основная функция запуска бота"""
    print("🤖 Бот запущен и готов к работе!")
    
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"Ошибка при запуске бота: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
