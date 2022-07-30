import json
from pathlib import Path

from flask import Flask, request
import telebot
from telebot.types import Message

import config
from kjbot import bot, SECRET, check_time_and_chat, display_status, check_payment, find_payee, edit_balances

ITEM_FILE = Path(__file__).parent / 'items.json'

app = Flask(__name__)


@app.route('/' + SECRET, methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode('utf-8'))
    bot.process_new_updates([update])
    return 'ok', 200


@bot.message_handler(commands=['start'])
def start(m: Message):
    if not check_time_and_chat(m):
        return

    bot.reply_to(m, 'Hi!')


@bot.message_handler(commands=['help'])
def help(m: Message):
    if not check_time_and_chat(m):
        return

    bot.reply_to(m, config.help_txt, parse_mode='Markdown')


@bot.message_handler(commands=['spent'])
def spent(m: Message):
    if not check_time_and_chat(m):
        return

    amount_flt = check_payment(m)

    if amount_flt == 'no':
        return

    if amount_flt == 0:
        bot.reply_to(m, config.zero_txt)
        return

    info = ['spent']

    balance_before = edit_balances(m, amount_flt, info)
    if balance_before == 0:
        return

    display_status(m, balance_before)

    bot.send_message(config.user1_id, m.text[7:], parse_mode='Markdown')

    bot.send_message(config.user2_id, m.text[7:], parse_mode='Markdown')

    bot.send_message(config.user3_id, m.text[7:], parse_mode='Markdown')


@bot.message_handler(commands=['paid'])
def paid(m: Message):
    if not check_time_and_chat(m):
        return

    amount_flt = check_payment(m)

    if amount_flt == 'no':
        return

    if amount_flt == 0:
        bot.reply_to(m, config.zero_txt)
        return

    paidfrom = m.from_user.id
    paidfrom = str(paidfrom)

    paidto = find_payee(m, paidfrom)
    if paidto == 0:
        return

    info = ['paid', paidfrom, paidto]

    balance_before = edit_balances(m, amount_flt, info)
    if balance_before == 0:
        return

    display_status(m, balance_before)


@bot.message_handler(commands=['status'])
def status(m: Message):
    if not check_time_and_chat(m):
        return

    display_status(m)


@bot.message_handler(commands=['add'])
def add(m: Message):
    if not check_time_and_chat(m):
        return

    with open(ITEM_FILE, 'r', encoding='utf-8') as f:
        items = json.load(f)
        try:
            item = m.text[5:]
        except Exception:
            bot.reply_to(m, 'What do we need son? :D')
            return 0
        items.append(item)

    with open(ITEM_FILE, 'w', encoding='utf-8') as f:
        json.dump(items, f, ensure_ascii=False, indent=4)

    if len(items) != 0:
        msg = ''
        for index, item in enumerate(items):
            msg = msg + '*' + str(index) + ': *' + item + '\n'
    else:
        msg = 'No items'

    bot.reply_to(m, msg, parse_mode='Markdown')


@bot.message_handler(commands=['remove'])
def remove(m: Message):
    if not check_time_and_chat(m):
        return

    with open(ITEM_FILE, 'r', encoding='utf-8') as f:
        items = json.load(f)
        try:
            index = m.text.split(' ')[1]
            item = items.pop(int(index))
        except Exception:
            bot.reply_to(m, 'Give me an appropriate index, will you?')
            return 0

    with open(ITEM_FILE, 'w', encoding='utf-8') as f:
        json.dump(items, f, ensure_ascii=False, indent=4)

    msg = '*' + item + '*' + ' is removed! \n\n'

    for index, item in enumerate(items):
        msg = msg + '*' + str(index) + ': *' + item + '\n'

    bot.reply_to(m, msg, parse_mode='Markdown')


@bot.message_handler(commands=['list'])
def list(m: Message):
    if not check_time_and_chat(m):
        return

    with open(ITEM_FILE, 'r', encoding='utf-8') as f:
        items = json.load(f)

    if len(items) != 0:
        msg = ''
        for index, item in enumerate(items):
            msg = msg + '*' + str(index) + ': *' + item + '\n'
    else:
        msg = 'No items'

    bot.reply_to(m, msg, parse_mode='Markdown')
