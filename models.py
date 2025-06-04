from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# Создаем базовый класс для моделей
Base = declarative_base()

class User(Base):
    """Модель пользователя"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False, index=True)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    name = Column(String(255), nullable=True)  # Имя указанное пользователем
    phone = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<User(telegram_id={self.telegram_id}, name='{self.name}')>"

class Application(Base):
    """Модель заявки"""
    __tablename__ = 'applications'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, index=True)  # telegram_id пользователя
    name = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=False)
    package_interest = Column(String(50), nullable=True)  # basic, advanced, premium
    status = Column(String(50), default='new')  # new, contacted, closed
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Application(id={self.id}, name='{self.name}', status='{self.status}')>"

class DialogState(Base):
    """Модель состояния диалога"""
    __tablename__ = 'dialog_states'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False, index=True)
    current_state = Column(String(100), nullable=True)
    data = Column(Text, nullable=True)  # JSON данные состояния
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<DialogState(telegram_id={self.telegram_id}, state='{self.current_state}')>"

class BotMetrics(Base):
    """Модель метрик бота"""
    __tablename__ = 'bot_metrics'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, nullable=False, index=True)
    action = Column(String(100), nullable=False)  # start, view_packages, submit_application
    data = Column(Text, nullable=True)  # Дополнительные данные
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<BotMetrics(telegram_id={self.telegram_id}, action='{self.action}')>"

# Настройка подключения к базе данных
def get_database_url():
    """Получает URL базы данных из переменных окружения"""
    database_url = os.getenv('DATABASE_URL')
    if database_url and database_url.startswith('postgres://'):
        # Heroku использует postgres://, но SQLAlchemy требует postgresql://
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    return database_url or 'sqlite:///bot.db'  # Fallback для локальной разработки

# Создание движка и сессии
engine = create_engine(get_database_url())
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Создает все таблицы в базе данных"""
    Base.metadata.create_all(bind=engine)
    print("✅ Таблицы базы данных созданы")

def get_db():
    """Получает сессию базы данных"""
    db = SessionLocal()
    try:
        return db
    except Exception as e:
        db.close()
        raise e
