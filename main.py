import asyncio
import time
from datetime import datetime
from aiogram import Bot, Dispatcher, executor, types
from config import TOKEN_API1
from storage import COMMANDS, DESCRIPTION, CLARIFICATION, DAYS, DAYZ
from keyboards import kb, kb1, kb11, kb2, kb3, kb4, kb227
from aiogram.dispatcher.filters import Text
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State, StatesGroupMeta
from sqlite import db_start, new_event, get_week_events, dell_event, get_day_events, check_profile, add_profile, \
    get_profiles, get_user, edit_notif_state, edit_notif_time

storage = MemoryStorage()
bot = Bot(TOKEN_API1)
dp = Dispatcher(bot=bot,
                storage=storage)


class ClientStatesGroup(StatesGroup):

    registration = State()

    day = State()
    event = State()

    dell = State()
    dell_compl = State()

    show_event = State()
    event_day = State()

    notification = State()
    notification_time = State()

async def on_startup(_):
    await db_start()
    print('Бот успешно инициализирован!')


async def day():
    day_now = datetime.today().weekday()
    day_now = DAYZ[day_now]
    return day_now


async def send_notification():
    profiles = await get_profiles()
    now = await day()
    for profile in profiles:
        if profile[4] == 1:
            if datetime.now().strftime('%H:%M') == profile[3]:
                events = await get_week_events(profile[1])
                events_dayl = "Расписание:"
                x = 0
                for event in events:
                    if now in event:
                        x += 1
                        events_dayl += '\n' + str(x) + ': ' + event[3] + ' ' + event[4]
                        await bot.send_message(text='Вот список дел на сегодня\n'+events_dayl,
                                               chat_id=profile[1])

                if x == 0:
                    await bot.send_message(text='На сегодня у вас нет запланированных дел'
                                                'Можете добавить что-то в свое расписание чтобы получать напоминание'
                                                'о запланированных делах каждый день',
                                           chat_id=profile[1])


# функция которая возвращает из бд расписание либо на день либо на неделю в зависимости от входных данных
async def show_all_events(message: types.Message, days) -> None:
    chat_id = str(message.from_user.id)
    events = await get_week_events(chat_id)
    events_dayl = "Расписание:"
    if type(days) == str:
        x = 0
        for event in events:
            if days in event:
                x += 1
                events_dayl += '\n' + str(x) + ': ' + event[3] + ' ' + event[4]
        if x == 0:
            events_dayl += '\nПусто 😔'
    else:
        for day in days:
            events_dayl += '\n'
            x = 0
            if day not in ['Понедельник', 'Вторник', 'Четверг', 'Воскресенье']:
                correct_day = day[0:-1] + 'у'
                events_dayl += '\n' + f'Расписание на {correct_day}'
            else:
                events_dayl += '\n' + f'Расписание на {day}'
            for event in events:
                if day in event:
                    x += 1
                    events_dayl += '\n' + str(x) + ': ' + event[3] + ' ' + event[4]
            if x == 0:
                events_dayl += '\nПусто 😔'
    await bot.send_message(text=events_dayl,
                           chat_id=message.from_user.id)


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message) -> None:
    if await check_profile(user_id=message.from_user.id):
        await bot.send_message(chat_id=message.from_user.id,
                               text='Привет пользователь!',
                               reply_markup=kb)
    else:
        await bot.send_message(chat_id=message.from_user.id,
                               text='Привет пользователь! \n'
                                    'Пожалуйста введи номер своей учебной группы '
                                    'для автоматического добавления \n'
                                    'учебного расписания в твой список дел')
        await ClientStatesGroup.registration.set()


# этот хендлер возвращает пользователю сообщение с кратким описанием функционала бота
@dp.message_handler(Text(equals='Описание'))
async def description_command(message: types.Message):
    await bot.send_message(chat_id=message.from_user.id,
                           text=f'Немного обо мне\n{DESCRIPTION}',
                           parse_mode='HTML')


# этот хендлер возвращает пользователю меню расписания
@dp.message_handler(Text(equals='Расписание'), state=None)
async def plans_command(message: types.Message, state: FSMContext):
    await message.answer(text='Выберите вариант действий',
                         parse_mode='HTML',
                         reply_markup=kb2)


# этот хендлер возвращает пользователю меню расписания
@dp.message_handler(Text(equals='Уведомления'), state="*")
async def plans_command(message: types.Message, state: FSMContext):
    await message.answer(text='Выберите подходящий вариант',
                         parse_mode='HTML',
                         reply_markup=kb4)
    await ClientStatesGroup.notification.set()


# этот хендлер возвращает пользователю клавиатуру начального меню
@dp.message_handler(Text(equals='Главное меню'), state="*")
async def back_command(message: types.Message, state: FSMContext):
    if state is None:
        return
    await state.finish()
    await message.answer(text='Вы вернулись в главное меню',
                         parse_mode='HTML',
                         reply_markup=kb)


