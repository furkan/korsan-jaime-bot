import logging
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
import telegram
from telegram import ParseMode
import config

clickable_button = True

users = {
    config.user1_id:0,
    config.user2_id:1,
    config.user3_id:2
}

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def correct_chat(chat_id):
    if chat_id == config.chat_id:
        return True
    else:
        return False

def display_status(update, context, balance_before = ['', '', '']):
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
        update.message.reply_text(text=msg, parse_mode='markdown')
    except:
        context.bot.send_message(chat_id=config.chat_id, text=msg, parse_mode='markdown')

def check_payment(update, context):
    if correct_chat(update.message.chat_id) is False:
        update.message.reply_text(config.wrong_chat_txt)
        return 0

    try:
        amount = update.message.text.split(' ')[1]
    except:
        update.message.reply_text(config.empty_txt)
        return 0

    try:
        amount_flt = float(amount)
    except:
        update.message.reply_text(config.not_a_number_txt)
        return 0

    return amount_flt

def find_payee(update,context,paidfrom):
    try:
        paidto_nickname = update.message.text.split(' ')[2]
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
        update.message.reply_text(config.paid_to_whom_text)
        return 0

    return paidto

def edit_balances(update,context,amount_flt,info):

    with open('balance.txt') as file:
        balance = file.read().split(',')

    balance_before = balance

    balance_num = [0,0,0]

    for i in range(len(balance_num)):
        balance_num[i] = float(balance[i])

    if info[0] == 'spent':
        for i in range(len(balance_num)):
            if i == users[str(update.message.from_user.id)]:
                try:
                    balance_num[i] += 2.0 * amount_flt / 3.0
                except:
                    update.message.reply_text('Nope')
            else:
                try:
                    balance_num[i] -= amount_flt / 3.0
                except:
                    update.message.reply_text('Nope')

    elif info[0] == 'paid':
        try:
            balance_num[users[info[1]]] += amount_flt
            balance_num[users[info[2]]] -= amount_flt
        except:
            update.message.reply_text('Nope')
            return 0

    with open('balance.txt', 'w') as file:
        data = ''
        for i in range(len(balance_num)):
            data += str(balance_num[i]) + ','

        data += '\n'
        file.write(data)

    return 1

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def start_callback(update, context):
    if correct_chat(update.message.chat_id):
        msg = "Hi dear master, "
        msg += str(update.message.from_user.username)
        update.message.reply_text(msg)
    else:
        update.message.reply_text(config.wrong_chat_txt)
        return

def help_callback(update, context):
    if correct_chat(update.message.chat_id) is False:
        update.message.reply_text(config.wrong_chat_txt)
        return
    update.message.reply_text(config.help_txt)

def spent_callback(update, context):

    amount_flt = check_payment(update, context)

    if amount_flt == 0:
        update.message.reply_text(config.zero_txt)
        return

    info = ['spent']

    if edit_balances(update,context,amount_flt,info) == 0:
        return

    display_status(update, context, balance_before)

    context.bot.send_message(chat_id=config.user1_id, text=update.message.text[7:], parse_mode='markdown')

    context.bot.send_message(chat_id=config.user2_id, text=update.message.text[7:], parse_mode='markdown')

    context.bot.send_message(chat_id=config.user3_id, text=update.message.text[7:], parse_mode='markdown')

def paid_callback(update, context):

    amount_flt = check_payment(update, context)

    if amount_flt == 0:
        update.message.reply_text(config.zero_txt)
        return

    paidfrom = update.message.from_user.id
    paidfrom = str(paidfrom)

    paidto = find_payee(update,context,paidfrom)
    if paidto == 0:
        return

    info = ['paid',paidfrom,paidto]

    if edit_balances(update,context,amount_flt,info) == 0:
        return

    display_status(update, context, balance_before)

def status_callback(update,context):
    if correct_chat(update.message.chat_id) is False:
        update.message.reply_text(config.wrong_chat_txt)
        return

    display_status(update, context)

def main():
    updater = Updater(config.token, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # handlers
    dp.add_handler(CommandHandler("start", start_callback))
    dp.add_handler(CommandHandler("help", help_callback))
    dp.add_handler(CommandHandler("spent", spent_callback))
    dp.add_handler(CommandHandler("paid", paid_callback))
    dp.add_handler(CommandHandler("status", status_callback))
 #   dp.add_handler(CommandHandler("IBAN", IBAN_callback)) #ONUR

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
