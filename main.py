import logging

import telebot  # type: ignore
from flask import Flask
from telebot.types import Message  # type: ignore

import config  # type: ignore
import replies
from kjbot import (add_item, check_payment, check_time_and_chat,
                   display_status, edit_balances, find_payee, list_items,
                   remove_item, users)

app = Flask(__name__)

TOKEN: str = config.token
URL: str = config.URL + TOKEN

logger: logging.Logger = telebot.logger
logger.setLevel(logging.DEBUG)

bot: telebot.TeleBot = telebot.TeleBot(TOKEN, threaded=False)


@bot.message_handler(commands=['start'])
def start(m: Message) -> None:
    if not check_time_and_chat(m.date, m.chat.id):
        return

    bot.reply_to(m, replies.START_GREETING)


@bot.message_handler(commands=['help'])
def help(m: Message) -> None:
    if not check_time_and_chat(m.date, m.chat.id):
        return

    bot.reply_to(m, replies.HELP, parse_mode='Markdown')


@bot.message_handler(commands=['spent'])
def spent(m: Message) -> None:
    if not check_time_and_chat(m.date, m.chat.id):
        return

    amount_flt, valid_number = check_payment(m.text, needs_description=True)

    if not valid_number:
        bot.reply_to(m, replies.VALID_AMT_W_DESC)
        return

    info = ['spent']

    balance_before, ok = edit_balances(str(m.from_user.id), amount_flt, info)
    if not ok:
        return

    msg = display_status(balance_before)

    try:
        bot.reply_to(m, msg, parse_mode='Markdown')
    except Exception:
        bot.send_message(config.chat_id, msg, parse_mode='Markdown')

    for user_id in users.keys():
        bot.send_message(user_id, m.text[7:], parse_mode='Markdown')


@bot.message_handler(commands=['paid'])
def paid(m: Message) -> None:
    if not check_time_and_chat(m.date, m.chat.id):
        return

    amount_flt, valid_number = check_payment(m.text, needs_description=False)

    if not valid_number:
        bot.reply_to(m, replies.VALID_AMT)
        return

    paidfrom = m.from_user.id
    paidfrom = str(paidfrom)

    paidto = find_payee(paidfrom)
    if paidto == '':
        bot.reply_to(m, replies.PAID_TO_WHOM)
        return

    info = ['paid', paidfrom, paidto]

    balance_before, ok = edit_balances(str(m.from_user.id), amount_flt, info)
    if not ok:
        return

    msg = display_status(balance_before)

    try:
        bot.reply_to(m, msg, parse_mode='Markdown')
    except Exception:
        bot.send_message(config.chat_id, msg, parse_mode='Markdown')


@bot.message_handler(commands=['status'])
def status(m: Message) -> None:
    if not check_time_and_chat(m.date, m.chat.id):
        return

    msg = display_status()

    try:
        bot.reply_to(m, msg, parse_mode='Markdown')
    except Exception:
        bot.send_message(config.chat_id, msg, parse_mode='Markdown')


@bot.message_handler(commands=['add'])
def add(m: Message) -> None:
    if not check_time_and_chat(m.date, m.chat.id):
        return

    try:
        item: str = m.text[5:]
    except Exception:
        bot.reply_to(m, replies.EMPTY_ADD)
        return

    if item == '':
        bot.reply_to(m, replies.EMPTY_ADD)
        return

    msg = add_item(item)

    bot.reply_to(m, msg, parse_mode='Markdown')


@bot.message_handler(commands=['remove'])
def remove(m: Message) -> None:
    if not check_time_and_chat(m.date, m.chat.id):
        return

    try:
        index = int(m.text.split(' ')[1])
    except Exception:
        bot.reply_to(m, replies.WRONG_INDEX)
        return

    msg = remove_item(index)

    bot.reply_to(m, msg, parse_mode='Markdown')


@bot.message_handler(commands=['list'])
def list(m: Message) -> None:
    if not check_time_and_chat(m.date, m.chat.id):
        return

    msg = list_items()

    bot.reply_to(m, msg, parse_mode='Markdown')


bot.infinity_polling()
