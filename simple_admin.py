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
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{ 
                    font-family: Arial, sans-serif; 
                    margin: 20px; 
                    background: #f5f5f5;
                }}
                .header {{ 
                    background: #007bff; 
                    color: white; 
                    padding: 20px; 
                    text-align: center; 
                    border-radius: 8px;
                    margin-bottom: 20px;
                }}
                .stats {{ 
                    background: #f8f9fa; 
                    padding: 15px; 
                    margin: 10px 0; 
                    border-radius: 8px;
                    border-left: 4px solid #007bff;
                }}
                .application {{ 
                    border: 1px solid #ddd; 
                    margin: 10px 0; 
                    padding: 15px; 
                    background: white;
                    border-radius: 8px;
                }}
                .app-id {{ 
                    background: #28a745; 
                    color: white; 
                    padding: 5px 10px; 
                    border-radius: 3px; 
                    display: inline-block;
                    margin-bottom: 10px;
                }}
                .refresh {{ 
                    background: #007bff; 
                    color: white; 
                    padding: 10px 20px; 
                    border: none; 
                    border-radius: 5px;
                    cursor: pointer;
                    margin: 10px 0; 
                }}
                .refresh:hover {{
                    background: #0056b3;
                }}
                .detail-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 10px;
                    margin-top: 10px;
                }}
                .detail-item {{
                    background: #f8f9fa;
                    padding: 8px;
                    border-radius: 4px;
                    border-left: 3px solid #007bff;
                }}
                .detail-label {{
                    font-weight: bold;
                    color: #495057;
                    display: block;
                    margin-bottom: 4px;
                }}
                .no-applications {{
                    text-align: center;
                    padding: 40px;
                    color: #666;
                    background: white;
                    border-radius: 8px;
                }}
                @media (max-width: 768px) {{
                    .detail-grid {{
                        grid-template-columns: 1fr;
                    }}
                    body {{
                        margin: 10px;
                    }}
                }}
            </style>
            <script>
                function refreshPage() {{ 
                    location.reload(); 
                }}
                // Автообновление каждую минуту
                setTimeout(function(){{ location.reload(); }}, 60000);
            </script>
        </head>
        <body>
            <div class="header">
                <h1>🤖 Админ-панель AI-решения</h1>
                <p>Управление заявками и мониторинг</p>
            </div>
            
            <button onclick="refreshPage()" class="refresh">🔄 Обновить</button>
            
            <div class="stats">
                <h3>📊 Статистика</h3>
                <p><strong>Всего заявок:</strong> {total}</p>
                <p><strong>Время обновления:</strong> {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}</p>
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
                    <div class="app-id">Заявка #{app.id}</div>
                    <div class="detail-grid">
                        <div class="detail-item">
                            <span class="detail-label">👤 Имя:</span>
                            {app.name}
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">📞 Телефон:</span>
                            <a href="tel:{app.phone}">{app.phone}</a>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">📦 Пакет:</span>
                            {package_name}
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">🆔 Telegram ID:</span>
                            {app.user_id}
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">⏰ Время:</span>
                            {app.created_at.strftime('%d.%m.%Y %H:%M')}
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">📊 Статус:</span>
                            {app.status or 'новая'}
                        </div>
                    </div>
                </div>
                """
        else:
            html += """
            <div class="no-applications">
                <h3>📭 Заявок пока нет</h3>
                <p>Как только поступит первая заявка, она появится здесь</p>
            </div>
            """
        
        html += """
            <div style="text-align: center; margin-top: 40px; padding: 20px; background: white; border-radius: 8px; color: #666;">
                <p>🔄 <strong>Автообновление каждую минуту</strong></p>
                <p>🚀 <a href="https://t.me/echo1995_bot" target="_blank">Открыть бота в Telegram</a></p>
            </div>
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
