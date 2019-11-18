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

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def start_callback(update, context):
    if correct_chat(update.message.chat_id):
        msg = "Hi dear master, "
        msg += str(update.message.from_user.username)
        update.message.reply_text(msg)
    else:
        update.message.reply_text('Not the right chat :D')
        return

def help_callback(update, context):
    if correct_chat(update.message.chat_id) is False:
        update.message.reply_text('Not the right chat :D')
        return
    msg = '/help: This long text \n \
/spent {x}: You spent x amount on your own \n \
/paid {x}: You paid x amount to one of the others \n \
/status: Displays the balances of each member \n\n \
Be careful: If you paid the entire amount of a product or a service, you should use \'/spent\'. \n \
Example usage: There are 3 members, and member 1 buys a product worth 3 dollars. \
That member then types \'/spent 3\'. As the others pay back, they type \'/paid 1\'.'
    update.message.reply_text(msg)

def spent_callback(update, context):
    if correct_chat(update.message.chat_id) is False:
        update.message.reply_text('Not the right chat :D')
        return

    try:
        amount = update.message.text.split(' ')[1]
    except:
        update.message.reply_text('How much did you spend?')
        return

    if amount[0] == '0' or amount[0:2] == '-0':
        update.message.reply_text('Please don\'t start with a zero')
        return

    try:
        amount_flt = float(amount)
    except:
        update.message.reply_text('Such a waste!')
        return

    with open('balance.txt') as file:
        balance = file.read().split(',')
    balance_num = [0,0,0]
    for i in range(len(balance_num)):
        balance_num[i] = float(balance[i])

    balance_before = balance
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
    with open('balance.txt', 'w') as file:
        data = ''
        for i in range(len(balance_num)):
            data += str(balance_num[i]) + ','

        data += '\n'
        file.write(data)

    display_status(update, context, balance_before)

    context.bot.send_message(chat_id=config.user1_id, text=update.message.text[7:], parse_mode='markdown')

    context.bot.send_message(chat_id=config.user2_id, text=update.message.text[7:], parse_mode='markdown')

    context.bot.send_message(chat_id=config.user3_id, text=update.message.text[7:], parse_mode='markdown')

def paid_callback(update, context):
    global clickable_button
    if correct_chat(update.message.chat_id) is False:
        update.message.reply_text('Not the right chat :D')
        return

    clickable_button = True
    try:
        amount = update.message.text.split(' ')[1]
    except:
        update.message.reply_text('How much did you pay?')
        return

    if amount[0] == '0' or amount[0:2] == '-0':
        update.message.reply_text('Please don\'t start with a zero')
        return

    try:
        amount_flt = float(amount)
    except:
        update.message.reply_text('We do not accept such payments here!')
        return

    amount = str(amount) + ','

    with open('balance.txt') as file:
        balance = file.read().split(',')

    balances = ',' + str("%.2f" % float(balance[0])) + ',' + str("%.2f" % float(balance[1])) + ',' + str("%.2f" % float(balance[2]))

    if str(update.message.from_user.id) == config.user1_id:
        keyboard = [[telegram.InlineKeyboardButton(config.user2_name, callback_data=amount + config.user1_id[0] + ',' + config.user2_id[0] + balances)],[telegram.InlineKeyboardButton(config.user3_name, callback_data=amount + config.user1_id[0] + ',' + config.user3_id[0] + balances)]]
    elif str(update.message.from_user.id) == config.user2_id:
        keyboard = [[telegram.InlineKeyboardButton(config.user1_name, callback_data=amount + config.user2_id[0] + ',' + config.user1_id[0] + balances)],[telegram.InlineKeyboardButton(config.user3_name, callback_data=amount + config.user2_id[0] + ',' + config.user3_id[0] + balances)]]
    elif str(update.message.from_user.id) == config.user3_id:
        keyboard = [[telegram.InlineKeyboardButton(config.user1_name, callback_data=amount + config.user3_id[0] + ',' + config.user1_id[0] + balances)],[telegram.InlineKeyboardButton(config.user2_name, callback_data=amount + config.user3_id[0] + ',' + config.user2_id[0] + balances)]]
    else:
        update.message.reply_text('Who are you :D')
        return

    reply_markup = telegram.InlineKeyboardMarkup(keyboard)
    update.message.reply_text('To whom did you pay?', reply_markup = reply_markup)

def button_callback(update, context):
    global clickable_button


    # When the button is pressed more than once
    if clickable_button == False:
        return

    clickable_button = False

    query = update.callback_query

    balance_before = [0,0,0]

    amount, paidfrom, paidto = query.data.split(',')[:3]

    #This works because our user ids start with different numbers

    if paidfrom == config.user1_id[0]:
        paidfrom = config.user1_id
    elif paidfrom == config.user3_id[0]:
        paidfrom = config.user3_id
    elif paidfrom == config.user2_id[0]:
        paidfrom = config.user2_id

    if paidto == config.user1_id[0]:
        paidto = config.user1_id
    elif paidto == config.user3_id[0]:
        paidto = config.user3_id
    elif paidto == config.user2_id[0]:
        paidto = config.user2_id

    balance_before = query.data.split(',')[3:6]

    with open('balance.txt') as file:
        balance = file.read().split(',')
    balance_num = [0,0,0]
    for i in range(len(balance_num)):
        balance_num[i] = float(balance[i])

    try:
        balance_num[users[paidfrom]] += float(amount)
        balance_num[users[paidto]]   -= float(amount)
    except:
        update.message.reply_text('Nope')


    with open('balance.txt', 'w') as file:
        data = ''
        for i in range(len(balance_num)):
            data += str(balance_num[i]) + ','

        data += '\n'
        file.write(data)

    display_status(update, context, balance_before)

def status_callback(update,context):
    if correct_chat(update.message.chat_id) is False:
        update.message.reply_text('Not the right chat :D')
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
    dp.add_handler(CallbackQueryHandler(button_callback))
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
