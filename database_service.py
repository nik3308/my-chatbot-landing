from sqlalchemy.orm import Session
from models import User, Application, DialogState, BotMetrics, get_db
from datetime import datetime
import json
import logging

class DatabaseService:
    """Сервис для работы с базой данных"""
    
    @staticmethod
    def get_or_create_user(telegram_id: int, username: str = None, 
                          first_name: str = None, last_name: str = None) -> User:
        """Получает или создает пользователя"""
        db = get_db()
        try:
            user = db.query(User).filter(User.telegram_id == telegram_id).first()
            
            if not user:
                user = User(
                    telegram_id=telegram_id,
                    username=username,
                    first_name=first_name,
                    last_name=last_name
                )
                db.add(user)
                db.commit()
                db.refresh(user)
                logging.info(f"Создан новый пользователь: {telegram_id}")
            else:
                # Обновляем данные если они изменились
                updated = False
                if user.username != username:
                    user.username = username
                    updated = True
                if user.first_name != first_name:
                    user.first_name = first_name
                    updated = True
                if user.last_name != last_name:
                    user.last_name = last_name
                    updated = True
                
                if updated:
                    user.updated_at = datetime.utcnow()
                    db.commit()
                    logging.info(f"Обновлены данные пользователя: {telegram_id}")
            
            return user
        except Exception as e:
            db.rollback()
            logging.error(f"Ошибка при работе с пользователем {telegram_id}: {e}")
            raise e
        finally:
            db.close()
    
    @staticmethod
    def has_user_submitted_application(telegram_id: int) -> bool:
        """Проверяет, подавал ли пользователь уже заявку"""
        db = get_db()
        try:
            application = db.query(Application).filter(
                Application.user_id == telegram_id
            ).first()
            return application is not None
        except Exception as e:
            logging.error(f"Ошибка при проверке заявки пользователя {telegram_id}: {e}")
            return False
        finally:
            db.close()
    
    @staticmethod
    def create_application(telegram_id: int, name: str, phone: str, 
                         package_interest: str = None) -> Application:
        """Создает новую заявку"""
        db = get_db()
        try:
            # Проверяем, есть ли уже заявка от этого пользователя
            existing = db.query(Application).filter(
                Application.user_id == telegram_id
            ).first()
            
            if existing:
                # Обновляем существующую заявку
                existing.name = name
                existing.phone = phone
                existing.package_interest = package_interest
                existing.updated_at = datetime.utcnow()
                existing.status = 'new'  # Сбрасываем статус
                db.commit()
                db.refresh(existing)
                logging.info(f"Обновлена заявка пользователя: {telegram_id}")
                return existing
            else:
                # Создаем новую заявку
                application = Application(
                    user_id=telegram_id,
                    name=name,
                    phone=phone,
                    package_interest=package_interest
                )
                db.add(application)
                db.commit()
                db.refresh(application)
                logging.info(f"Создана новая заявка: {telegram_id} - {name}")
                return application
        except Exception as e:
            db.rollback()
            logging.error(f"Ошибка при создании заявки {telegram_id}: {e}")
            raise e
        finally:
            db.close()
    
    @staticmethod
    def update_user_contact_data(telegram_id: int, name: str, phone: str):
        """Обновляет контактные данные пользователя"""
        db = get_db()
        try:
            user = db.query(User).filter(User.telegram_id == telegram_id).first()
            if user:
                user.name = name
                user.phone = phone
                user.updated_at = datetime.utcnow()
                db.commit()
                logging.info(f"Обновлены контактные данные пользователя: {telegram_id}")
        except Exception as e:
            db.rollback()
            logging.error(f"Ошибка при обновлении контактов {telegram_id}: {e}")
        finally:
            db.close()
    
    @staticmethod
    def save_dialog_state(telegram_id: int, state: str, data: dict = None):
        """Сохраняет состояние диалога"""
        db = get_db()
        try:
            dialog_state = db.query(DialogState).filter(
                DialogState.telegram_id == telegram_id
            ).first()
            
            data_json = json.dumps(data) if data else None
            
            if dialog_state:
                dialog_state.current_state = state
                dialog_state.data = data_json
                dialog_state.updated_at = datetime.utcnow()
            else:
                dialog_state = DialogState(
                    telegram_id=telegram_id,
                    current_state=state,
                    data=data_json
                )
                db.add(dialog_state)
            
            db.commit()
        except Exception as e:
            db.rollback()
            logging.error(f"Ошибка при сохранении состояния {telegram_id}: {e}")
        finally:
            db.close()
    
    @staticmethod
    def get_dialog_state(telegram_id: int) -> tuple:
        """Получает состояние диалога"""
        db = get_db()
        try:
            dialog_state = db.query(DialogState).filter(
                DialogState.telegram_id == telegram_id
            ).first()
            
            if dialog_state:
                data = json.loads(dialog_state.data) if dialog_state.data else {}
                return dialog_state.current_state, data
            return None, {}
        except Exception as e:
            logging.error(f"Ошибка при получении состояния {telegram_id}: {e}")
            return None, {}
        finally:
            db.close()
    
    @staticmethod
    def clear_dialog_state(telegram_id: int):
        """Очищает состояние диалога"""
        db = get_db()
        try:
            dialog_state = db.query(DialogState).filter(
                DialogState.telegram_id == telegram_id
            ).first()
            
            if dialog_state:
                db.delete(dialog_state)
                db.commit()
        except Exception as e:
            db.rollback()
            logging.error(f"Ошибка при очистке состояния {telegram_id}: {e}")
        finally:
            db.close()
    
    @staticmethod
    def log_user_action(telegram_id: int, action: str, data: dict = None):
        """Логирует действие пользователя"""
        db = get_db()
        try:
            metric = BotMetrics(
                telegram_id=telegram_id,
                action=action,
                data=json.dumps(data) if data else None
            )
            db.add(metric)
            db.commit()
        except Exception as e:
            db.rollback()
            logging.error(f"Ошибка при логировании действия {telegram_id}: {e}")
        finally:
            db.close()
    
    @staticmethod
    def get_applications_count() -> int:
        """Получает общее количество заявок"""
        db = get_db()
        try:
            count = db.query(Application).count()
            return count
        except Exception as e:
            logging.error(f"Ошибка при подсчете заявок: {e}")
            return 0
        finally:
            db.close()
    
    @staticmethod
    def get_recent_applications(limit: int = 10) -> list:
        """Получает последние заявки"""
        db = get_db()
        try:
            applications = db.query(Application).order_by(
                Application.created_at.desc()
            ).limit(limit).all()
            return applications
        except Exception as e:
            logging.error(f"Ошибка при получении заявок: {e}")
            return []
        finally:
            db.close()