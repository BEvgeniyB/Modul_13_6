from idlelib.window import add_windows_to_menu

from config import api
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
# import asyncio


bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
button1 = types.KeyboardButton(text="Рассчитать")
button2 = types.KeyboardButton(text="Информация")
kb.row(button1,button2)

meny_kb = types.InlineKeyboardMarkup(
    inline_keyboard=[
        [
            types.KeyboardButton(text='Рассчитать норму калорий', callback_data='calories'),
         types.KeyboardButton(text='Формулы расчёта', callback_data='formulas')
        ]
    ],resize_keyboard=True
)

class UserState(StatesGroup):
    age = State()
    growth = State()
    weigth = State()
    gender = State()


def calculation(data):
    print(data)
    try:
        if data['gender'] == '1':
            calories = (10 * float(data['weigth']) + 6.25 * float(data['growth']) -
                        5 * float(data['age']) + float(5))
        elif data['gender'] == '2':
            calories = (10 * float(data['weigth']) + 6.25 * float(data['growth']) -
                    5 * float(data['age']) - float(161))
        else:
            calories = 'Не правильно введен пол'
    except:
        calories = ("Не правильно введены данные")

    return calories

@dp.message_handler(commands='start')
async def starter(message: types.Message):
    await message.answer('Привет! Я бот помогающий твоему здоровью.',reply_markup= kb)

@dp.message_handler(text='Рассчитать')
async def starter(message: types.Message):
    await message.answer('Выберите опцию:',reply_markup= meny_kb)


@dp.callback_query_handler(text='formulas')
async def get_formulas(call: types.CallbackQuery):
    await call.message.answer('для мужчин: 10 х вес (кг) + 6,25 x рост (см) – 5 х возраст (г) + 5')
    await call.message.answer('для женщин: 10 x вес (кг) + 6,25 x рост (см) – 5 x возраст (г) – 161')
    await call.answer()

@dp.message_handler(text="Информация")
async def set_age(message: types.Message):
    await message.answer('Расчет ведется по формуле Миффлина - Сан Жеора',reply_markup= kb)


@dp.callback_query_handler(text="calories")
async def set_age(call: types.CallbackQuery):
            await call.message.answer('Введите свой возраст:')
            await call.answer()
            await UserState.age.set()


@dp.message_handler(state=UserState.age)
async def set_growth(message: types.Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.answer('Введите свой рост в сантиметрах:')
    await UserState.growth.set()


@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    await state.update_data(growth=message.text)
    await message.answer('Введите свой вес:')
    await UserState.weigth.set()

@dp.message_handler(state=UserState.weigth)
async def set_gender(message, state):
    await state.update_data(weigth=message.text)
    await message.answer('Если мужчина введите : 1 ,если женщина : 2:')
    await UserState.gender.set()


@dp.message_handler(state=UserState.gender)
async def set_res(message, state):
    await state.update_data(gender=message.text)
    data = await state.get_data()
    await state.finish()
    await  message.answer(f'Суточная норма калорий равна : {calculation(data)}')
    await message.answer('Введите команду /start, чтобы начать расчет.')

@dp.message_handler()
async def all_message(message):
    await message.answer('Введите команду /start, чтобы начать общение.')

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
