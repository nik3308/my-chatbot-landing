#!/usr/bin/env python3
"""
Улучшенная веб-админка с управлением статусами заявок
"""

import os
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template_string, redirect, url_for
from database_service import DatabaseService
from sqlalchemy import create_engine, text
from models import get_database_url, SessionLocal

app = Flask(__name__)

# Простая аутентификация
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')

def check_auth():
    """Проверка аутентификации"""
    if request.method == 'POST':
        return request.form.get('password') == ADMIN_PASSWORD
    return request.args.get('password') == ADMIN_PASSWORD

def update_application_status(app_id, status):
    """Обновляет статус заявки"""
    try:
        db = SessionLocal()
        db.execute(text("UPDATE applications SET status = :status, updated_at = :updated_at WHERE id = :id"), 
                  {"status": status, "updated_at": datetime.utcnow(), "id": app_id})
        db.commit()
        db.close()
        return True
    except Exception as e:
        print(f"Ошибка обновления статуса: {e}")
        return False

# Расширенный HTML шаблон
ENHANCED_HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Админ-панель AI-решения - Расширенная</title>
    <style>
        * { box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; background: #f8f9fa; color: #333; }
        .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #007bff, #0056b3); color: white; padding: 30px; text-align: center; border-radius: 10px; margin-bottom: 30px; box-shadow: 0 4px 20px rgba(0,123,255,0.3); }
        .header h1 { margin: 0; font-size: 2.5em; font-weight: 300; }
        .header p { margin: 10px 0 0 0; opacity: 0.9; }
        
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .stat-card { background: white; padding: 25px; border-radius: 12px; box-shadow: 0 2px 15px rgba(0,0,0,0.08); text-align: center; border-left: 4px solid #007bff; }
        .stat-number { font-size: 2.5em; font-weight: bold; color: #007bff; margin-bottom: 5px; }
        .stat-label { color: #666; font-size: 0.9em; text-transform: uppercase; letter-spacing: 1px; }
        
        .controls { background: white; padding: 20px; border-radius: 12px; margin-bottom: 20px; box-shadow: 0 2px 15px rgba(0,0,0,0.08); }
        .controls h3 { margin-top: 0; color: #333; }
        .btn { padding: 10px 20px; border: none; border-radius: 6px; cursor: pointer; font-size: 14px; margin: 5px; text-decoration: none; display: inline-block; transition: all 0.3s; }
        .btn-primary { background: #007bff; color: white; }
        .btn-secondary { background: #6c757d; color: white; }
        .btn-success { background: #28a745; color: white; }
        .btn-warning { background: #ffc107; color: #212529; }
        .btn-danger { background: #dc3545; color: white; }
        .btn:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
        
        .applications { background: white; border-radius: 12px; box-shadow: 0 2px 15px rgba(0,0,0,0.08); overflow: hidden; }
        .applications h3 { margin: 0; padding: 20px; background: #f8f9fa; border-bottom: 1px solid #dee2e6; }
        
        .app-card { border-bottom: 1px solid #f0f0f0; padding: 20px; transition: all 0.3s; }
        .app-card:hover { background: #f8f9fa; }
        .app-card:last-child { border-bottom: none; }
        
        .app-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; flex-wrap: wrap; gap: 10px; }
        .app-id { background: #28a745; color: white; padding: 8px 16px; border-radius: 20px; font-size: 0.9em; font-weight: bold; }
        .app-status { padding: 6px 12px; border-radius: 20px; font-size: 0.85em; font-weight: 600; }
        .status-new { background: #fff3cd; color: #856404; border: 1px solid #ffeaa7; }
        .status-contacted { background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }
        .status-closed { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        
        .app-details { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-top: 15px; }
        .detail-item { padding: 12px; background: #f8f9fa; border-radius: 8px; border-left: 3px solid #007bff; }
        .detail-label { font-weight: 600; color: #495057; display: block; margin-bottom: 5px; }
        .detail-value { color: #333; }
        
        .actions { margin-top: 15px; padding-top: 15px; border-top: 1px solid #f0f0f0; }
        .actions h4 { margin: 0 0 10px 0; color: #666; font-size: 0.9em; }
        
        .login-form { max-width: 400px; margin: 100px auto; background: white; padding: 40px; border-radius: 12px; box-shadow: 0 4px 25px rgba(0,0,0,0.1); text-align: center; }
        .login-input { width: 100%; padding: 12px; margin: 15px 0; border: 2px solid #e9ecef; border-radius: 8px; font-size: 16px; }
        .login-input:focus { outline: none; border-color: #007bff; }
        .login-btn { background: #007bff; color: white; padding: 12px 30px; border: none; border-radius: 8px; cursor: pointer; font-size: 16px; width: 100%; }
        
        .filter-section { margin-bottom: 20px; }
        .filter-btn { padding: 8px 16px; margin: 5px; border: 1px solid #007bff; background: white; color: #007bff; border-radius: 20px; cursor: pointer; }
        .filter-btn.active { background: #007bff; color: white; }
        
        .empty-state { text-align: center; padding: 60px 20px; color: #666; }
        .empty-state img { width: 100px; opacity: 0.5; margin-bottom: 20px; }
        
        @media (max-width: 768px) {
            .container { padding: 10px; }
            .stats-grid { grid-template-columns: 1fr; }
            .app-header { flex-direction: column; align-items: flex-start; }
            .app-details { grid-template-columns: 1fr; }
        }
    </style>
    <script>
        function refreshPage() { 
            window.location.reload(); 
        }
        
        function updateStatus(appId, status) {
            fetch('/update_status', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({app_id: appId, status: status, password: '{{ password }}'})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    refreshPage();
                } else {
                    alert('Ошибка: ' + data.error);
                }
            });
        }
        
        function filterApplications(status) {
            const apps = document.querySelectorAll('.app-card');
            const buttons = document.querySelectorAll('.filter-btn');
            
            buttons.forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            
            apps.forEach(app => {
                if (status === 'all' || app.dataset.status === status) {
                    app.style.display = 'block';
                } else {
                    app.style.display = 'none';
                }
            });
        }
        
        // Автообновление каждые 2 минуты
        setInterval(refreshPage, 120000);
    </script>
</head>
<body>
    {% if not authenticated %}
    <div class="login-form">
        <h2>🔐 Админ-панель AI-решения</h2>
        <p>Введите пароль для доступа</p>
        <form method="post">
            <input type="password" name="password" placeholder="Пароль" class="login-input" required>
            <button type="submit" class="login-btn">Войти</button>
        </form>
        <p><small>Пароль по умолчанию: admin123</small></p>
    </div>
    {% else %}
    <div class="container">
        <div class="header">
            <h1>🤖 Админ-панель AI-решения</h1>
            <p>Управление заявками и мониторинг эффективности</p>
        </div>

        <div class="controls">
            <h3>🔧 Управление</h3>
            <button onclick="refreshPage()" class="btn btn-primary">🔄 Обновить данные</button>
            <a href="/export" class="btn btn-secondary">📊 Экспорт CSV</a>
            <a href="/api/applications" class="btn btn-secondary">🔗 JSON API</a>
            <button onclick="window.print()" class="btn btn-secondary">🖨️ Печать</button>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{{ total_applications }}</div>
                <div class="stat-label">Всего заявок</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ new_applications }}</div>
                <div class="stat-label">Новых заявок</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ today_applications }}</div>
                <div class="stat-label">За сегодня</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ total_users }}</div>
                <div class="stat-label">Пользователей</div>
            </div>
        </div>

        <div class="applications">
            <h3>📋 Заявки клиентов</h3>
            
            <div class="filter-section" style="padding: 0 20px 10px;">
                <button class="filter-btn active" onclick="filterApplications('all')">Все</button>
                <button class="filter-btn" onclick="filterApplications('new')">🆕 Новые</button>
                <button class="filter-btn" onclick="filterApplications('contacted')">📞 Обработанные</button>
                <button class="filter-btn" onclick="filterApplications('closed')">✅ Закрытые</button>
            </div>

            {% if applications %}
                {% for app in applications %}
                <div class="app-card" data-status="{{ app.status }}">
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
                        <div class="detail-item">
                            <span class="detail-label">⏰ Дата заявки</span>
                            <span class="detail-value">{{ app.created_at.strftime('%d.%m.%Y %H:%M') }}</span>
                        </div>
                        {% if app.package_interest %}
                        <div class="detail-item">
                            <span class="detail-label">📦 Интересующий пакет</span>
                            <span class="detail-value">
                                {% if app.package_interest == 'basic' %}💫 Базовый (85 000₽)
                                {% elif app.package_interest == 'advanced' %}⭐ Продвинутый (150 000₽)
                                {% elif app.package_interest == 'premium' %}💎 Премиум (250 000₽)
                                {% else %}{{ app.package_interest }}
                                {% endif %}
                            </span>
                        </div>
                        {% endif %}
                    </div>
                    
                    <div class="actions">
                        <h4>🎯 Действия со статусом:</h4>
                        {% if app.status == 'new' %}
                            <button onclick="updateStatus({{ app.id }}, 'contacted')" class="btn btn-warning">
                                📞 Отметить "Связались"
                            </button>
                        {% endif %}
                        {% if app.status in ['new', 'contacted'] %}
                            <button onclick="updateStatus({{ app.id }}, 'closed')" class="btn btn-success">
                                ✅ Закрыть заявку
                            </button>
                        {% endif %}
                        {% if app.status != 'new' %}
                            <button onclick="updateStatus({{ app.id }}, 'new')" class="btn btn-secondary">
                                🔄 Вернуть в "Новые"
                            </button>
                        {% endif %}
                    </div>
                </div>
                {% endfor %}
            {% else %}
                <div class="empty-state">
                    <div style="font-size: 4em; margin-bottom: 20px;">📭</div>
                    <h3>Заявок пока нет</h3>
                    <p>Как только поступит первая заявка, она появится здесь</p>
                </div>
            {% endif %}
        </div>

        <div style="text-align: center; margin-top: 40px; padding: 20px; background: white; border-radius: 12px; color: #666; box-shadow: 0 2px 15px rgba(0,0,0,0.08);">
            <p>🔄 <strong>Автообновление каждые 2 минуты</strong></p>
            <p>⏰ Последнее обновление: {{ current_time }}</p>
            <p>🚀 <a href="https://t.me/echo1995_bot" target="_blank">Открыть бота в Telegram</a></p>
        </div>
    </div>
    {% endif %}

    <script>
        // Скрипт для автообновления страницы при получении новых заявок
        let lastApplicationCount = {{ total_applications }};
        
        async function checkForUpdates() {
            try {
                const response = await fetch('/api/applications');
                const data = await response.json();
                if (data.total > lastApplicationCount) {
                    // Новая заявка! Показываем уведомление и обновляем
                    if (Notification.permission === 'granted') {
                        new Notification('Новая заявка!', {
                            body: `Поступила новая заявка. Всего: ${data.total}`,
                            icon: '/favicon.ico'
                        });
                    }
                    window.location.reload();
                }
            } catch (error) {
                console.log('Ошибка проверки обновлений:', error);
            }
        }
        
        // Запрашиваем разрешение на уведомления
        if ('Notification' in window && Notification.permission === 'default') {
            Notification.requestPermission();
        }
        
        // Проверяем обновления каждые 30 секунд
        setInterval(checkForUpdates, 30000);
    </script>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def admin_panel():
    """Главная страница расширенной админ-панели"""
    
    # Проверка аутентификации
    if not check_auth():
        return render_template_string(ENHANCED_HTML_TEMPLATE, authenticated=False)
    
    try:
        # Получаем все заявки
        applications = DatabaseService.get_recent_applications(limit=50)
        total_applications = DatabaseService.get_applications_count()
        
        # Статистика
        new_applications = sum(1 for app in applications if app.status == 'new')
        
        # Заявки за сегодня
        today = datetime.now().date()
        today_applications = sum(1 for app in applications if app.created_at.date() == today)
        
        # Уникальные пользователи
        total_users = len(set(app.user_id for app in applications))
        
        return render_template_string(
            ENHANCED_HTML_TEMPLATE,
            authenticated=True,
            applications=applications,
            total_applications=total_applications,
            new_applications=new_applications,
            today_applications=today_applications,
            total_users=total_users,
            current_time=datetime.now().strftime('%d.%m.%Y %H:%M:%S'),
            password=ADMIN_PASSWORD
        )
        
    except Exception as e:
        return f"❌ Ошибка: {str(e)}"

@app.route('/update_status', methods=['POST'])
def update_status():
    """Обновление статуса заявки"""
    try:
        data = request.get_json()
        
        # Проверка пароля
        if data.get('password') != ADMIN_PASSWORD:
            return jsonify({'success': False, 'error': 'Неверный пароль'})
        
        app_id = data.get('app_id')
        status = data.get('status')
        
        if not app_id or not status:
            return jsonify({'success': False, 'error': 'Некорректные данные'})
        
        # Обновляем статус
        success = update_application_status(app_id, status)
        
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Ошибка обновления'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/applications')
def api_applications():
    """API для получения заявок"""
    try:
        applications = DatabaseService.get_recent_applications(limit=20)
        result = []
        
        for app in applications:
            result.append({
                'id': app.id,
                'name': app.name,
                'phone': app.phone,
                'package_interest': app.package_interest,
                'user_id': app.user_id,
                'status': app.status,
                'created_at': app.created_at.isoformat(),
                'updated_at': app.updated_at.isoformat() if app.updated_at else None
            })
        
        return jsonify({
            'total': DatabaseService.get_applications_count(),
            'applications': result,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/export')
def export_csv():
    """Экспорт заявок в CSV"""
    try:
        applications = DatabaseService.get_recent_applications(limit=1000)
        
        # Формируем CSV
        csv_content = "ID,Имя,Телефон,Пакет,Telegram ID,Статус,Дата создания,Дата обновления\n"
        
        for app in applications:
            package_names = {
                'basic': 'Базовый',
                'advanced': 'Продвинутый',
                'premium': 'Премиум'
            }
            package_name = package_names.get(app.package_interest, app.package_interest or '')
            
            csv_content += f'{app.id},"{app.name}","{app.phone}","{package_name}",{app.user_id},{app.status},{app.created_at},{app.updated_at or ""}\n'
        
        # Отправляем файл
        from flask import Response
        return Response(
            csv_content,
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename="applications_{datetime.now().strftime("%Y%m%d_%H%M")}.csv"'}
        )
        
    except Exception as e:
        return f"Ошибка экспорта: {str(e)}"

@app.route('/health')
def health_check():
    """Проверка работоспособности"""
    return jsonify({
        'status': 'ok', 
        'service': 'enhanced-admin-panel',
        'timestamp': datetime.now().isoformat(),
        'total_applications': DatabaseService.get_applications_count()
    })

@app.route('/stats')
def get_stats():
    """Детальная статистика"""
    try:
        db = SessionLocal()
        
        # Статистика по дням за последнюю неделю
        week_ago = datetime.now() - timedelta(days=7)
        daily_stats = db.execute(text("""
            SELECT DATE(created_at) as date, COUNT(*) as count,
                   COUNT(CASE WHEN package_interest = 'basic' THEN 1 END) as basic_count,
                   COUNT(CASE WHEN package_interest = 'advanced' THEN 1 END) as advanced_count,
                   COUNT(CASE WHEN package_interest = 'premium' THEN 1 END) as premium_count
            FROM applications 
            WHERE created_at >= :week_ago
            GROUP BY DATE(created_at) 
            ORDER BY date DESC
        """), {"week_ago": week_ago}).fetchall()
        
        # Статистика по статусам
        status_stats = db.execute(text("""
            SELECT status, COUNT(*) as count 
            FROM applications 
            GROUP BY status
        """)).fetchall()
        
        db.close()
        
        stats = {
            'daily_stats': [{'date': str(row[0]), 'total': row[1], 'basic': row[2], 'advanced': row[3], 'premium': row[4]} for row in daily_stats],
            'status_stats': [{'status': row[0], 'count': row[1]} for row in status_stats],
            'total_applications': DatabaseService.get_applications_count()
        }
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
                            <span class="detail-label">👤 Имя клиента</span>
                            <span class="detail-value">{{ app.name }}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">📞 Телефон</span>
                            <span class="detail-value"><a href="tel:{{ app.phone }}">{{ app.phone }}</a></span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">🆔 Telegram ID</span>
                            <span class="detail-value">{{ app.user_id }}</span>
                        </div>
                        <div class="detail-item">