# этот хендлер возвращает пользователю клавиатуру из меню расписания
@dp.message_handler(Text(equals='Назад'), state="*")
async def back_command(message: types.Message, state: FSMContext):
    if state is None:
        return
    await state.finish()
    await message.answer(text='Вы вернулись назад',
                         parse_mode='HTML',
                         reply_markup=kb2)


# этот хендлер возвращает пользователю клавиатуру из меню выбора варианта вывода расписания
@dp.message_handler(Text(equals='Вернуться назад'), state="*")
async def back_command(message: types.Message, state: FSMContext):
    if state is None:
        return
    await ClientStatesGroup.show_event.set()
    await message.answer(text='Вы вернулись назад',
                         parse_mode='HTML',
                         reply_markup=kb3)


# этот хендлер отправляет пользователю меню где он сможет выбрать день для назначния нового события
@dp.message_handler(Text(equals='Новое событие'), state=None)
async def new_command(message: types.Message):
    await message.answer(text='Выберите день недели',
                         parse_mode='HTML',
                         reply_markup=kb1)
    await ClientStatesGroup.day.set()


# этот хендлер отправляет пользователю меню где сможет выбрать день где он сможет выбрать день для корекции раписания
@dp.message_handler(Text(equals='Удалить событие'), state=None)
async def new_command(message: types.Message):
    await message.answer(text='Выберите день недели',
                         parse_mode='HTML',
                         reply_markup=kb1)
    await ClientStatesGroup.dell.set()


@dp.message_handler(Text(equals='Показать расписание'), state=None)
async def new_command(message: types.Message):
    await message.answer(text='Выберите дальнейшее действие',
                         parse_mode='HTML',
                         reply_markup=kb3)
    await ClientStatesGroup.show_event.set()


@dp.message_handler(Text(equals='На неделю'), state=ClientStatesGroup.show_event)
async def new_command(message: types.Message, state: FSMContext):
    await message.answer(text='Вот расписание на неделю',
                         parse_mode='HTML',
                         reply_markup=kb2)
    await show_all_events(message, DAYS)
    await state.finish()


@dp.message_handler(Text(equals='Изменить время'), state=ClientStatesGroup.notification)
async def new_command(message: types.Message, state: FSMContext):
    await message.answer(text='Введите новое время для получения уведомлений\n'
                              'В формате: HH:MM (H-часы, M-минуты)\n'
                              'Например: 10:30 или 12:33,',
                         parse_mode='HTML')
    await ClientStatesGroup.next()


@dp.message_handler(Text(equals='На день'), state=ClientStatesGroup.show_event)
async def new_command(message: types.Message, state: FSMContext):
    await message.answer(text='Выберите день недели',
                         parse_mode='HTML',
                         reply_markup=kb11)
    await ClientStatesGroup.next()


# Обработка сообщения с днем недели для добавления нового события
@dp.message_handler(Text(equals=('Понедельник', 'Вторник', 'Среда',
                                 'Четверг', 'Пятница', 'Суббота', 'Воскресенье')),
                    state=ClientStatesGroup.day)
