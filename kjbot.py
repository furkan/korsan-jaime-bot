import ast
import json
from pathlib import Path
from time import time
from typing import Dict, List, Tuple

import config  # type: ignore
import replies

BALANCE_FILE: Path = Path(__file__).parent / 'balance.txt'
ITEM_FILE: Path = Path(__file__).parent / 'items.json'

INITIAL_UNIX_TIME: float = time()

users: Dict[str, int] = {
    config.user1_id: 0,
    config.user2_id: 1
}

user_names: List[str] = [
    config.user1_name,
    config.user2_name
]

NUMBER_OF_PEOPLE: int = len(users)


def check_time_and_chat(message_date: int, message_chat_id: int) -> bool:
    new_message: bool = message_date > INITIAL_UNIX_TIME
    correct_chat: bool = message_chat_id == config.chat_id
    return new_message and correct_chat


def expr(code: str) -> float:
    '''Eval a math expression and return the result'''
    code = code.format(**{})

    expr = ast.parse(code, mode='eval')
    code_object = compile(expr, '<string>', 'eval')

    return float(eval(code_object))


def display_status(balance_before: List[str] = ['']) -> str:
    with open(BALANCE_FILE) as file:
        balance: List[str] = file.read().split(',')

    if balance_before != ['']:
        balance_before_strings: List[str] = []
        for i in range(NUMBER_OF_PEOPLE):
            balance_before_strings.append(f'*  <--  *{float(balance_before[i]):.2f}')
    else:
        balance_before_strings = [''] * NUMBER_OF_PEOPLE

    msg = ''
    for i in range(NUMBER_OF_PEOPLE):
        msg += (
            f'*{user_names[i]}:*\n{float(balance[i]):.2f}'
            f'{balance_before_strings[i]}\n'
        )
    return msg


def check_payment(message: str, needs_description: bool) -> Tuple[float, bool]:
    message_words = message.split(' ')

    try:
        amount = message_words[1]
    except Exception:
        return 0.0, False

    if needs_description and len(message_words) < 3:
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


def edit_balances(payer_id: str,
                  amount_flt: float,
                  info: List[str]) -> Tuple[List[str], bool]:
    if payer_id not in users.keys():
        return [''], False

    with open(BALANCE_FILE) as file:
        balance = file.read().split(',')

    balance_before: List[str] = balance

    balance_num: List[float] = [0.0] * NUMBER_OF_PEOPLE

    for i in range(len(balance_num)):
        balance_num[i] = float(balance[i])

    if info[0] == 'spent':
        for i in range(len(balance_num)):
            if i == users[payer_id]:
                try:
                    balance_num[i] += (NUMBER_OF_PEOPLE - 1.0) * amount_flt / NUMBER_OF_PEOPLE
                except Exception:
                    return [''], False
            else:
                try:
                    balance_num[i] -= amount_flt / NUMBER_OF_PEOPLE
                except Exception:
                    return [''], False

    elif info[0] == 'paid':
        try:
            balance_num[users[info[1]]] += amount_flt
            balance_num[users[info[2]]] -= amount_flt
        except Exception:
            return [''], False

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
            return replies.WRONG_INDEX

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
        msg = replies.NO_ITEMS

    return msg
