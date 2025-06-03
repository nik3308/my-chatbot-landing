import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from config import PACKAGES, ADMIN_USER_ID
from keyboards import (
    main_menu_keyboard,
    packages_keyboard,
    stages_keyboard,
    package_detail_keyboard,
    back_keyboard,
    after_request_keyboard,
    cancel_request_keyboard
)
from content import (
    WELCOME_MESSAGE,
    get_packages_info,
    get_stages_info,
    get_package_info,
    REQUEST_START_MESSAGE,
    get_phone_request_message,
    get_request_success_message,
    get_admin_notification_message,
    UNKNOWN_REQUEST_MESSAGE,
    CANCEL_REQUEST_MESSAGE
)
# Закомментируем импорт базы данных
# from database import save_request

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Состояния для ConversationHandler
NAME, PHONE = range(2)

# Обработчики команд
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start."""
    user = update.effective_user
    logger.info(f"Пользователь {user.id} ({user.username}) запустил бота")
    
    # Добавим больше логирования
    try:
        await update.message.reply_html(
            WELCOME_MESSAGE,
            reply_markup=main_menu_keyboard()
        )
        logger.info(f"Отправлено приветственное сообщение пользователю {user.id}")
    except Exception as e:
        logger.error(f"Ошибка при отправке приветствия: {e}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /help."""
    logger.info(f"Пользователь {update.effective_user.id} запросил справку")
    await update.message.reply_text(
        "Я могу рассказать о пакетах услуг, этапах разработки бота и принять вашу заявку.",
        reply_markup=main_menu_keyboard()
    )

# Обработчики текстовых сообщений
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработчик текстовых сообщений."""
    text = update.message.text.lower()
    logger.info(f"Получено сообщение: '{text}' от пользователя {update.effective_user.id}")
    
    # Проверяем, находится ли пользователь в процессе оформления заявки
    user_state = context.user_data.get('state')
    if user_state == 'waiting_for_name':
        return await get_name(update, context)
    elif user_state == 'waiting_for_phone':
        return await get_phone(update, context)
    
    # Если не в процессе оформления заявки, обрабатываем обычные сообщения
    if any(keyword in text for keyword in ["стоимость", "цена", "тариф", "пакет", "услуг"]):
        logger.info(f"Отправляем информацию о пакетах пользователю {update.effective_user.id}")
        await update.message.reply_html(
            get_packages_info(),
            reply_markup=packages_keyboard()
        )
    elif any(keyword in text for keyword in ["этап", "процесс", "как работает", "разработк"]):
        logger.info(f"Отправляем информацию об этапах пользователю {update.effective_user.id}")
        await update.message.reply_html(
            get_stages_info(),
            reply_markup=stages_keyboard()
        )
    elif any(keyword in text for keyword in ["заявк", "оставить", "связаться", "купить", "заказать"]):
        logger.info(f"Начинаем оформление заявки для пользователя {update.effective_user.id}")
        context.user_data['state'] = 'waiting_for_name'
        await update.message.reply_text(
            REQUEST_START_MESSAGE,
            reply_markup=cancel_request_keyboard()
        )
        return NAME
    else:
        logger.info(f"Отправляем сообщение о непонятном запросе пользователю {update.effective_user.id}")
        await update.message.reply_text(
            UNKNOWN_REQUEST_MESSAGE,
            reply_markup=main_menu_keyboard()
        )
    
    return ConversationHandler.END

# Обработчик кнопок
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработчик нажатий на кнопки."""
    query = update.callback_query
    await query.answer()
    
    logger.info(f"Пользователь {query.from_user.id} нажал кнопку с data: {query.data}")
    
    if query.data == 'packages':
        await query.message.edit_text(
            get_packages_info(), 
            reply_markup=packages_keyboard(),
            parse_mode='HTML'
        )
    
    elif query.data == 'stages':
        await query.message.edit_text(
            get_stages_info(), 
            reply_markup=stages_keyboard(),
            parse_mode='HTML'
        )
    
    elif query.data == 'request':
        context.user_data['state'] = 'waiting_for_name'
        await query.message.edit_text(
            REQUEST_START_MESSAGE,
            parse_mode='HTML'
        )
        return NAME
    
    elif query.data == 'back_to_menu':
        await query.message.edit_text(
            WELCOME_MESSAGE, 
            reply_markup=main_menu_keyboard(),
            parse_mode='HTML'
        )
    
    elif query.data.startswith('package_'):
        package_key = query.data.split('_')[1]
        if package_key in PACKAGES:
            context.user_data['selected_package'] = package_key
            await query.message.edit_text(
                get_package_info(package_key),
                reply_markup=package_detail_keyboard(package_key),
                parse_mode='HTML'
            )
    
    elif query.data.startswith('request_package_'):
        package_key = query.data.split('_')[2]
        if package_key in PACKAGES:
            context.user_data['selected_package'] = package_key
            context.user_data['state'] = 'waiting_for_name'
            await query.message.edit_text(
                REQUEST_START_MESSAGE,
                parse_mode='HTML'
            )
            return NAME
    
    elif query.data == 'cancel_request':
        context.user_data.pop('state', None)
        await query.message.edit_text(
            CANCEL_REQUEST_MESSAGE,
            reply_markup=main_menu_keyboard(),
            parse_mode='HTML'
        )
        return ConversationHandler.END
    
    return ConversationHandler.END

