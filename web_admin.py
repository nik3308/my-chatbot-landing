#!/usr/bin/env python3
"""
Веб-админка для просмотра заявок через браузер.
Добавьте в Procfile: web: python web_admin.py
"""

import os
from flask import Flask, render_template_string, request
from database_service import DatabaseService
from datetime import datetime

app = Flask(__name__)

# Простая аутентификация (в production используйте более надежную)
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')

def check_auth():
    """Проверка простой аутентификации"""
    if request.method == 'POST':
        return request.form.get('password') == ADMIN_PASSWORD
    return request.args.get('password') == ADMIN_PASSWORD

# HTML шаблон
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Админ-панель AI-решения</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { text-align: center; color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; margin-bottom: 20px; }
        .stats { display: flex; gap: 20px; margin-bottom: 30px; flex-wrap: wrap; }
        .stat-card { background: #007bff; color: white; padding: 20px; border-radius: 8px; flex: 1; min-width: 200px; text-align: center; }
        .stat-number { font-size: 2em; font-weight: bold; }
        .applications { margin-top: 20px; }
        .app-card { border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 8px; background: #fff; }
        .app-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
        .app-id { background: #28a745; color: white; padding: 5px 10px; border-radius: 20px; font-size: 0.9em; }
        .app-status { padding: 5px 10px; border-radius: 20px; font-size: 0.9em; }
        .status-new { background: #ffc107; color: #000; }
        .status-contacted { background: #17a2b8; color: white; }
        .status-closed { background: #28a745; color: white; }
        .app-details { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; margin-top: 10px; }
        .detail-item { padding: 8px; background: #f8f9fa; border-radius: 4px; }
        .refresh-btn { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin-bottom: 20px; }
        .refresh-btn:hover { background: #0056b3; }
        .login-form { max-width: 400px; margin: 100px auto; text-align: center; }
        .login-input { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; }
        .login-btn { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
    </style>
    <script>
        function refreshPage() { location.reload(); }
        setInterval(refreshPage, 30000); // Автообновление каждые 30 секунд
    </script>
</head>
<body>
    {% if not authenticated %}
    <div class="login-form">
        <h2>🔐 Вход в админ-панель</h2>
        <form method="post">
            <input type="password" name="password" placeholder="Пароль" class="login-input" required>
            <br>
            <button type="submit" class="login-btn">Войти</button>
        </form>
        <p><small>Пароль по умолчанию: admin123</small></p>
    </div>
    {% else %}
    <div class="container">
        <div class="header">
            <h1>🤖 Админ-панель AI-решения</h1>
            <p>Управление заявками и статистика бота</p>
        </div>

        <button onclick="refreshPage()" class="refresh-btn">🔄 Обновить</button>

        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{{ total_applications }}</div>
                <div>Всего заявок</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ new_applications }}</div>
                <div>Новых заявок</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ total_users }}</div>
                <div>Пользователей</div>
            </div>
        </div>

        <div class="applications">
            <h2>📋 Последние заявки</h2>
            {% for app in applications %}
            <div class="app-card">
                <div class="app-header">
                    <span class="app-id">Заявка #{{ app.id }}</span>
                    <span class="app-status status-{{ app.status }}">
                        {% if app.status == 'new' %}🆕 Новая
                        {% elif app.status == 'contacted' %}📞 Связались
                        {% elif app.status == 'closed' %}✅ Закрыта
                        {% else %}❓ {{ app.status }}
                        {% endif %}
                    </span>
                </div>
                <div class="app-details">
                    <div class="detail-item"><strong>👤 Имя:</strong> {{ app.name }}</div>
                    <div class="detail-item"><strong>📞 Телефон:</strong> {{ app.phone }}</div>
                    <div class="detail-item"><strong>🆔 Telegram ID:</strong> {{ app.user_id }}</div>
                    <div class="detail-item"><strong>⏰ Дата:</strong> {{ app.created_at.strftime('%d.%m.%Y %H:%M') }}</div>
                    {% if app.package_interest %}
                    <div class="detail-item">
                        <strong>📦 Пакет:</strong> 
                        {% if app.package_interest == 'basic' %}Базовый
                        {% elif app.package_interest == 'advanced' %}Продвинутый
                        {% elif app.package_interest == 'premium' %}Премиум
                        {% else %}{{ app.package_interest }}
                        {% endif %}
                    </div>
                    {% endif %}
                </div>
            </div>
            {% endfor %}
        </div>

        <div style="text-align: center; margin-top: 40px; color: #666;">
            <p>🔄 Автообновление каждые 30 секунд</p>
            <p><small>Время последнего обновления: {{ current_time }}</small></p>
        </div>
    </div>
    {% endif %}
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def admin_panel():
    """Главная страница админ-панели"""
    
    # Проверка аутентификации
    if not check_auth():
        return render_template_string(HTML_TEMPLATE, authenticated=False)
    
    try:
        # Получаем статистику
        applications = DatabaseService.get_recent_applications(limit=20)
        total_applications = DatabaseService.get_applications_count()
        
        # Подсчитываем новые заявки
        new_applications = sum(1 for app in applications if app.status == 'new')
        
        # Подсчитываем пользователей (приблизительно)
        total_users = len(set(app.user_id for app in applications))
        
        return render_template_string(
            HTML_TEMPLATE,
            authenticated=True,
            applications=applications,
            total_applications=total_applications,
            new_applications=new_applications,
            total_users=total_users,
            current_time=datetime.now().strftime('%d.%m.%Y %H:%M:%S')
        )
        
    except Exception as e:
        return f"❌ Ошибка: {str(e)}"

@app.route('/health')
def health_check():
    """Проверка работоспособности"""
    return {"status": "ok", "service": "admin-panel"}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
