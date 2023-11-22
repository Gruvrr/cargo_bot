from utils import database
import psycopg2
from aiogram import Bot


class WaybillService:
    @staticmethod
    def create_waybill(user_id, waybill_data):
        if not WaybillService.validate_data(waybill_data):
            raise ValueError("Invalid waybill data")

        waybill_id = WaybillService.save_waybill_to_db(user_id, waybill_data)
        if waybill_id is None:
            raise Exception("Failed to save waybill to database")
        return waybill_id

    @staticmethod
    def validate_data(data):
        required_fields = ["cargo_description", "weight", "dimensions", "address_from", "address_to", "payment_method"]
        return all(field in data for field in required_fields)

    @staticmethod
    def save_waybill_to_db(telegram_user_id, data):
        conn = database.connect()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT userid FROM users WHERE telegramuserid = %s", (telegram_user_id,))
            user_id = cursor.fetchone()[0]
            cursor.execute(
                "INSERT INTO waybills (userid, cargodescription, weight, dimensions, addressfrom, addressto, paymentmethod) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING waybillid",
                (user_id, data['cargo_description'], data['weight'], data['dimensions'], data['address_from'],
                 data['address_to'], data['payment_method']))

            waybill_id = cursor.fetchone()[0]
            conn.commit()
            return waybill_id
        except (Exception, psycopg2.DatabaseError) as error:
            print("Error in save_waybill_to_db method", error)
            return None
        finally:
            database.close(conn)
