from utils.database import connect, close
from models.user import User


class UserService:
    @staticmethod
    def create_new_user(user_data):
        conn = connect()
        cursor = conn.cursor()
        new_user = User(
            user_id=user_data['user_id'],
            telegram_user_id=user_data['telegram_user_id'],
            username=user_data['username'],
            is_manager=user_data['is_manager'],
            manager_id=user_data['manager_id']
        )

        try:
            cursor.execute("SELECT userid FROM users WHERE telegramuserid = %s", (user_data['telegram_user_id'],))
            result = cursor.fetchone()

            if not result:
                cursor.execute("INSERT INTO users (telegramuserid, username, ismanager, managerid) VALUES (%s, %s, %s, %s)",
                               (new_user.telegram_user_id, new_user.username, new_user.is_manager, new_user.manager_id))
                conn.commit()
        except Exception as e:
            print(f"Ошибка при работе с базой данных: {e}")
        finally:
            close(conn)