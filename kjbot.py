import ast
from pathlib import Path
from time import time
from typing import List, Tuple
import json

from telebot.types import Message

import config

BALANCE_FILE: Path = Path(__file__).parent / 'balance.txt'
ITEM_FILE: Path = Path(__file__).parent / 'item.json'

INITIAL_UNIX_TIME: float = time()

users: dict = {
    config.user1_id: 0,
    config.user2_id: 1,
    config.user3_id: 2
}

NUMBER_OF_PEOPLE: int = len(users)


def check_time_and_chat(m: Message) -> bool:
    new_message: bool = m.date > INITIAL_UNIX_TIME
    correct_chat: bool = m.chat.id == config.chat_id
    return new_message and correct_chat


def expr(code: str) -> float:
    '''Eval a math expression and return the result'''
    code = code.format(**{})

    expr = ast.parse(code, mode='eval')
    code_object = compile(expr, '<string>', 'eval')

    return float(eval(code_object))


def display_status(balance_before: List[str] = ['', '', '']) -> str:
    with open(BALANCE_FILE) as file:
        balance: List[str] = file.read().split(',')

    if balance_before != ['', '', '']:
        balance_before_strings = [f'*  <--  *{float(balance_before[0]):.2f}',
                                  f'*  <--  *{float(balance_before[1]):.2f}',
                                  f'*  <--  *{float(balance_before[2]):.2f}']
        # TODO: Stop hardcoding these to work for only 3 people
    else:
        balance_before_strings = ['', '', '']

    msg = (
        f'*{config.user1_name}:*\n{float(balance[0]):.2f}{balance_before_strings[0]}\n'
        f'*{config.user2_name}:*\n{float(balance[1]):.2f}{balance_before_strings[1]}\n'
        f'*{config.user3_name}:*\n{float(balance[2]):.2f}{balance_before_strings[2]}\n'
    )
    return msg


def check_payment(message: str) -> Tuple[float, bool]:
    try:
        amount = message.split(' ')[1]
    except Exception:
        return 0.0, False

    try:
        amount_flt = expr(amount)
    except Exception:
        return 0.0, False

    if amount_flt == 0.0:
        return 0.0, False

    return amount_flt, True


def find_payee(paidfrom: str) -> str:
    paidto = ''
    if paidfrom == config.user1_id:
        paidto = config.user2_id
    if paidfrom == config.user2_id:
        paidto = config.user1_id
    return paidto


def edit_balances(payer_id: str, amount_flt: float, info: List) -> Tuple[List[str], bool]:
    with open(BALANCE_FILE) as file:
        balance = file.read().split(',')

    balance_before: List[str] = balance

    balance_num: List[float] = [0.0, 0.0, 0.0]

    for i in range(len(balance_num)):
        balance_num[i] = float(balance[i])

    if info[0] == 'spent':
        for i in range(len(balance_num)):
            if i == users[payer_id]:
                try:
                    balance_num[i] += (NUMBER_OF_PEOPLE - 1.0) * amount_flt / NUMBER_OF_PEOPLE
                except Exception:
                    return ['', '', ''], False
            else:
                try:
                    balance_num[i] -= amount_flt / NUMBER_OF_PEOPLE
                except Exception:
                    return ['', '', ''], False

    elif info[0] == 'paid':
        try:
            balance_num[users[info[1]]] += amount_flt
            balance_num[users[info[2]]] -= amount_flt
        except Exception:
            return ['', '', ''], False

    with open(BALANCE_FILE, 'w') as file:
        data = ''
        for i in range(len(balance_num)):
            data += str(balance_num[i]) + ','

        data += '\n'
        file.write(data)

    return balance_before, True


def add_item(item: str) -> str:
    with open(ITEM_FILE, 'r', encoding='utf-8') as f:
        items = json.load(f)
        items.append(item)

    with open(ITEM_FILE, 'w', encoding='utf-8') as f:
        json.dump(items, f, ensure_ascii=False, indent=4)

    msg = ''
    for index, item in enumerate(items):
        msg = msg + f'*{index}: *{item}\n'

    return msg


def remove_item(index: int) -> str:
    with open(ITEM_FILE, 'r', encoding='utf-8') as f:
        items = json.load(f)
        try:
            item = items.pop(index)
        except Exception:
            return 'WRONG_INDEX'

    with open(ITEM_FILE, 'w', encoding='utf-8') as f:
        json.dump(items, f, ensure_ascii=False, indent=4)

    msg = f'*{item}*' + ' is removed! \n\n'

    for index, item in enumerate(items):
        msg = msg + f'*{index}: *{item}\n'

    return msg


def list_items() -> str:
    with open(ITEM_FILE, 'r', encoding='utf-8') as f:
        items = json.load(f)

    if len(items) != 0:
        msg = ''
        for index, item in enumerate(items):
            msg = msg + f'*{index}: *{item}\n'
    else:
        msg = 'No items'

    return msg
