import telegram
import asyncio


BOT_TOKEN = ''
CHAT_ID = ''
text = 'Bot에서 보낸 메세지입니다.'

bot = telegram.Bot(token = BOT_TOKEN)
asyncio.run(bot.sendMessage(chat_id=CHAT_ID, text=text))