from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# Главное меню
def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("📦 Узнать о пакетах услуг", callback_data='packages')],
        [InlineKeyboardButton("🔄 Этапы разработки бота", callback_data='stages')],
        [InlineKeyboardButton("📝 Оставить заявку", callback_data='request')]
    ]
    return InlineKeyboardMarkup(keyboard)

# Клавиатура для выбора пакета
def packages_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("Базовый", callback_data='package_basic'),
            InlineKeyboardButton("Продвинутый", callback_data='package_advanced'),
            InlineKeyboardButton("Премиум", callback_data='package_premium')
        ],
        [InlineKeyboardButton("« Назад в меню", callback_data='back_to_menu')]
    ]
    return InlineKeyboardMarkup(keyboard)

# Клавиатура для раздела этапов
def stages_keyboard():
    keyboard = [
        [InlineKeyboardButton("📦 Узнать о пакетах", callback_data='packages')],
        [InlineKeyboardButton("📝 Оставить заявку", callback_data='request')],
        [InlineKeyboardButton("« Назад в меню", callback_data='back_to_menu')]
    ]
    return InlineKeyboardMarkup(keyboard)

# Клавиатура для конкретного пакета
def package_detail_keyboard(package_key):
    keyboard = [
        [InlineKeyboardButton("📝 Оставить заявку на этот пакет", callback_data=f'request_package_{package_key}')],
        [InlineKeyboardButton("« Назад к пакетам", callback_data='packages')],
        [InlineKeyboardButton("« Назад в меню", callback_data='back_to_menu')]
    ]
    return InlineKeyboardMarkup(keyboard)

# Клавиатура для кнопки "назад"
def back_keyboard():
    keyboard = [[InlineKeyboardButton("« Назад в меню", callback_data='back_to_menu')]]
    return InlineKeyboardMarkup(keyboard)

# Клавиатура после оформления заявки
def after_request_keyboard():
    keyboard = [
        [InlineKeyboardButton("📦 Узнать больше о пакетах", callback_data='packages')],
        [InlineKeyboardButton("🔄 Узнать об этапах разработки", callback_data='stages')],
        [InlineKeyboardButton("« Вернуться в главное меню", callback_data='back_to_menu')]
    ]
    return InlineKeyboardMarkup(keyboard)

# Клавиатура отмены при оформлении заявки
def cancel_request_keyboard():
    keyboard = [[InlineKeyboardButton("❌ Отменить оформление заявки", callback_data='cancel_request')]]
    return InlineKeyboardMarkup(keyboard)