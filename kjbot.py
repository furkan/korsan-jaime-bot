from flask import Flask, request
import telebot
import config
import logging
import time
import ast
import json

TOKEN = config.token
secret = config.secret
url = config.URL + secret

users = {
    config.user1_id:0,
    config.user2_id:1,
    config.user3_id:2
}

initial_unix_date = time.time()
number_of_people = 2.0

logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)

bot = telebot.TeleBot(TOKEN, threaded=False)
bot.remove_webhook()
bot.set_webhook(url=url)

app = Flask(__name__)

def correct_chat(chat_id):
    if chat_id == config.chat_id:
        return True
    else:
        return False

def expr(code, context=None):
    """Eval a math expression and return the result"""
    if not context:
        context = {}
    code = code.format(**context)

    expr = ast.parse(code, mode='eval')
    code_object = compile(expr, '<string>', 'eval')

    return eval(code_object)

def display_status(m, balance_before = ['', '', '']):
    with open('/home/kjbot/korsan-jaime-bot/balance.txt') as file:
        balance = file.read().split(',')

    if balance_before != ['','','']:
        balance_before_strings = ['*  <--  *' + str("%.2f" % float(balance_before[0])), '*  <--  *' + str("%.2f" % float(balance_before[1])), '*  <--  *' + str("%.2f" % float(balance_before[2]))]
    else:
        balance_before_strings = ['','','']

    msg  =  '*'+ config.user1_name + ':*\n' + str("%.2f" % float(balance[0])) + balance_before_strings[0] \
        + '\n*'+ config.user2_name + ': *\n' + str("%.2f" % float(balance[1])) + balance_before_strings[1] \
        + '\n*'+ config.user3_name + ':*\n' + str("%.2f" % float(balance[2])) + balance_before_strings[2]
    try:
        bot.reply_to(m, msg, parse_mode='Markdown')
    except:
        bot.send_message(config.chat_id, msg, parse_mode='Markdown')

def check_payment(m, spentby = 0):
    if correct_chat(m.chat.id) is False:
        bot.reply_to(m, config.wrong_chat_txt)
        return 'no'

    amount_index = 1
    if spentby == 1:
        amount_index = 2

    try:
        amount = m.text.split(' ')[amount_index]
    except:
        #bot.reply_to(m, config.empty_txt)
        bot.reply_to(m, 'MEOW')
        return 'no'

    try:
        amount_flt = float(expr(amount))
    except:
        #bot.reply_to(m, config.not_a_number_txt)
        bot.reply_to(m, 'MEOW')
        return 'no'

    return amount_flt

def find_payee(m,paidfrom):
    try:
        paidto = 0
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

def find_payee_new(m,paidfrom):
    try:
        paidto = 0
        if paidfrom == config.user1_id:
            paidto = config.user2_id
        if paidfrom == config.user2_id:
            paidto = config.user1_id
        if paidfrom == config.user3_id:
            bot.reply_to(m, 'sen bir dur')
    except:
        bot.reply_to(m, config.paid_to_whom_text)
        return 0

    return paidto

def edit_balances(m, amount_flt, info):

    with open('/home/kjbot/korsan-jaime-bot/balance.txt') as file:
        balance = file.read().split(',')

    balance_before = balance

    balance_num = [0,0,0]

    for i in range(len(balance_num)):
        balance_num[i] = float(balance[i])

    if info[0] == 'spent':
        if info[1] == 2:
            bot.reply_to(m, 'yav bir dur')
            return 0
        for i in range(len(balance_num)):
            if i == 2:
                continue # dismiss dikici
            if i == info[1]:
                try:
                    balance_num[i] += (number_of_people - 1.0) * amount_flt / number_of_people
                except:
                    bot.reply_to(m, 'Nope')
                    return 0
            else:
                try:
                    balance_num[i] -= amount_flt / number_of_people
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

    with open('/home/kjbot/korsan-jaime-bot/balance.txt', 'w') as file:
        data = ''
        for i in range(len(balance_num)):
            data += str(balance_num[i]) + ','

        data += '\n'
        file.write(data)

    return balance_before

@app.route('/'+secret, methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode('utf-8'))
    bot.process_new_updates([update])
    return 'ok', 200

@bot.message_handler(commands=['start'])
def start(m):
    if m.date < initial_unix_date:
        return 'old message'

    if not correct_chat(m.chat.id):
        bot.reply_to(m, config.wrong_chat_txt)
        return 'not the right chat'

    bot.reply_to(m, 'Hi!')

@bot.message_handler(commands=['help'])
def help(m):
    if m.date < initial_unix_date:
        return 'old message'

    if not correct_chat(m.chat.id):
        bot.reply_to(m, config.wrong_chat_txt)
        return 'not the right chat'

    bot.reply_to(m, config.help_txt, parse_mode='Markdown')

