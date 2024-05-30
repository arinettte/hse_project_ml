from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup)

main = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Listen your Emotion 🎼')],
                                     [KeyboardButton(text='Оцените приложение 🤩'),
                                      KeyboardButton(text="О нас ❓")],
                                     [KeyboardButton(text="Чат с поддержкой 🫶")]],
                           resize_keyboard=True,
                           input_field_placeholder='Что вас интересует?')

password = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Отмена")]], resize_keyboard=True, one_time_keyboard=True,
                               selective=True)

login = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Log in", callback_data='login')]])

rating = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Оставить отзыв ✍️", callback_data='words'), ],
    [InlineKeyboardButton(text="Оценить приложение ⭐", callback_data='number')]
]
)

general = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Да,все хорошо", callback_data='yes'),
     InlineKeyboardButton(text="Нет,выберу другой вариант", callback_data='no')],
])

rate = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="1 ⭐", callback_data='11'),
     InlineKeyboardButton(text="2 ⭐", callback_data='12'),
     InlineKeyboardButton(text="3 ⭐", callback_data='13'),
     InlineKeyboardButton(text="4 ⭐", callback_data='14'),
     InlineKeyboardButton(text="5 ⭐", callback_data='15')]
]
)

service = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="1 ⭐", callback_data='21'),
     InlineKeyboardButton(text="2 ⭐", callback_data='22'),
     InlineKeyboardButton(text="3 ⭐", callback_data='23'),
     InlineKeyboardButton(text="4 ⭐", callback_data='24'),
     InlineKeyboardButton(text="5 ⭐", callback_data='25')]
]
)

interface = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="1 ⭐", callback_data='31'),
     InlineKeyboardButton(text="2 ⭐", callback_data='32'),
     InlineKeyboardButton(text="3 ⭐", callback_data='33'),
     InlineKeyboardButton(text="4 ⭐", callback_data='34'),
     InlineKeyboardButton(text="5 ⭐", callback_data='35')]
]
)
