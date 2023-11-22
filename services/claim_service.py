from utils.database import connect, close


class ClaimService:

    @staticmethod
    def get_user_id(telegram_user_id):
        conn = connect()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT userid FROM users WHERE telegramuserid=%s", (telegram_user_id,))
            user_id = cursor.fetchone()[0]
            return user_id
        except Exception as _ex:
            print(_ex)
        finally:
            close(conn)

    @staticmethod
    def get_manager_id(telegram_user_id):
        conn = connect()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT managers.telegramuserid FROM managers JOIN users ON managers.managerid = users.managerid WHERE users.telegramuserid = %s", (telegram_user_id,))
            manager_id = cursor.fetchone()[0]
            return manager_id
        except Exception as _ex:
            print(_ex)
        finally:
            close(conn)

    @staticmethod
    def create_claim(waybillid, userid, email, description, amount_requested, evidence):
        try:
            conn = connect()
            cursor = conn.cursor()
            insert_query = """
                INSERT INTO claims (waybillid, userid, email, description, amountrequested, evidence)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING claimid
            """
            cursor.execute(insert_query, (waybillid, userid, email, description, amount_requested, evidence))
            claim_id = cursor.fetchone()[0]
            conn.commit()

            return claim_id
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            close(conn)
