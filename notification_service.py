import asyncio
import logging
import os
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from aiogram import Bot
from datetime import datetime
import json

class NotificationService:
    """Сервис для отправки уведомлений менеджерам"""
    
    def __init__(self):
        self.bot_token = os.getenv('BOT_TOKEN')
        self.admin_chat_id = os.getenv('ADMIN_CHAT_ID')  # ID чата для уведомлений
        self.manager_email = os.getenv('MANAGER_EMAIL')
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = os.getenv('SMTP_USERNAME')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        
    async def send_telegram_notification(self, application_data: dict):
        """Отправляет уведомление в Telegram админ-чат"""
        if not self.bot_token or not self.admin_chat_id:
            logging.warning("Telegram уведомления не настроены (нет BOT_TOKEN или ADMIN_CHAT_ID)")
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
            logging.info(f"Telegram уведомление отправлено для заявки #{application_data['id']}")
            return True
            
        except Exception as e:
            logging.error(f"Ошибка отправки Telegram уведомления: {e}")
            return False
    
    def send_email_notification(self, application_data: dict):
        """Отправляет email уведомление менеджеру"""
        if not all([self.manager_email, self.smtp_username, self.smtp_password]):
            logging.warning("Email уведомления не настроены")
            return False
            
        try:
            # Создаем сообщение
            msg = MimeMultipart()
            msg['From'] = self.smtp_username
            msg['To'] = self.manager_email
            msg['Subject'] = f"Новая заявка #{application_data['id']} - {application_data['name']}"
            
            # Форматируем данные пакета
            package_names = {
                'basic': 'Базовый пакет (85 000₽)',
                'advanced': 'Продвинутый пакет (150 000₽)',
                'premium': 'Премиум пакет (250 000₽)'
            }
            package_name = package_names.get(
                application_data.get('package_interest', ''), 
                'Пакет не указан'
            )
            
            # HTML содержимое письма
            html_body = f"""
            <html>
            <body style="font-family: Arial, sans-serif;">
                <div style="background: #007bff; color: white; padding: 20px; text-align: center;">
                    <h1>🆕 Новая заявка #{application_data['id']}</h1>
                </div>
                
                <div style="padding: 20px;">
                    <h2>Данные клиента:</h2>
                    <table style="border-collapse: collapse; width: 100%;">
                        <tr>
                            <td style="border: 1px solid #ddd; padding: 8px; background: #f2f2f2;"><strong>👤 Имя:</strong></td>
                            <td style="border: 1px solid #ddd; padding: 8px;">{application_data['name']}</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #ddd; padding: 8px; background: #f2f2f2;"><strong>📞 Телефон:</strong></td>
                            <td style="border: 1px solid #ddd; padding: 8px;"><a href="tel:{application_data['phone']}">{application_data['phone']}</a></td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #ddd; padding: 8px; background: #f2f2f2;"><strong>📦 Пакет:</strong></td>
                            <td style="border: 1px solid #ddd; padding: 8px;">{package_name}</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #ddd; padding: 8px; background: #f2f2f2;"><strong>🆔 Telegram ID:</strong></td>
                            <td style="border: 1px solid #ddd; padding: 8px;">{application_data['user_id']}</td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #ddd; padding: 8px; background: #f2f2f2;"><strong>⏰ Время заявки:</strong></td>
                            <td style="border: 1px solid #ddd; padding: 8px;">{application_data['created_at']}</td>
                        </tr>
                    </table>
                    
                    <h3>🎯 Рекомендуемые действия:</h3>
                    <ul>
                        <li>☎️ Позвонить клиенту в рабочее время (ПН-ПТ 9:00-18:00)</li>
                        <li>💬 Обсудить детали проекта и требования</li>
                        <li>📊 Подготовить коммерческое предложение</li>
                        <li>📅 Запланировать встречу или звонок</li>
                    </ul>
                    
                    <div style="text-align: center; margin: 20px 0;">
                        <a href="https://my-chatbot-landing.herokuapp.com" 
                           style="background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                           🔗 Открыть админ-панель
                        </a>
                    </div>
                </div>
                
                <div style="background: #f8f9fa; padding: 15px; text-align: center; color: #666;">
                    <p>Это автоматическое уведомление от Telegram-бота AI-решения</p>
                    <p>Время отправки: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}</p>
                </div>
            </body>
            </html>
            """
            
            msg.attach(MimeText(html_body, 'html', 'utf-8'))
            
            # Отправляем письмо
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            text = msg.as_string()
            server.sendmail(self.smtp_username, self.manager_email, text)
            server.quit()
            
            logging.info(f"Email уведомление отправлено для заявки #{application_data['id']}")
            return True
            
        except Exception as e:
            logging.error(f"Ошибка отправки email уведомления: {e}")
            return False
    
    async def send_all_notifications(self, application_data: dict):
        """Отправляет все типы уведомлений"""
        results = {
            'telegram': False,
            'email': False
        }
        
        # Telegram уведомление (асинхронно)
        results['telegram'] = await self.send_telegram_notification(application_data)
        
        # Email уведомление (синхронно)
        results['email'] = self.send_email_notification(application_data)
        
        # Логируем результаты
        sent_notifications = [k for k, v in results.items() if v]
        if sent_notifications:
            logging.info(f"Уведомления отправлены: {', '.join(sent_notifications)}")
        else:
            logging.warning("Ни одно уведомление не было отправлено")
        
        return results
    
    async def send_daily_report(self):
        """Отправляет ежедневный отчет"""
        try:
            from database_service import DatabaseService
            
            # Получаем статистику за сегодня
            today = datetime.now().date()
            total_apps = DatabaseService.get_applications_count()
            recent_apps = DatabaseService.get_recent_applications(limit=10)
            
            # Подсчитываем заявки за сегодня
            today_apps = [app for app in recent_apps if app.created_at.date() == today]
            
            if not self.admin_chat_id or not self.bot_token:
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
            logging.info("Ежедневный отчет отправлен")
            return True
            
        except Exception as e:
            logging.error(f"Ошибка отправки ежедневного отчета: {e}")
            return False
