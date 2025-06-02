from config import PACKAGES, DEVELOPMENT_STAGES, COMPANY_NAME

# Приветственное сообщение
WELCOME_MESSAGE = f"""
👋 Здравствуйте! Я бот компании "{COMPANY_NAME}".

Я помогу вам с ответами на вопросы о процессе создания бота, расскажу об этапах работ, помогу определить специфику вашего проекта и сориентирую по стоимости.

Чем я могу вам помочь сегодня?
"""

# Информация о пакетах услуг
def get_packages_info():
    message = "📦 У нас есть 3 пакета услуг:\n\n"
    
    for i, (key, package) in enumerate(PACKAGES.items(), 1):
        emoji_number = f"{i}️⃣"
        message += f"{emoji_number} <b>{package['name']}</b>:\n"
        message += f"   💰 Стоимость: {package['price']}\n"
        message += f"   ✅ Включает: {package['includes']}\n"
        message += f"   ⏱️ Срок: {package['deadline']}\n\n"
    
    message += "Какой пакет вас заинтересовал больше всего?"
    return message

# Информация об этапах разработки
def get_stages_info():
    message = "🔄 <b>Этапы разработки бота</b>:\n\n"
    
    for i, stage in enumerate(DEVELOPMENT_STAGES, 1):
        message += f"{i}. <b>{stage['name']}</b> - {stage['description']}\n"
    
    message += "\nХотите узнать о наших пакетах услуг или оставить заявку?"
    return message

# Информация о конкретном пакете
def get_package_info(package_key):
    if package_key in PACKAGES:
        package = PACKAGES[package_key]
        message = f"📦 <b>{package['name']}</b>\n\n"
        message += f"💰 Стоимость: {package['price']}\n"
        message += f"✅ Включает: {package['includes']}\n"
        message += f"⏱️ Срок: {package['deadline']}\n\n"
        message += "Хотите оставить заявку на этот пакет?"
        return message
    else:
        return "Извините, информация о выбранном пакете не найдена."

# Сообщение о начале сбора заявки
REQUEST_START_MESSAGE = """
Для оформления заявки мне потребуется собрать немного информации.

Пожалуйста, укажите ваше имя:
"""

# Сообщение для запроса телефона
def get_phone_request_message(name):
    return f"Спасибо, {name}! Теперь, пожалуйста, укажите ваш номер телефона:"

# Сообщение об успешном оформлении заявки
def get_request_success_message(name, phone, package=None):
    message = f"""
✅ Спасибо за вашу заявку!

<b>Имя:</b> {name}
<b>Телефон:</b> {phone}
"""
    
    if package:
        message += f"<b>Выбранный пакет:</b> {package}\n"
    
    message += """
Наш менеджер свяжется с вами в ближайшее рабочее время для обсуждения деталей.

Есть ли у вас ещё вопросы?
"""
    return message

# Сообщение для уведомления администратора о новой заявке
def get_admin_notification_message(user_id, username, name, phone, package=None):
    message = f"""
🔔 <b>Новая заявка!</b>

<b>От пользователя:</b> {username or 'Не указан'} (ID: {user_id})
<b>Имя:</b> {name}
<b>Телефон:</b> {phone}
"""
    
    if package:
        message += f"<b>Выбранный пакет:</b> {package}\n"
    
    return message

# Сообщение, если бот не понял запрос
UNKNOWN_REQUEST_MESSAGE = """
Извините, я не совсем понял ваш вопрос. 

Я могу рассказать о:
- Наших пакетах услуг
- Этапах разработки бота
- Помочь оформить заявку

Пожалуйста, выберите одну из опций ниже или задайте вопрос по-другому.
"""

# Сообщение для отмены сбора заявки
CANCEL_REQUEST_MESSAGE = """
Оформление заявки отменено. 

Чем ещё я могу вам помочь?
"""