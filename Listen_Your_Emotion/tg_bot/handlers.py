import datetime
import asyncio
import hashlib

from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

import tg_bot.keyboards as kb

from db.models import Profile, Review, Feedback, Rating
from db.database import database

router = Router()


class Request(StatesGroup):
    name = State()
    password = State()
    custom_name = State()

    review = State()
    feedback = State()


# storing user profiles
users_cache: dict[int, Profile] = {}


async def delete_message_delayed(message: Message, delay: int):
    await asyncio.sleep(delay)
    await message.delete()


@router.message(CommandStart())
async def start(message: Message):
    await message.answer(
        '<b>Здравствуйте!❤️ </b> \n\nПрежде чем начать,просим Вас войти в свой аккаунт.\n\nДля этого войдите в свой профиль',
        parse_mode='HTML', reply_markup=kb.login)


# button login, input name and password
@router.callback_query(F.data == 'login')
async def login(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Request.name)
    await callback.message.answer('Введите ваш <b>логин</b> <b>в</b> <b>LYE</b>', parse_mode='HTML')


@router.message(Request.name)
async def login_1(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Request.password)
    await message.answer('Введите ваш <b>пароль</b> <b>в</b> <b>LYE</b>', parse_mode='HTML')


@router.message(Request.password)
async def login_2(message: Message, state: FSMContext):
    data = await state.get_data()
    username = data.get('name')
    password = message.text

    user = database.get_profile_by_username(username)

    asyncio.create_task(delete_message_delayed(message, 2))

    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    if user and user.password == hashed_password:

        current_date = datetime.date.today()

        if user.birthday.month == current_date.month and user.birthday.day == current_date.day:
            await message.answer(f'С днём рождения! 🎉', parse_mode='HTML')

        await message.answer(
            f'Добрый день, <b>{user.username}!</b>\n\nУдобно ли Вам, если мы будем к вам так обращаться или Вы введете свой вариант?',
            reply_markup=kb.general, parse_mode='HTML')

        users_cache[message.from_user.id] = user
    else:
        await message.answer('Неверный логин или пароль. Пожалуйста, проверьте данные или зарегистрируйтесь в LYE',
                             reply_markup=kb.login)

    await state.set_state(None)


@router.callback_query(F.data == 'yes')
async def handle_yes(callback: CallbackQuery):
    await callback.message.answer(
        '💫 <b>Супер!</b> \n\nСкорее переходите в интересующие вас разделы и знакомьтесь с ними подробнее',
        parse_mode='HTML', reply_markup=kb.main)


@router.callback_query(F.data == 'no')
async def handle_no(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer('Хорошо, предложите свой вариант обращения')
    await state.set_state(Request.custom_name)


@router.message(Request.custom_name)
async def custom_name(message: Message, state: FSMContext):
    await state.update_data(custom_name=message.text)
    await message.answer(
        f"Теперь точно здравствуйте, <b>{message.text}</b> ☺️\n\nНиже вы сможете найти интересующие вас разделы и \nознакомиться с ними подробнее",
        reply_markup=kb.main, parse_mode='HTML')
    await state.set_state(None)


@router.message(F.text == 'Оцените приложение 🤩')
async def rating(message: Message):
    await message.answer(
        '📍<b>LYE</b> - это прежде всего про людей,про их чувства и музыку!\n\n <b>Наша цель</b> - помочь вам услышать себя и нам было бы очень приятно,если бы Вы оценили наше приложение и оставили отзыв. \n\n Так мы сможем стать еще ближе!',
        reply_markup=kb.rating, parse_mode='HTML')


text = '<b>Listen your emotion</b> - это инновационное музыкальное приложение, которое использует технологии распознавания лиц для определения эмоций пользователя и автоматического подбора подходящего трека. \n\nПриложение <b>анализирует выражение лица</b> пользователя и определяет его настроение, после чего запускает музыку, которая соответствует этим эмоциям.\n\nНапример, если пользователь улыбается, приложение может включить веселую и жизнерадостную музыку, а если он выглядит задумчивым или грустным, то выберет треки с более спокойным и меланхоличным настроением.\n\nЭто приложение отлично подходит для тех, кто хочет быстро найти музыку, которая соответствует их текущему настроению, без необходимости самостоятельно выбирать плейлисты или жанры. \n\nListen your emotion поможет создать подходящую атмосферу и поможет пользователю насладиться музыкой в полной мере'


@router.message(F.text == 'О нас ❓')
async def about(message: Message):
    await message.answer(text, reply_markup=kb.main, parse_mode='HTML')


# review
@router.callback_query(F.data == 'words')
async def number(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Request.review)
    await callback.message.answer('Нам важно ваше мнение. Оставьте свой отзыв пожалуйста')


@router.message(Request.review)
async def custom_name(message: Message, state: FSMContext):
    text = message.text
    tg_user_id = message.from_user.id

    review = Review(
        user_id=users_cache[tg_user_id].id,
        text=text
    )
    database.insert_review(review)

    await message.answer(f"Спасибо, ваш отзыв сохранен!", parse_mode='HTML')
    await state.set_state(None)


# support chat
@router.message(F.text == 'Чат с поддержкой 🫶')
async def feedback_callback(message: Message, state: FSMContext):
    await message.answer('Введите ваш вопрос или жалобу. Наши специалисты ваше сообщение и ответят вам в течении дня!')
    await state.set_state(Request.feedback)


@router.message(Request.feedback)
async def feedback_text(message: Message, state: FSMContext):
    text = message.text
    tg_user_id = message.from_user.id

    feedback = Feedback(
        user_id=users_cache[tg_user_id].id,
        text=text
    )
    database.insert_feedback(feedback)

    await message.answer("Спасибо!\n\nВаше сообщение отправлена нашим специалистам!")
    await state.set_state(None)


# for rating

@router.callback_query(F.data == 'number')
async def number(callback: CallbackQuery):
    await callback.message.answer(
        'Мы бы очень хотели, чтобы наше приложение помогло Вам услышать Вашу эмоцию ☺️ \n\nПожалуйста, оцените нас:',
        reply_markup=kb.rate)


@router.callback_query(F.data.in_(('11', '12', '13', '14', '15')))
async def number(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer('Оцените в среднем соответствие музыки вашему настроению', reply_markup=kb.service)
    user_id = callback.from_user.id
    data = callback.data
    r = int(data[-1])
    await state.update_data(general_rating=r)


@router.callback_query(F.data.in_(('21', '22', '23', '24', '25')))
async def number(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer('Оцените само приложение, интерфейс', reply_markup=kb.interface)
    data = callback.data
    r = int(data[-1])
    await state.update_data(service_rating=r)


@router.callback_query(F.data.in_(('31', '32', '33', '34', '35')))
async def number(callback: CallbackQuery, state: FSMContext):
    tg_user_id = callback.from_user.id
    data = callback.data
    interface = int(data[-1])

    state_data = await state.get_data()
    general = state_data.get('general_rating')
    service = state_data.get('service_rating')

    record_rating(
        users_cache[tg_user_id].id,
        general,
        service,
        interface
    )

    avg = (general + interface + service) / 3.0

    await callback.message.answer(f'<b>Спасибо!❤️ </b>\n\nСредняя оценка: {avg:.2f}', parse_mode='HTML')


def record_rating(user_id, general, service, interface):
    rating = Rating(
        user_id=user_id,
        general=general,
        service=service,
        interface=interface
    )

    database.insert_rating(rating)
