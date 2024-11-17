import ccxt
import asyncio
from aiogram import Bot, Dispatcher
import logging
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from config import api_secret, api_key, telegram_bot_api
from database import return_user_id, return_values, insert_values
from text import start, insert

is_waiting_pair = False

pair = ""

bot = Bot(token=telegram_bot_api)
dp = Dispatcher()
chat_id = []
list_crypt = [[]]

fetch_task = False

phemex = ccxt.phemex({
    'enableRateLimit': True,
    'apiKey': api_key,
    'secret': api_secret
})

def update():
    global chat_id, list_crypt, fetch_task

    chat_id.clear()
    list_crypt.clear()
    list_crypt.append([])
    try:

        ids = return_user_id()

        for i in ids:
            chat_id.append(i)

        for id in range(len(chat_id)):
            print(id)
            print(f"ReturnValues: {return_values(chat_id[id])}")

            list_crypt[id] = return_values(chat_id[id])
            list_crypt.append([])

        # list_crypt.remove([])


        if fetch_task:
            fetch_task.cancel()  # Завершаем текущую задачу
        fetch_task = asyncio.create_task(fetch_and_print_prices())  # Создаем новую


    except Exception as e:
        print(f"Ошибка при загрузке ДАННЫХ: {e}")

    print("Chat_id: ", chat_id)
    print(f"ListCrypt: {list_crypt}")

async def send_text_to_user(chat_id: int, text: str):
    try:
        await bot.send_message(chat_id=chat_id, text=text)
    except Exception as e:
        logging.error(f"Ошибка при отправке сообщения: {e}")


@dp.message(CommandStart())
async def cmd_start(message: Message):
    print(f"Chat id: {message.chat.id}")
    await message.answer(start)



@dp.message(Command("add_crypto_pair"))
async def add_crypto_pair(message : Message):
    global is_waiting_pair
    print("I SEE YOUR MESSAGE")
    await send_text_to_user(int(message.chat.id), insert)
    is_waiting_pair = True




@dp.message(Command("view_tracking"))
async def view_tracking(message : Message):
    user = message.chat.id
    text = "На данный момент бот отслеживает у вас следующие криптовалютные пары:\n"
    try:
        id_in_chatid = chat_id.index(user)
    except Exception as e:
        await send_text_to_user(user, "Что-то пошло не так")
        return

    for pair in list_crypt[id_in_chatid]:
        text += f"{pair}\n"

    await send_text_to_user(user, text=text)

@dp.message()
async def process_messages(message : Message):
    print("OK")
    global is_waiting_pair
    if (is_waiting_pair):
        pair = message.text
        is_waiting_pair = False
        if (len(chat_id) != 0):
            key = chat_id.index(int(message.chat.id))
        else:

            list_crypt[0] += pair

        insert_values(int(message.chat.id), pair)
        update()



async def fetch_and_print_prices():
    while True:
        global list_crypt
        global chat_id
        print("IN SCRIPT:", list_crypt)
        for i in range(len(list_crypt)):  # Проходим по каждому вложенному списку
            crypt_list = list_crypt[i]
            for l in crypt_list:  # Перебираем криптовалюты в текущем списке
                try:


                    btc_phe_book = phemex.fetch_order_book(l)
                    buy_price = btc_phe_book['bids'][0][0]

                    # Разбиваем строку на тикеры
                    one = l.split("USD")
                    two = l.replace(one[0], "")
                    ticker = f"{one[0]}/{two}"
                    btc_usdt = phemex.fetch_ticker(ticker)['last']

                    sellPrice = btc_usdt
                    spread = (sellPrice - buy_price) / buy_price * 100

                    if spread >= 0:
                        message = f"{l}: {spread:.2f}%: {buy_price}: {sellPrice}"
                    else:
                        message = f"На рынке с криптовалютной парой {l} ничего не происходит"

                     # Отправляем сообщение для текущего пользователя
                    await send_text_to_user(chat_id[i], message)

                except Exception as e:
                    logging.error(f"Ошибка при получении данных: {e}")

        await asyncio.sleep(120)




async def main():
    global fetch_task
    fetch_task = asyncio.create_task(fetch_and_print_prices())
    await dp.start_polling(bot)

if __name__ == "__main__":

    try:

        ids = return_user_id()

        for i in ids:
            chat_id.append(i)

        for id in range (len(chat_id)):
            print(id)
            print(f"ReturnValues: {return_values(chat_id[id])}")

            list_crypt[id] = return_values(chat_id[id])
            list_crypt.append([])



        # list_crypt.remove([])

        print(f"ListCrypt: {list_crypt}")
    except Exception as e:
        print(f"Ошибка при загрузке ДАННЫХ: {e}")


    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Выход из программы")
