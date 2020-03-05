from config import Config

class CommandHandler ():

    def __init__(self, bot):
        self.bot = bot
        self.users = {
            Config.user1_id:0,
            Config.user2_id:1,
            Config.user3_id:2
        }

    def display_status(self, chat_id, msg_id, balance_before = ['', '', '']):
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
            self.bot.send_message(chat_id=Config.chat_id, text=msg, reply_to_message_id=msg_id, parse_mode='markdown')
        except:
            self.bot.send_message(chat_id=Config.chat_id, text=msg, parse_mode='markdown')

    def check_payment(self, chat_id, msg_id, text):
        try:
            amount = text.split(' ')[1]
        except:
            self.bot.send_message(chat_id=Config.chat_id, text=Config.empty_txt, reply_to_message_id=msg_id)
            return 0

        try:
            amount_flt = float(amount)
        except:
            self.bot.send_message(chat_id=Config.chat_id, text=Config.not_a_number_txt, reply_to_message_id=msg_id)
            return 0

        return amount_flt

    def find_payee(self, chat_id, msg_id, text):
        try:
            paidto_nickname = text.split(' ')[2]

            if paidto_nickname in Config.user1_nicknames:
                paidto = Config.user1_id
            if paidto_nickname in Config.user2_nicknames:
                paidto = Config.user2_id
            if paidto_nickname in Config.user3_nicknames:
                paidto = Config.user3_id

        except:
            self.bot.send_message(chat_id=Config.chat_id, text=Config.paid_to_whom_text, reply_to_message_id=msg_id)
            return 0

        return paidto

    def edit_balances(self, chat_id, sender_id, msg_id, text, amount_flt, info):

        with open('balance.txt') as file:
            balance = file.read().split(',')

        balance_before = balance

        balance_num = [0,0,0]

        for i in range(len(balance_num)):
            balance_num[i] = float(balance[i])

        if info[0] == 'spent':
            for i in range(len(balance_num)):
                if i == self.users[str(sender_id)]:
                    try:
                        balance_num[i] += 2.0 * amount_flt / 3.0
                    except:
                        self.bot.send_message(chat_id=Config.chat_id, text='nope', reply_to_message_id=msg_id)
                else:
                    try:
                        balance_num[i] -= amount_flt / 3.0
                    except:
                        self.bot.send_message(chat_id=Config.chat_id, text='nope', reply_to_message_id=msg_id)

        elif info[0] == 'paid':
            try:
                balance_num[self.users[info[1]]] += amount_flt
                balance_num[self.users[info[2]]] -= amount_flt
            except:
                self.bot.send_message(chat_id=Config.chat_id, text='nope', reply_to_message_id=msg_id)
                return 0

        with open('balance.txt', 'w') as file:
            data = ''
            for i in range(len(balance_num)):
                data += str(balance_num[i]) + ','

            data += '\n'
            file.write(data)

        return 1

    def spent_callback(self, chat_id, msg_id, sender_id, text):

        amount_flt = check_payment(chat_id, msg_id, text)

        if amount_flt == 0:
            self.bot.send_message(chat_id=Config.chat_id, text=Config.zero_txt, reply_to_message_id=msg_id)
            return

        info = ['spent']

        if edit_balances(chat_id, sender_id, msg_id, text, amount_flt, info) == 0:
            return

        display_status(chat_id, msg_id, balance_before)

        self.bot.send_message(chat_id=Config.user1_id, text=text[7:], parse_mode='markdown')

        self.bot.send_message(chat_id=Config.user2_id, text=text[7:], parse_mode='markdown')

        self.bot.send_message(chat_id=Config.user3_id, text=text[7:], parse_mode='markdown')

    def paid_callback(self, chat_id, msg_id, sender_id, text):

        amount_flt = check_payment(chat_id, msg_id, text)

        if amount_flt == 0:
            self.bot.send_message(chat_id=Config.chat_id, text=Config.zero_txt, reply_to_message_id=msg_id)
            return

        paidfrom = sender_id
        paidfrom = str(paidfrom)

        paidto = find_payee(chat_id, msg_id, text)
        if paidto == 0:
            return

        info = ['paid',paidfrom,paidto]

        if edit_balances(chat_id, sender_id, msg_id, text, amount_flt, info) == 0:
            return

        display_status(chat_id, msg_id, balance_before)

    def status_callback(self, chat_id, msg_id):

        display_status(chat_id, msg_id)

    def handle_commands(self, chat_id, msg_id, sender_id, text):
        if text[0:5] == '/paid':
            paid_callback(chat_id, msg_id, sender_id, text)

        elif text[0:6] == '/spent':
            spent_callback(chat_id, msg_id, sender_id, text)

        elif text[0:7] != '/status':
            status_callback(chat_id, msg_id)

        else:
            return 'message is not a command, but handler was called'
