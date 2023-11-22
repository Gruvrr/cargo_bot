import json
from utils.database import connect,close


class Chat:
    @staticmethod
    def new_callback_from_user(user_id, username):
        try:
            conn = connect()
            cursor = conn.cursor()
            cursor.execute("SELECT managerid FROM users WHERE telegramuserid = %s", (user_id,))
            manager_id = cursor.fetchone()[0]
            if manager_id:
                cursor.execute("""
                                INSERT INTO notifications (managerid, type, details)
                                VALUES (%s, %s, %s)
                            """, (manager_id, 'call', f'Вас вызывает пользователь @{username}'))
                conn.commit()
                cursor.execute("SELECT telegramuserid FROM managers WHERE managerid = %s", (manager_id,))
                manager_telegram_id = cursor.fetchone()[0]
                return manager_telegram_id
        except Exception as _ex:
            print(f"[ERROR] - {_ex}")
        finally:
            close(conn)

    # @staticmethod
    # def new_chat_with_user(user_id, manager_id):
    #     conn = connect()
    #     cursor = conn.cursor()
    #     try:
    #         cursor.execute("SELECT stateid FROM userstates WHERE userid = %s", (manager_id,))
    #         state = cursor.fetchone()
    #         cursor.execute("SELECT userid FROM users WHERE telegramuserid = %s", (manager_id,))
    #         manager_id = cursor.fetchone()[0]
    #         if state is not None:
    #             actiondetails_json = json.dumps({'current_client_id': user_id})
    #             cursor.execute("""
    #                             UPDATE userstates
    #                             SET state = %s, actiondetails = %s, lastupdated = CURRENT_TIMESTAMP
    #                             WHERE stateid = %s
    #                         """, ('in_chat', actiondetails_json, state[0]))
    #         else:
    #             actiondetails_json = json.dumps({'current_client_id': user_id})
    #             cursor.execute("""
    #                             INSERT INTO userstates (userid, state, actiondetails, lastupdated)
    #                             VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
    #                         """, (manager_id, 'in_chat', actiondetails_json))
    #
    #         conn.commit()
    #         return True
    #     except Exception as _ex:
    #         print(f"[ERROR тут] - {_ex}")
    #         return False
    #     finally:
    #         close(conn)


    @staticmethod
    def new_chat_with_user(user_id, manager_id):
        conn = connect()
        cursor = conn.cursor()

        try:

            cursor.execute("SELECT managerid FROM managers WHERE telegramuserid = %s", (manager_id,))
            manager_id = cursor.fetchone()[0]
            cursor.execute("SELECT userid FROM users WHERE telegramuserid = %s", (user_id,))
            user_id = cursor.fetchone()[0]
            cursor.execute("""
                INSERT INTO chats (userid, managerid, messages)
                VALUES (%s, %s, %s)
            """, (user_id, manager_id, ''))
            cursor.execute("""
                            UPDATE userstates
                            SET state = 'in_chat'
                            WHERE userid = %s OR userid = %s
                        """, (user_id, manager_id))
            conn.commit()
            return True
        except Exception as _ex:
            print(f"[ERROR тут] - {_ex}")
            return False
        finally:
            close(conn)