async def days_command(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['day'] = message.text
    await ClientStatesGroup.next()
    await message.answer(text=CLARIFICATION,
                         reply_markup=kb227)


# Обратботка сообщения с днем недели для удаления события
@dp.message_handler(Text(equals=('Понедельник', 'Вторник', 'Среда',
                                 'Четверг', 'Пятница', 'Суббота', 'Воскресенье')),
                    state=ClientStatesGroup.dell)
async def days_command(message: types.Message, state: FSMContext):
    chat_id = str(message.from_user.id)
    # условия для проверки корректности вывода имени дня недели
    if message.text not in ['Понедельник', 'Вторник', 'Четверг', 'Воскресенье']:
        correct_day = message.text[0:-1] + 'у'
        await message.answer(text=f"Расписание на {correct_day}")
    else:
        await message.answer(text=f"Расписание на {message.text}")
    await show_all_events(message, message.text)

    async with state.proxy() as data:
        data['day'] = message.text

    # условия для проверки наличия запланнированных событий на выбранный день
    if await get_day_events(chat_id, message.text) == []:
        await message.answer(text='Удалять нечего',
                             reply_markup=kb2)
        await state.finish()
    else:
        await message.answer(text='А теперь введите номер события для удаления',
                             reply_markup=kb227)
        await ClientStatesGroup.next()


# Обработка сообщения с запросом на вывод расписания на определенный день
@dp.message_handler(Text(equals=('Понедельник', 'Вторник', 'Среда',
                                 'Четверг', 'Пятница', 'Суббота', 'Воскресенье')),
                    state=ClientStatesGroup.event_day,)
async def days_command(message: types.Message, state: FSMContext):
    if message.text not in ['Понедельник', 'Вторник', 'Четверг', 'Воскресенье']:
        correct_day = message.text[0:-1] + 'у'
        await message.answer(text=f"Расписание на {correct_day}",
                             reply_markup=kb2)
    else:
        await message.answer(text=f"Расписание на {message.text}",
                             reply_markup=kb2)
    await show_all_events(message, message.text)
    await state.finish()


# Обработка сообщений о включении и выключении уведомлений
@dp.message_handler(Text(equals=('Включить', 'Выключить')),
                    state=ClientStatesGroup.notification)
async def set_notif_state_command(message: types.Message, state: FSMContext):
    user = await get_user(message.from_user.id)
    if message.text == 'Выключить' and user[0][4] == 1:
        await edit_notif_state(0, user_id=str(message.from_user.id))
        await message.answer(text='Уведомления выключены',
                             reply_markup=kb)
        await state.finish()
    elif message.text == 'Включить' and user[0][4] == 0:
        await message.answer(text='Уведомления включены',
                             reply_markup=kb)
        await edit_notif_state(1, user_id=str(message.from_user.id))
        await state.finish()
    else:
        if message.text == 'Включить':
            await message.answer(text='Уведомления уже включены',
                             reply_markup=kb4)
            await ClientStatesGroup.notification.set()
        elif message.text == 'Выключить':
            await message.answer(text='Уведомления уже выключены',
                                 reply_markup=kb4)
            await ClientStatesGroup.notification.set()


# сохранения в бд события  введенного пользователем
@dp.message_handler(state=ClientStatesGroup.event)
async def new_command(message: types.Message, state: FSMContext):
    try:
        if message.text.count(':') == 2:
            async with state.proxy() as data:
                a = message.text
                data['name_event'] = a[:a.find(':')-2]
                data['time_event'] = a[a.find(':')-2:]
            await message.reply('Ваше событие сохранено',
                                reply_markup=kb2)
            async with state.proxy() as data:
                await bot.send_message(text=data['day'] + ' ' + data['name_event'] + ' ' + data['time_event'],
                                       chat_id=message.from_user.id)
            await new_event(state, user_id=message.from_user.id)
            await state.finish()
        else:
            await bot.send_message(text='Пожалуйста введите название и время события\n'
                                        'В соответсвии с примером приведенным в форме',
                                   chat_id=message.from_user.id)
    except:
        await bot.send_message(text='Пожалуйста введите название и время события\n'
                                    'В соответсвии с примером приведенным в форме',
                               chat_id=message.from_user.id)


# удаление события выбранного пользователем из бд
@dp.message_handler(state=ClientStatesGroup.dell_compl)
async def dell_command(message: types.Message, state: FSMContext):
    chat_id = str(message.from_user.id)
    events = await get_week_events(chat_id)
    y = 0
    async with state.proxy() as data:
        for event in events:
            if data['day'] in event:
                y += 1
    try:
        if 0 < int(message.text) <= y:
            chat_id = str(message.from_user.id)
            events = await get_week_events(chat_id)
            y = 0
            smth = {}
            async with state.proxy() as data:
                for event in events:
                    if data['day'] in event:
                        y += 1
                        smth[str(y)] = event[0]
                        await bot.send_message(chat_id=message.from_user.id,
                                               text=str(y) + ': ' + event[3] + ' ' + event[4])
            await dell_event(smth[message.text])
            await message.answer(text='Выбранное событие удалено',
                                 reply_markup=kb2)
            await show_all_events(message, data['day'])
            await state.finish()
        else:
            await bot.send_message(text='Пожалуйста введи корректное значение',
                                   chat_id=message.from_user.id)
    except:
        await bot.send_message(text='Введи корректное значение',
                               chat_id=message.from_user.id)


# Обработчик данных о времени получения уведомлений
@dp.message_handler(state=ClientStatesGroup.notification_time)
async def change_notif_time_command(message: types.Message, state: FSMContext):
    try:
        if message.text.count(':') == 1 and int(message.text[0:message.text.find(':')]) < 25:
            await edit_notif_time(message.text, user_id=str(message.from_user.id))
            await bot.send_message(text='Время получения уведомлений успешно изменено',
                                   chat_id=message.from_user.id,
                                   reply_markup=kb)
            await state.finish()
        else:
            await bot.send_message(text='Пожалуйста введите время в соответствии с примером',
                                   chat_id=message.from_user.id)
    except:
        await bot.send_message(text='Пожалуйста введите время в соответствии с примером',
                               chat_id=message.from_user.id)


# Обработчик данных о группе обучающегося
@dp.message_handler(state=ClientStatesGroup.registration)
async def new_command(message: types.Message, state: FSMContext):
    try:
        if message.text == 'Ист-21':
            async with state.proxy() as data:
                data['name_group'] = message.text
            await add_profile(state, user_id=message.from_user.id)
            await bot.send_message(text='Отлично ваши занятия добавлены в список дел\n'
                                        'Выбери дальнейшее действие',
                                   chat_id=message.from_user.id,
                                   reply_markup=kb)
            await state.finish()
        else:
            await bot.send_message(text='Пожалуйста введи кореектные данные',
                                   chat_id=message.from_user.id)
    except:
        pass


def repeat(coro, loop):
    asyncio.ensure_future(coro(), loop=loop)
    loop.call_later(60, repeat, coro, loop)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.call_later(60, repeat, send_notification, loop)
    executor.start_polling(dp, loop=loop,
                           on_startup=on_startup,
                           skip_updates=True
                           )



