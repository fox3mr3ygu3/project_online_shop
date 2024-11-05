import requests


def send_order_to_telegram(order):
    token = '7653371699:AAFNsjg7xkki8eE2XuiFwjqqGV-VpobU2MM'  # Замените на ваш токен
    chat_id = '1731973285'  # Замените на ваш chat_id
    message = (f"Новый заказ #{order.id}:\n"
               f"Имя: {order.name}\n"
               f"Город: {order.city}\n"
               f"Адрес: {order.address}\n"
               f"Телефон: {order.phone}\n"
               f"Telegram: {order.telegram}\n"
               f"Количество: {order.quantity}\n"
               f"Название продукта: {order.product_name}\n"
               f"Общая стоимость: {order.total_price:.2f}\n"
               f"Дата заказа: {order.order_date}")

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {'chat_id': chat_id, 'text': message, 'parse_mode': 'HTML'}
    response = requests.post(url, json=payload)
    return response
