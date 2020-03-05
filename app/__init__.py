from flask import Flask, request
from config import Config
import telegram
from app.commandhandler import CommandHandler

global bot
global TOKEN
TOKEN = Config.token
bot = telegram.Bot(token=TOKEN)
URL = Config.URL

app = Flask(__name__)

ch = CommandHandler(bot)

@app.route('/{}'.format(TOKEN), methods=['POST'])
def respond():
    # retrieve the message in JSON and then transform it to Telegram object
    update = telegram.Update.de_json(request.get_json(force=True), bot)

    chat_id   = update.message.chat.id
    msg_id    = update.message.message_id
    sender_id = update.message.from_user.id

    if chat_id != Config.chat_id:
        bot.send_message(chat_id=chat_id, text=Config.wrong_chat_txt, reply_to_message_id=msg_id)
        return 'wrong chat'

    # Telegram understands UTF-8, so encode text for unicode compatibility
    text = update.message.text.encode('utf-8').decode()

    if (text[0:5] != '/paid') and (text[0:6] != '/spent') and (text[0:7] != '/status'):
        return 'message is not a command'

    print("got text message :", text)

    ch.handle_commands(chat_id, msg_id, sender_id, text)

    return 'ok'

@app.route('/setwebhook', methods=['GET', 'POST'])
def set_webhook():
    try:
        s = bot.setWebhook('{URL}{HOOK}'.format(URL=URL, HOOK=TOKEN))
    except:
        return "hmmm"

    if s:
        return "webhook setup ok"
    else:
        return "webhook setup failed"

@app.route('/')
def index():
    return '.'