@bot.message_handler(commands=['spent'])
def spent(m):
    if m.date < initial_unix_date:
        return 'old message'

    if not correct_chat(m.chat.id):
        bot.reply_to(m, config.wrong_chat_txt)
        return 'not the right chat'

    amount_flt = check_payment(m)

    if amount_flt == 'no':
        return

    if amount_flt == 0:
        #bot.reply_to(m, config.zero_txt)
        bot.reply_to(m, 'MEOW')
        return

    try:
        reason = m.text.split(' ')[2]
    except:
        # bot.reply_to(m, 'What did you spend it on homie :D')
        bot.reply_to(m, 'MEOW')
        return 0

    info = ['spent', users[str(m.from_user.id)]]

    balance_before = edit_balances(m,amount_flt,info)
    if balance_before == 0:
        return

    display_status(m, balance_before)

    bot.send_message(config.user1_id, m.text[7:], parse_mode='Markdown')

    bot.send_message(config.user2_id, m.text[7:], parse_mode='Markdown')

#    bot.send_message(config.user3_id, m.text[7:], parse_mode='Markdown')


@bot.message_handler(commands=['paid'])
def paid(m):
    if m.date < initial_unix_date:
        return 'old message'

    if not correct_chat(m.chat.id):
        bot.reply_to(m, config.wrong_chat_txt)
        return 'not the right chat'

    amount_flt = check_payment(m)

    if amount_flt == 'no':
        return

    if amount_flt == 0:
        #bot.reply_to(m, config.zero_txt)
        bot.reply_to(m, 'MEOW')
        return

    paidfrom = m.from_user.id
    paidfrom = str(paidfrom)

    paidto = find_payee_new(m,paidfrom)
    if paidto == 0:
        return

    info = ['paid',paidfrom,paidto]

    balance_before = edit_balances(m,amount_flt,info)
    if balance_before == 0:
        return

    display_status(m, balance_before)

@bot.message_handler(commands=['status'])
def status(m):
    if m.date < initial_unix_date:
        return 'old message'

    if not correct_chat(m.chat.id):
        bot.reply_to(m, config.wrong_chat_txt)
        return 'not the right chat'

    display_status(m)


@bot.message_handler(commands=['add'])
def add(m):
    if m.date < initial_unix_date:
        return 'old message'

    if not correct_chat(m.chat.id):
        bot.reply_to(m, config.wrong_chat_txt)
        return 'not the right chat'

    with open('/home/kjbot/korsan-jaime-bot/items.json', 'r', encoding='utf-8') as f:
        items = json.load(f)
        try:
            item = m.text[5:]
        except:
            #bot.reply_to(m, 'What do we need son? :D')
            bot.reply_to(m, 'MEOW')
            return 0
        items.append(item)

    with open('/home/kjbot/korsan-jaime-bot/items.json', 'w', encoding='utf-8') as f:
        json.dump(items, f, ensure_ascii=False, indent=4)

    if len(items) != 0:
        msg = ''
        for index, item in enumerate(items):
            msg = msg + '*' + str(index) + ': *' + item + '\n'
    else:
        msg = 'No items'

    bot.reply_to(m, msg, parse_mode='Markdown')

@bot.message_handler(commands=['remove'])
def remove(m):
    if m.date < initial_unix_date:
        return 'old message'

    if not correct_chat(m.chat.id):
        bot.reply_to(m, config.wrong_chat_txt)
        return 'not the right chat'

    with open('/home/kjbot/korsan-jaime-bot/items.json', 'r', encoding='utf-8') as f:
        items = json.load(f)
        try:
            index = m.text.split(' ')[1]
            item = items.pop(int(index))
        except:
            #bot.reply_to(m, 'Give me an appropriate index, will you?')
            bot.reply_to(m, 'MEOW')
            return 0

    with open('/home/kjbot/korsan-jaime-bot/items.json', 'w', encoding='utf-8') as f:
        json.dump(items, f, ensure_ascii=False, indent=4)

    msg = '*' + item + '*' + ' is removed! \n\n'

    for index, item in enumerate(items):
        msg = msg + '*' + str(index) + ': *' + item + '\n'

    bot.reply_to(m, msg, parse_mode='Markdown')

@bot.message_handler(commands=['list'])
def list(m):
    if m.date < initial_unix_date:
        return 'old message'

    if not correct_chat(m.chat.id):
        bot.reply_to(m, config.wrong_chat_txt)
        return 'not the right chat'

    with open('/home/kjbot/korsan-jaime-bot/items.json', 'r', encoding='utf-8') as f:
        items = json.load(f)

    if len(items) != 0:
        msg = ''
        for index, item in enumerate(items):
            msg = msg + '*' + str(index) + ': *' + item + '\n'
    else:
        msg = 'No items'

    bot.reply_to(m, msg, parse_mode='Markdown')

