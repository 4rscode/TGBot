from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


kb = ReplyKeyboardMarkup(resize_keyboard=True)  # клавиатура №1 стартовая клавиатура
b3 = KeyboardButton(text='Описание')
b4 = KeyboardButton(text='Расписание')
b5 = KeyboardButton(text='Уведомления')
kb.add(b3, b4).add(b5)

kb2 = ReplyKeyboardMarkup(resize_keyboard=True)
b21 = KeyboardButton(text='Новое событие')
b22 = KeyboardButton(text='Удалить событие')
b23 = KeyboardButton(text='Показать расписание')
b24 = KeyboardButton(text='Главное меню',
                     callback_data='back1')
kb2.add(b21, b22).add(b23).add(b24)

kb1 = ReplyKeyboardMarkup(resize_keyboard=True)  # инлайн клавиатура №1 клавиатура для выбора дня недели
b11 = KeyboardButton(text='Понедельник')
b12 = KeyboardButton(text='Вторник')
b13 = KeyboardButton(text='Среда')
b14 = KeyboardButton(text='Четверг')
b15 = KeyboardButton(text='Пятница')
b16 = KeyboardButton(text='Суббота')
b17 = KeyboardButton(text='Воскресенье')
b18 = KeyboardButton(text='Назад')
kb1.add(b11, b12).add(b13, b14).add(b15, b16).add(b17, b18)


kb11 = ReplyKeyboardMarkup(resize_keyboard=True)  # инлайн клавиатура №1 клавиатура для выбора дня недели
b111 = KeyboardButton(text='Понедельник')
b121 = KeyboardButton(text='Вторник')
b131 = KeyboardButton(text='Среда')
b141 = KeyboardButton(text='Четверг')
b151 = KeyboardButton(text='Пятница')
b161 = KeyboardButton(text='Суббота')
b171 = KeyboardButton(text='Воскресенье')
b181 = KeyboardButton(text='Вернуться назад')
kb11.add(b111, b121).add(b131, b141).add(b151, b161).add(b171, b181)


kb3 = ReplyKeyboardMarkup(resize_keyboard=True)
b31 = InlineKeyboardButton('На день')
b32 = InlineKeyboardButton('На неделю')
b33 = InlineKeyboardButton('Назад')
kb3.add(b31, b32).add(b33)


kb4 = ReplyKeyboardMarkup(resize_keyboard=True)
b41 = KeyboardButton(text='Включить ')
b42 = KeyboardButton(text='Выключить')
b43 = KeyboardButton(text='Изменить время')
b44 = KeyboardButton(text='Главное меню',
                     callback_data='back1')
kb4.add(b41, b42).add(b43).add(b44)

kb5 = ReplyKeyboardMarkup(resize_keyboard=True)
kb51 = KeyboardButton(text='Изменить время')
kb52 = KeyboardButton(text='Вернуться назад')
kb5.add(kb51, kb52)

kb227 = ReplyKeyboardMarkup(resize_keyboard=True)
b1 = KeyboardButton(text='Назад')
kb227.add(b1)