# /start
START_GREETING: str = 'Hi there, kjbot at your service!'

# /help
HELP: str = '''
*/start: * You clearly don\'t need this.
*/help: * Replies with this text.
*/paid <x> <y>: * Use this when you gave *x* amount of money to *y*.
*/spent <x> <y>: * Use this when the *x* amount of money you spent on *y* is for all members.
*/status: * Display the current balance.
*/add <x>: * Add *x* to chores/shopping list.
*/list: * Display the chores/shopping items with their indices.
*/remove <x>: * Remove the item with index *x* from the chores/shopping list.
'''

# /paid
VALID_AMT: str = 'Please provide a valid amount'
PAID_TO_WHOM: str = '''
To whom did you pay that:
/paid 100 furkan
'''

# /spent
VALID_AMT_W_DESC: str = '''
Please provide a valid amount with a description:
/spent 1250 rent
'''

# /add
EMPTY_ADD: str = '''
What needs to be added to the list:
/add Buy milk
'''

# /list
NO_ITEMS: str = 'There are no items in the list.'

# /remove
WRONG_INDEX: str = '''
The index you provided is not appropriate. You can see the items with their indices:
/list
'''
