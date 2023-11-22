from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime


def generate_pdf(waybill_data, file_name=None):
    if file_name is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        waybill_id = waybill_data.get('waybill_id', 'unknown')
        file_name = f"waybill_{waybill_id}_{timestamp}.pdf"

    pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))

    c = canvas.Canvas(file_name, pagesize=A4)
    c.setFont("DejaVuSans", 12)

    c.drawString(100, 800, f"Накладная ID: {waybill_data.get('waybill_id', 'N/A')}")
    c.drawString(100, 780, f"Описание груза: {waybill_data.get('cargo_description', 'N/A')}")
    c.drawString(100, 760, f"Вес груза: {waybill_data.get('weight', 'N/A')}")
    c.drawString(100, 740, f"Габариты: {waybill_data.get('dimensions', 'N/A')}")
    c.drawString(100, 720, f"Адрес отправки: {waybill_data.get('address_from', 'N/A')}")
    c.drawString(100, 700, f"Адрес получения: {waybill_data.get('address_to', 'N/A')}")
    c.drawString(100, 680, f"Способ оплаты: {waybill_data.get('payment_method', 'N/A')}")

    c.save()
    return file_name

