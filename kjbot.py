import ast
import logging
from pathlib import Path
from time import time

import telebot

import config

BALANCE_FILE = Path('balance.txt')
ITEM_FILE = Path('items.json')

INITIAL_UNIX_TIME = time()

TOKEN = config.token
SECRET = config.SECRET
URL = config.URL + SECRET

NUMBER_OF_PEOPLE = 3.0

logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)

bot = telebot.TeleBot(TOKEN, threaded=False)
bot.remove_webhook()
bot.set_webhook(url=URL)

users = {
    config.user1_id: 0,
    config.user2_id: 1,
    config.user3_id: 2
}


def check_time_and_chat(m) -> bool:
    if m.date < INITIAL_UNIX_TIME:
        return False

    if m.chat.id != config.chat_id:
        bot.reply_to(m, config.wrong_chat_txt)
        return False

    return True


def expr(code, context=None):
    """Eval a math expression and return the result"""
    if not context:
        context = {}
    code = code.format(**context)

    expr = ast.parse(code, mode='eval')
    code_object = compile(expr, '<string>', 'eval')

    return eval(code_object)


def display_status(m, balance_before=['', '', '']):
    with open(BALANCE_FILE) as file:
        balance = file.read().split(',')

    if balance_before != ['', '', '']:
        balance_before_strings = ['*  <--  *' + str("%.2f" % float(balance_before[0])), '*  <--  *' + str("%.2f" % float(balance_before[1])), '*  <--  *' + str("%.2f" % float(balance_before[2]))]
    else:
        balance_before_strings = ['', '', '']

    msg = '*' + config.user1_name + ':*\n' + str("%.2f" % float(balance[0])) + balance_before_strings[0] \
              + '\n*' + config.user2_name + ': *\n' + str("%.2f" % float(balance[1])) + balance_before_strings[1] \
              + '\n*' + config.user3_name + ':*\n' + str("%.2f" % float(balance[2])) + balance_before_strings[2]
    try:
        bot.reply_to(m, msg, parse_mode='Markdown')
    except Exception:
        bot.send_message(config.chat_id, msg, parse_mode='Markdown')


def check_payment(m):
    try:
        amount = m.text.split(' ')[1]
    except Exception:
        bot.reply_to(m, config.empty_txt)
        return 'no'

    try:
        amount_flt = float(expr(amount))
    except Exception:
        bot.reply_to(m, config.not_a_number_txt)
        return 'no'

    return amount_flt


def find_payee(m, paidfrom):
    try:
        paidto_nickname = m.text.split(' ')[2]
        paidto = 0
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
    except Exception:
        bot.reply_to(m, config.paid_to_whom_text)
        return 0

    return paidto


def edit_balances(m, amount_flt, info):
    with open(BALANCE_FILE) as file:
        balance = file.read().split(',')

    balance_before = balance

    balance_num = [0, 0, 0]

    for i in range(len(balance_num)):
        balance_num[i] = float(balance[i])

    if info[0] == 'spent':
        for i in range(len(balance_num)):
            if i == users[str(m.from_user.id)]:
                try:
                    balance_num[i] += (NUMBER_OF_PEOPLE - 1.0) * amount_flt / NUMBER_OF_PEOPLE
                except Exception:
                    bot.reply_to(m, 'Nope')
                    return 0
            else:
                try:
                    balance_num[i] -= amount_flt / NUMBER_OF_PEOPLE
                except Exception:
                    bot.reply_to(m, 'Nope')
                    return 0

    elif info[0] == 'paid':
        try:
            balance_num[users[info[1]]] += amount_flt
            balance_num[users[info[2]]] -= amount_flt
        except Exception:
            bot.reply_to(m, 'Nope')
            return 0

    with open(BALANCE_FILE, 'w') as file:
        data = ''
        for i in range(len(balance_num)):
            data += str(balance_num[i]) + ','

        data += '\n'
        file.write(data)

    return balance_before
