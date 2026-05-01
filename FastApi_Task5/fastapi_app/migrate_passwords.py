import sys
import os

# Добавляем корень проекта в путь, чтобы работали импорты src
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.infrastructure.postgres.database import database
from src.infrastructure.postgres.models.users import User
from src.core.security import get_password_hash

# --- КОНФИГУРАЦИЯ ---
TARGET_USERNAMES = ["admin", "alex", "anton", "leo", "mcvent", "ventik", "mcvent2", "sdfsdf", "stghjkring", "str5ing", "string", "ventik"]
NEW_PASSWORD = "TestPass123!"

def migrate_passwords():
    print(f"Начало миграции паролей для пользователей: {TARGET_USERNAMES}")
    print(f"Новый пароль для всех будет установлен на: {NEW_PASSWORD}")

    with database.session() as session:
        updated_count = 0

        for username in TARGET_USERNAMES:
            user = session.query(User).filter(User.username == username).first()

            if not user:
                print(f"Пользователь '{username}' не найден в базе данных.")
                continue

            try:
                # Генерируем новый хеш bcrypt
                new_hash = get_password_hash(NEW_PASSWORD)

                # Обновляем поле password в БД
                user.password = new_hash
                session.commit()

                print(f"Пароль для пользователя '{username}' успешно обновлен.")
                updated_count += 1

            except Exception as e:
                session.rollback()
                print(f"Ошибка при обновлении пользователя '{username}': {e}")

    print(f"\nГотово. Обновлено пользователей: {updated_count}")
    print(f"Теперь вы можете войти под этими пользователями с паролем: {NEW_PASSWORD}")


if __name__ == "__main__":
    migrate_passwords()