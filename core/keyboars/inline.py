from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

keyboard_balance = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text='Пополнить баланс',
            callback_data='refillbalance'
        )
    ],
    [
        InlineKeyboardButton(
            text='Вывод баланса',
            callback_data='requestbalance'
        )
    ]
])

cancel_redill_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text='Отменить пополнение баланса',
            callback_data='cancelrefill'
        )
    ]
])


def keyboard_for_admin(user_id, sum):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Написать пользователю',
                url=f'tg://user?id={user_id}'
            )
        ],
        [
            InlineKeyboardButton(
                text='Баланс выведен',
                callback_data=f'requestbalancecomplete|{user_id}|{sum}'
            )
        ]
    ])

refill_balance = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text='Пополнить баланс',
            callback_data='refillbalance'
        )
    ]
])

you_ready = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text='Я готов',
            callback_data='youready'
        )
    ]
])