# Функции для сбора заявки
async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получает имя пользователя."""
    if update.callback_query:
        # Если функция вызвана из обработчика кнопок
        context.user_data['state'] = 'waiting_for_name'
        return NAME
    
    # Получаем имя из сообщения
    context.user_data['name'] = update.message.text
    context.user_data['state'] = 'waiting_for_phone'
    
    logger.info(f"Получено имя пользователя: {context.user_data['name']}")
    
    await update.message.reply_text(
        get_phone_request_message(context.user_data['name']),
        reply_markup=cancel_request_keyboard()
    )
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получает телефон пользователя и завершает сбор заявки."""
    context.user_data['phone'] = update.message.text
    
    logger.info(f"Получен телефон пользователя: {context.user_data['phone']}")
    
    # Получаем информацию о выбранном пакете
    package_key = context.user_data.get('selected_package')
    package_name = PACKAGES[package_key]['name'] if package_key else None
    
    # Закомментируем сохранение заявки в базу данных
    # save_request(
    #     user_id=update.effective_user.id,
    #     username=update.effective_user.username,
    #     name=context.user_data['name'],
    #     phone=context.user_data['phone'],
    #     package=package_name
    # )
    
    # Отправляем сообщение пользователю
    await update.message.reply_html(
        get_request_success_message(
            context.user_data['name'],
            context.user_data['phone'],
            package_name
        ),
        reply_markup=after_request_keyboard()
    )
    
    # Отправляем уведомление администратору, если указан ADMIN_USER_ID
    if ADMIN_USER_ID:
        try:
            await context.bot.send_message(
                chat_id=ADMIN_USER_ID,
                text=get_admin_notification_message(
                    update.effective_user.id,
                    update.effective_user.username,
                    context.user_data['name'],
                    context.user_data['phone'],
                    package_name
                ),
                parse_mode='HTML'
            )
            logger.info(f"Отправлено уведомление администратору о новой заявке")
        except Exception as e:
            logger.error(f"Ошибка при отправке уведомления администратору: {e}")
    
    # Очищаем состояние пользователя
    context.user_data.pop('state', None)
    logger.info(f"Новая заявка: {context.user_data['name']}, {context.user_data['phone']}, пакет: {package_name}")
    
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отменяет сбор заявки."""
    context.user_data.pop('state', None)
    
    if update.callback_query:
        await update.callback_query.message.edit_text(
            CANCEL_REQUEST_MESSAGE,
            reply_markup=main_menu_keyboard()
        )
    else:
        await update.message.reply_text(
            CANCEL_REQUEST_MESSAGE,
            reply_markup=main_menu_keyboard()
        )
    
    logger.info(f"Пользователь {update.effective_user.id} отменил оформление заявки")
    return ConversationHandler.END
