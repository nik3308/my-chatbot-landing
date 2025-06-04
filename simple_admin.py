#!/usr/bin/env python3
"""
Простая веб-админка для просмотра заявок
"""

import os
from datetime import datetime
import json

try:
    from flask import Flask, request, jsonify
    from database_service import DatabaseService
except ImportError as e:
    print(f"Ошибка импорта: {e}")
    print("Убедитесь, что установлены зависимости: pip install flask sqlalchemy psycopg2-binary")
    exit(1)

app = Flask(__name__)

@app.route('/')
def home():
    """Главная страница с простым HTML"""
    try:
        # Получаем заявки
        applications = DatabaseService.get_recent_applications(limit=20)
        total = DatabaseService.get_applications_count()
        
        # Простой HTML
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Админ-панель AI-решения</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background: #007bff; color: white; padding: 20px; text-align: center; }}
                .stats {{ background: #f8f9fa; padding: 15px; margin: 10px 0; }}
                .application {{ border: 1px solid #ddd; margin: 10px 0; padding: 15px; }}
                .app-id {{ background: #28a745; color: white; padding: 5px 10px; border-radius: 3px; }}
                .refresh {{ background: #007bff; color: white; padding: 10px; border: none; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🤖 Админ-панель AI-решения</h1>
            </div>
            
            <button onclick="location.reload()" class="refresh">🔄 Обновить</button>
            
            <div class="stats">
                <h3>📊 Статистика</h3>
                <p>Всего заявок: <strong>{total}</strong></p>
                <p>Время обновления: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}</p>
            </div>
            
            <h3>📋 Заявки</h3>
        """
        
        if applications:
            for app in applications:
                package_name = {
                    'basic': 'Базовый',
                    'advanced': 'Продвинутый', 
                    'premium': 'Премиум'
                }.get(app.package_interest, app.package_interest or 'не указан')
                
                html += f"""
                <div class="application">
                    <span class="app-id">Заявка #{app.id}</span>
                    <p><strong>👤 Имя:</strong> {app.name}</p>
                    <p><strong>📞 Телефон:</strong> {app.phone}</p>
                    <p><strong>📦 Пакет:</strong> {package_name}</p>
                    <p><strong>🆔 Telegram ID:</strong> {app.user_id}</p>
                    <p><strong>⏰ Время:</strong> {app.created_at.strftime('%d.%m.%Y %H:%M')}</p>
                </div>
                """
        else:
            html += "<p>📭 Заявок пока нет</p>"
        
        html += """
            <script>
                // Автообновление каждую минуту
                setTimeout(function(){ location.reload(); }, 60000);
            </script>
        </body>
        </html>
        """
        
        return html
        
    except Exception as e:
        return f"<h1>❌ Ошибка</h1><p>{str(e)}</p>"

@app.route('/api/applications')
def api_applications():
    """API для получения заявок в JSON"""
    try:
        applications = DatabaseService.get_recent_applications(limit=10)
        result = []
        
        for app in applications:
            result.append({
                'id': app.id,
                'name': app.name,
                'phone': app.phone,
                'package_interest': app.package_interest,
                'user_id': app.user_id,
                'created_at': app.created_at.isoformat(),
                'status': app.status
            })
        
        return jsonify({
            'total': DatabaseService.get_applications_count(),
            'applications': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    """Проверка работоспособности"""
    return jsonify({'status': 'ok', 'time': datetime.now().isoformat()})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
