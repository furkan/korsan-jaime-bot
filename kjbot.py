from flask import Flask, request
import telebot
import config
import logging

TOKEN = config.token
secret = config.secret
url = config.URL + secret

logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)

global bot
bot = telebot.TeleBot(TOKEN, threaded=False)
bot.remove_webhook()
bot.set_webhook(url=url)

app = Flask(__name__)

def correct_chat(chat_id):
    if chat_id == config.chat_id:
        return True
    else:
        return False

def display_status(m, balance_before = ['', '', '']):
    with open('balance.txt') as file:
        balance = file.read().split(',')

    if balance_before != ['','','']:
        balance_before_strings = ['*  <--  *' + str("%.2f" % float(balance_before[0])), '*  <--  *' + str("%.2f" % float(balance_before[1])), '*  <--  *' + str("%.2f" % float(balance_before[2]))]
    else:
        balance_before_strings = ['','','']

    msg  =  '*furkan:*\n' + str("%.2f" % float(balance[0])) + balance_before_strings[0] \
        + '\n*tanış: *\n' + str("%.2f" % float(balance[1])) + balance_before_strings[1] \
        + '\n*dikici:*\n' + str("%.2f" % float(balance[2])) + balance_before_strings[2]
    try:
        bot.reply_to(m, msg, parse_mode='Markdown')
    except:
        bot.send_message(config.chat_id, msg, parse_mode='Markdown')

def check_payment(m):
    if correct_chat(m.chat.id) is False:
        bot.reply_to(m, config.wrong_chat_txt)
        return 0

    try:
        amount = m.text.split(' ')[1]
    except:
        bot.reply_to(m, config.empty_txt)
        return 0

    try:
        amount_flt = float(amount)
    except:
        bot.reply_to(m, config.not_a_number_txt)
        return 0

    return amount_flt

def find_payee(m,paidfrom):
    try:
        paidto_nickname = m.text.split(' ')[2]
        if paidfrom == config.user1_id:
            if paidto_nickname in config.user2_nicknames:
                paidto = config.user2_id
            if paidto_nickname in config.user3_nicknames:
                paidto = config.user3_id
        if paidfrom == config.user2_id:
            if paidto_nickname in config.user1_nicknames:
                paidto = config.user1_id
            if paidto_nickname in config.user3_nicknames:
                paidto = config.user3_id
        if paidfrom == config.user3_id:
            if paidto_nickname in config.user1_nicknames:
                paidto = config.user1_id
            if paidto_nickname in config.user2_nicknames:
                paidto = config.user2_id
    except:
        bot.reply_to(m, config.paid_to_whom_text)
        return 0

    return paidto

def edit_balances(m, amount_flt, info):

    with open('balance.txt') as file:
        balance = file.read().split(',')

    balance_before = balance

    balance_num = [0,0,0]

    for i in range(len(balance_num)):
        balance_num[i] = float(balance[i])

    if info[0] == 'spent':
        for i in range(len(balance_num)):
            if i == users[str(m.from_user.id)]:
                try:
                    balance_num[i] += 2.0 * amount_flt / 3.0
                except:
                    bot.reply_to(m, 'Nope')
                    return 0
            else:
                try:
                    balance_num[i] -= amount_flt / 3.0
                except:
                    bot.reply_to(m, 'Nope')
                    return 0

    elif info[0] == 'paid':
        try:
            balance_num[users[info[1]]] += amount_flt
            balance_num[users[info[2]]] -= amount_flt
        except:
            bot.reply_to(m, 'Nope')
            return 0

    with open('balance.txt', 'w') as file:
        data = ''
        for i in range(len(balance_num)):
            data += str(balance_num[i]) + ','

        data += '\n'
        file.write(data)

    return balance_before

@app.route('/'+secret+'/', methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode('utf-8'))
    bot.process_new_updates([update])
    return 'ok', 200

@bot.message_handler(commands=['start'])
def start(m):
    if not correct_chat(m.chat.id):
        bot.reply_to(m, config.wrong_chat_txt)
        return 'not the right chat'

    bot.reply_to(m, 'Hi!')

@bot.message_handler(commands=['help'])
def help(m):
    if not correct_chat(m.chat.id):
        bot.reply_to(m, config.wrong_chat_txt)
        return 'not the right chat'

    bot.reply_to(m, config.help_txt)

@bot.message_handler(commands=['spent'])
def spent(m):
    if not correct_chat(m.chat.id):
        bot.reply_to(m, config.wrong_chat_txt)
        return 'not the right chat'

    amount_flt = check_payment(m)

    if amount_flt == 0:
        bot.reply_to(m, config.zero_txt)
        return

    info = ['spent']

    balance_before = edit_balances(m,amount_flt,info)
    if balance_before == 0:
        return

    display_status(m, balance_before)

    bot.send_message(config.user1_id, m.text[7:], parse_mode='Markdown')

    bot.send_message(config.user2_id, m.text[7:], parse_mode='Markdown')

    bot.send_message(config.user3_id, m.text[7:], parse_mode='Markdown')

@bot.message_handler(commands=['paid'])
def paid(m):
    if not correct_chat(m.chat.id):
        bot.reply_to(m, config.wrong_chat_txt)
        return 'not the right chat'

    amount_flt = check_payment(m)

    if amount_flt == 0:
        bot.reply_to(m, config.zero_txt)
        return

    paidfrom = m.from_user.id
    paidfrom = str(paidfrom)

    paidto = find_payee(m,paidfrom)
    if paidto == 0:
        return

    info = ['paid',paidfrom,paidto]

    balance_before = edit_balances(m,amount_flt,info)
    if balance_before == 0:
        return

    display_status(m, balance_before)

@bot.message_handler(commands=['status'])
def status(m):
    if not correct_chat(m.chat.id):
        bot.reply_to(m, config.wrong_chat_txt)
        return 'not the right chat'

    display_status(m)
