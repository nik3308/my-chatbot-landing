import asyncio
import logging
import os
from datetime import datetime

try:
    import smtplib
    from email.mime.text import MimeText
    from email.mime.multipart import MimeMultipart
    EMAIL_AVAILABLE = True
except ImportError:
    EMAIL_AVAILABLE = False
    print("⚠️ Email библиотеки недоступны")

try:
    from aiogram import Bot
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    print("⚠️ Telegram библиотеки недоступны")

class NotificationService:
    """Сервис для отправки уведомлений менеджерам"""
    
    def __init__(self):
        self.bot_token = os.getenv('BOT_TOKEN')
        self.admin_chat_id = os.getenv('ADMIN_CHAT_ID')
        self.manager_email = os.getenv('MANAGER_EMAIL')
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = os.getenv('SMTP_USERNAME')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        
    async def send_telegram_notification(self, application_data: dict):
        """Отправляет уведомление в Telegram админ-чат"""
        if not TELEGRAM_AVAILABLE:
            print("❌ Telegram библиотеки недоступны")
            return False
            
        if not self.bot_token or not self.admin_chat_id:
            print("⚠️ Telegram уведомления не настроены (нет BOT_TOKEN или ADMIN_CHAT_ID)")
            return False
            
        try:
            bot = Bot(token=self.bot_token)
            
            # Форматируем данные пакета
            package_names = {
                'basic': 'Базовый (85 000₽)',
                'advanced': 'Продвинутый (150 000₽)',
                'premium': 'Премиум (250 000₽)'
            }
            package_name = package_names.get(
                application_data.get('package_interest', ''), 
                application_data.get('package_interest', 'не указан')
            )
            
            # Создаем сообщение
            message = (
                f"🆕 **НОВАЯ ЗАЯВКА #{application_data['id']}**\n\n"
                f"👤 **Клиент**: {application_data['name']}\n"
                f"📞 **Телефон**: `{application_data['phone']}`\n"
                f"📦 **Интересующий пакет**: {package_name}\n"
                f"🆔 **Telegram ID**: {application_data['user_id']}\n"
                f"⏰ **Время**: {application_data['created_at']}\n\n"
                f"🔗 **Админка**: https://my-chatbot-landing.herokuapp.com\n\n"
                f"⚡ **Действия**:\n"
                f"• Позвонить клиенту в рабочее время\n"
                f"• Обсудить детали проекта\n"
                f"• Подготовить коммерческое предложение"
            )
            
            await bot.send_message(
                chat_id=self.admin_chat_id,
                text=message,
                parse_mode="Markdown"
            )
            
            await bot.session.close()
            print(f"✅ Telegram уведомление отправлено для заявки #{application_data['id']}")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка отправки Telegram уведомления: {e}")
            return False
    
    def send_email_notification(self, application_data: dict):
        """Отправляет email уведомление менеджеру"""
        if not EMAIL_AVAILABLE:
            print("❌ Email библиотеки недоступны")
            return False
            
        if not all([self.manager_email, self.smtp_username, self.smtp_password]):
            print("⚠️ Email уведомления не настроены")
            return False
            
        try:
            # Создаем сообщение
            msg = MimeMultipart()
            msg['From'] = self.smtp_username
            msg['To'] = self.manager_email
            msg['Subject'] = f"Новая заявка #{application_data['id']} - {application_data['name']}"
            
            # Простое текстовое содержимое
            text_body = f"""
Новая заявка #{application_data['id']}

Клиент: {application_data['name']}
Телефон: {application_data['phone']}
Telegram ID: {application_data['user_id']}
Время: {application_data['created_at']}

Админ-панель: https://my-chatbot-landing.herokuapp.com
            """
            
            msg.attach(MimeText(text_body, 'plain', 'utf-8'))
            
            # Отправляем письмо
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            text = msg.as_string()
            server.sendmail(self.smtp_username, self.manager_email, text)
            server.quit()
            
            print(f"✅ Email уведомление отправлено для заявки #{application_data['id']}")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка отправки email уведомления: {e}")
            return False
    
    async def send_all_notifications(self, application_data: dict):
        """Отправляет все типы уведомлений"""
        print(f"🔔 Отправка уведомлений для заявки #{application_data['id']}")
        
        results = {
            'telegram': False,
            'email': False
        }
        
        # Telegram уведомление (асинхронно)
        try:
            results['telegram'] = await self.send_telegram_notification(application_data)
        except Exception as e:
            print(f"❌ Ошибка Telegram уведомления: {e}")
        
        # Email уведомление (синхронно)
        try:
            results['email'] = self.send_email_notification(application_data)
        except Exception as e:
            print(f"❌ Ошибка Email уведомления: {e}")
        
        # Логируем результаты
        sent_notifications = [k for k, v in results.items() if v]
        if sent_notifications:
            print(f"✅ Уведомления отправлены: {', '.join(sent_notifications)}")
        else:
            print("⚠️ Ни одно уведомление не было отправлено")
        
        return results
    
    async def send_daily_report(self):
        """Отправляет ежедневный отчет"""
        if not TELEGRAM_AVAILABLE:
            print("❌ Telegram библиотеки недоступны для отчета")
            return False
            
        try:
            from database_service import DatabaseService
            
            # Получаем статистику за сегодня
            today = datetime.now().date()
            total_apps = DatabaseService.get_applications_count()
            recent_apps = DatabaseService.get_recent_applications(limit=10)
            
            # Подсчитываем заявки за сегодня
            today_apps = [app for app in recent_apps if app.created_at.date() == today]
            
            if not self.admin_chat_id or not self.bot_token:
                print("⚠️ Настройки Telegram для отчета не найдены")
                return False
            
            bot = Bot(token=self.bot_token)
            
            report_message = (
                f"📊 **ЕЖЕДНЕВНЫЙ ОТЧЕТ** - {today.strftime('%d.%m.%Y')}\n\n"
                f"📈 **Статистика:**\n"
                f"• Всего заявок: {total_apps}\n"
                f"• Заявок за сегодня: {len(today_apps)}\n\n"
            )
            
            if today_apps:
                report_message += "🆕 **Заявки за сегодня:**\n"
                for app in today_apps:
                    package_name = {
                        'basic': 'Базовый',
                        'advanced': 'Продвинутый',
                        'premium': 'Премиум'
                    }.get(app.package_interest, 'не указан')
                    
                    report_message += (
                        f"• #{app.id} - {app.name} ({app.phone}) - {package_name}\n"
                    )
            else:
                report_message += "📭 Новых заявок за сегодня нет\n"
            
            report_message += f"\n🔗 [Админ-панель](https://my-chatbot-landing.herokuapp.com)"
            
            await bot.send_message(
                chat_id=self.admin_chat_id,
                text=report_message,
                parse_mode="Markdown"
            )
            
            await bot.session.close()
            print("✅ Ежедневный отчет отправлен")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка отправки ежедневного отчета: {e}")
            return False
