import json
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib import colors
import re
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime

# Регистрируем шрифт с поддержкой кириллицы
pdfmetrics.registerFont(TTFont("DejaVuSans", "DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DejaVuSans-Bold", "DejaVuSans-Bold.ttf"))


def generate_invoice(
    order_json: str,
    invoice_number: str = "001",
    supplier: str = "ИП Слабошпицкий В.В.",
    year: int = 2025,
):
    # Парсим JSON
    order_json = order_json.strip().strip("```").lstrip("json")
    order = json.loads(order_json)
    date_str = order["order"].get("date")
    try:
        day, month = map(int, date_str.split("."))
    except:  # noqa
        day, month = datetime.now().day, datetime.now().month

    # Форматирование даты
    months = [
        "ЯНВАРЯ",
        "ФЕВРАЛЯ",
        "МАРТА",
        "АПРЕЛЯ",
        "МАЯ",
        "ИЮНЯ",
        "ИЮЛЯ",
        "АВГУСТА",
        "СЕНТЯБРЯ",
        "ОКТЯБРЯ",
        "НОЯБРЯ",
        "ДЕКАБРЯ",
    ]
    header_date = f"{day:02d} {months[month - 1]} {year} г."

    # Извлекаем данные
    order = order["order"]
    city = order.get("city")
    name = order.get("name")
    phone = order.get("phone")
    items = order.get("items")
    total = order.get("total_from_text")
    address = order.get("address")

    # Формируем данные для таблицы товаров
    item_data = [["№", "Наименование товара", "Кол-во", "Ед.", "Стоимость"]]
    for i, item in enumerate(items, 1):
        name = item["name"]
        quantity = item["quantity"]
        unit = item["unit"]
        price = item["price"]
        item_data.append([str(i), name, quantity, unit, price])

    # Создаем PDF
    pdf_filename = f"{phone}_{datetime.now().strftime('%Y%m%d')}.pdf".replace("+", "")
    doc = SimpleDocTemplate(pdf_filename, pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    elements = []

    # Стили
    styles = getSampleStyleSheet()
    title_style = styles["Title"]
    title_style.fontName = "DejaVuSans-Bold"
    title_style.fontSize = 16
    title_style.spaceAfter = 12
    normal_style = styles["Normal"]
    normal_style.fontName = "DejaVuSans"
    normal_style.fontSize = 12
    normal_style.spaceAfter = 6

    # Заголовок
    elements.append(Paragraph(f"{header_date} РАСХОДНАЯ НАКЛАДНАЯ", title_style))

    # Информация о поставщике и покупателе
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"Поставщик: {supplier}", normal_style))
    elements.append(Paragraph(f"Адрес: {address}", normal_style))
    elements.append(Paragraph(f"Телефон: {phone}", normal_style))
    elements.append(Spacer(1, 12))

    # Таблица товаров
    table = Table(item_data, colWidths=[30, 350, 60, 80, 80], hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),  # Заголовки по центру
                ("ALIGN", (0, 1), (-1, -1), "LEFT"),  # Содержимое по левому краю
                ("FONTNAME", (0, 0), (-1, 0), "DejaVuSans-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "DejaVuSans"),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]
        )
    )
    elements.append(table)
    elements.append(Spacer(1, 12))

    cost_style = styles["Normal"].clone(name="cost_style")
    cost_style.fontName = "DejaVuSans-Bold"
    cost_style.fontSize = 14

    # Общая стоимость
    elements.append(Paragraph(f"Общая стоимость: {total} руб.", cost_style))
    elements.append(Spacer(1, 24))

    title_style_custom = styles["Normal"].clone(name="custom_title")
    title_style_custom.fontName = "DejaVuSans-Bold"
    title_style_custom.fontSize = 12

    # Подписи
    elements.append(Paragraph("Отпустил:", title_style_custom))
    elements.append(Spacer(1, 25))
    elements.append(Paragraph(f"Подпись: ___________________________ {supplier}", normal_style))
    elements.append(Spacer(1, 25))
    elements.append(Paragraph("Получил:", title_style_custom))
    elements.append(Spacer(1, 25))
    elements.append(Paragraph("Подпись: ____________________  Дата: ____________________", normal_style))
    elements.append(Spacer(1, 12))

    normal_style = styles["Normal"]
    normal_style.textColor = colors.gray
    elements.append(Paragraph("Примечания:", normal_style))
    elements.append(Paragraph("* - Товар отпущен в соответствии с заказом", normal_style))
    elements.append(Paragraph("* - Качество товара соответствует требованиям", normal_style))
    elements.append(Paragraph("* - Срок реализации согласно маркировке", normal_style))

    # Генерация PDF
    doc.build(elements)
    return pdf_filename


# order_json = """
# ```json
# {
#     "order": {
#         "date": "18.07",
#         "city": "Макеевка",
#         "address": "квартал Гвардейский (центрально-городской район) д.7 кв 83",
#         "phone": "+79493736534",
#         "items": [
#             {"name": "Икра горбуши", "quantity": 1, "unit_price": 2790},
#             {"name": "Лещ цимлянский", "quantity": 1, "unit_price": 762},
#             {"name": "Кальмар филе", "quantity": 1, "unit_price": 856}
#         ],
#         "total": 5110,
#         "discount": 4000,
#         "final_total": 1110,
#         "packages": 3
#     }
# }
# ```
# """

# # Генерация накладной
# pdf_file = generate_invoice(order_json)
# print(f"PDF-накладная сгенерирована: {pdf_file}")
