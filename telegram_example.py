# from telegram import Bot

# import asyncio


# BOT_TOKEN = '7042471860:AAEGGb2usb6ZjZomisNmyEEB1SytBqSXrsM'
# CHAT_ID = '770967266'
# text = 'text'

# def send_message(text):
#     """
#     동기적으로 Telegram 메세지를 보내는 함수
#     :param text: 보낼 메세지의 내용
#     """
#     bot = Bot(token=BOT_TOKEN)
#     bot.send_message(chat_id=CHAT_ID, text=text)

# # 함수 사용 예제
# send_message(text)


import telebot

BOT_TOKEN = '7042471860:AAEGGb2usb6ZjZomisNmyEEB1SytBqSXrsM'
CHAT_ID = '770967266'

bot = telebot.TeleBot(BOT_TOKEN)

def send_message(text):
    bot.send_message(CHAT_ID, text)

send_message('Bot에서 보낸 메세지입니다.')