from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

keyboard_user = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(
            text='Играть'
        )
    ],
    [
        KeyboardButton(
            text='Баланс'
        ),
        KeyboardButton(
            text='Рефералы'
        )
    ]
], resize_keyboard=True, one_time_keyboard=False)