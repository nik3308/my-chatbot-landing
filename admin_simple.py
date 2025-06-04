#!/usr/bin/env python3
"""
Простая админ-панель для просмотра заявок из базы данных.
Запуск: python admin.py
"""

import os
from datetime import datetime
from models import get_database_url, SessionLocal
from database_service import DatabaseService
from sqlalchemy import create_engine, text

def print_separator():
    print("=" * 60)

def print_header(title):
    print_separator()
    print(f"🎯 {title}")
    print_separator()

def format_datetime(dt):
    """Форматирует дату и время для вывода"""
    if dt:
        return dt.strftime("%d.%m.%Y %H:%M")
    return "—"

def show_applications():
    """Показывает все заявки"""
    print_header("ЗАЯВКИ КЛИЕНТОВ")
    
    try:
        applications = DatabaseService.get_recent_applications(limit=50)
        
        if not applications:
            print("📭 Заявок пока нет")
            return
        
        print(f"📊 Всего заявок: {DatabaseService.get_applications_count()}")
        print()
        
        for app in applications:
            status_emoji = {
                'new': '🆕',
                'contacted': '📞',
                'closed': '✅'
            }.get(app.status, '❓')
            
            package_name = ""
            if app.package_interest:
                packages = {
                    'basic': 'Базовый',
                    'advanced': 'Продвинутый', 
                    'premium': 'Премиум'
                }
                package_name = f" | 📦 {packages.get(app.package_interest, app.package_interest)}"
            
            print(f"{status_emoji} Заявка #{app.id}")
            print(f"   👤 {app.name}")
            print(f"   📞 {app.phone}")
            print(f"   🆔 Telegram ID: {app.user_id}")
            print(f"   ⏰ {format_datetime(app.created_at)}{package_name}")
            if app.notes:
                print(f"   📝 {app.notes}")
            print()
            
    except Exception as e:
        print(f"❌ Ошибка при получении заявок: {e}")

def show_statistics():
    """Показывает статистику"""
    print_header("СТАТИСТИКА")
    
    try:
        db = SessionLocal()
        
        # Общее количество заявок
        total_apps = DatabaseService.get_applications_count()
        print(f"📋 Всего заявок: {total_apps}")
        
        # Статистика по пакетам
        result = db.execute(text("""
            SELECT package_interest, COUNT(*) as count 
            FROM applications 
            WHERE package_interest IS NOT NULL 
            GROUP BY package_interest
        """)).fetchall()
        
        print("\n📦 По пакетам:")
        package_names = {
            'basic': 'Базовый',
            'advanced': 'Продвинутый',
            'premium': 'Премиум'
        }
        
        for row in result:
            package_name = package_names.get(row[0], row[0])
            print(f"   • {package_name}: {row[1]}")
        
        # Статистика по дням
        result = db.execute(text("""
            SELECT DATE(created_at) as date, COUNT(*) as count 
            FROM applications 
            GROUP BY DATE(created_at) 
            ORDER BY date DESC 
            LIMIT 7
        """)).fetchall()
        
        print("\n📅 За последние дни:")
        for row in result:
            date_str = row[0].strftime("%d.%m.%Y") if hasattr(row[0], 'strftime') else str(row[0])
            print(f"   • {date_str}: {row[1]}")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Ошибка при получении статистики: {e}")

def test_connection():
    """Тестирует подключение к базе данных"""
    print_header("ТЕСТ ПОДКЛЮЧЕНИЯ К БД")
    
    try:
        database_url = get_database_url()
        print(f"🔗 URL БД: {database_url[:50]}...")
        
        engine = create_engine(database_url)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1")).fetchone()
            print("✅ Подключение к базе данных успешно!")
            
        # Проверяем таблицы
        db = SessionLocal()
        try:
            apps_count = db.execute(text("SELECT COUNT(*) FROM applications")).scalar()
            users_count = db.execute(text("SELECT COUNT(*) FROM users")).scalar()
            print(f"📊 Пользователей: {users_count}")
            print(f"📊 Заявок: {apps_count}")
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")

def show_recent_activity():
    """Показывает последнюю активность"""
    print_header("ПОСЛЕДНЯЯ АКТИВНОСТЬ")
    
    try:
        db = SessionLocal()
        
        result = db.execute(text("""
            SELECT telegram_id, action, data, created_at 
            FROM bot_metrics 
            ORDER BY created_at DESC 
            LIMIT 10
        """)).fetchall()
        
        if not result:
            print("📭 Активности пока нет")
            return
        
        action_names = {
            'start': '🚀 Запуск бота',
            'view_packages': '📦 Просмотр пакетов',
            'view_package_details': '👀 Детали пакета',
            'view_stages': '🔧 Этапы разработки',
            'start_contact_form': '📝 Начало заявки',
            'submit_application': '✅ Подача заявки',
            'unknown_message': '❓ Неизвестное сообщение'
        }
        
        for row in result:
            telegram_id, action, data, created_at = row
            action_name = action_names.get(action, action)
            time_str = format_datetime(created_at)
            print(f"{action_name} | ID: {telegram_id} | {time_str}")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Ошибка при получении активности: {e}")

def main_menu():
    """Главное меню админ-панели"""
    while True:
        print_header("АДМИН-ПАНЕЛЬ AI-РЕШЕНИЯ")
        print("1. 📋 Показать заявки")
        print("2. 📊 Статистика")
        print("3. 🔄 Последняя активность") 
        print("4. 🔧 Тест подключения к БД")
        print("0. ❌ Выход")
        print()
        
        choice = input("Выберите действие (0-4): ").strip()
        
        if choice == "1":
            show_applications()
        elif choice == "2":
            show_statistics()
        elif choice == "3":
            show_recent_activity()
        elif choice == "4":
            test_connection()
        elif choice == "0":
            print("👋 До свидания!")
            break
        else:
            print("❌ Неверный выбор!")
        
        input("\nНажмите Enter для продолжения...")
        print("\n" * 2)

if __name__ == "__main__":
    # Проверяем наличие переменных окружения
    if not os.getenv('DATABASE_URL') and not os.path.exists('bot.db'):
        print("❌ Не найдена база данных!")
        print("Установите переменную DATABASE_URL или создайте bot.db")
        exit(1)
    
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n👋 Выход по Ctrl+C")