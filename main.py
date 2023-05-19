import requests
import aiogram 
from aiogram import Bot
from aiogram import Dispatcher
from aiogram import executor
from aiogram import types

SPOTIFY_TOKEN = ''
YANDEX_TOKEN=''
bot = Bot('token')
dp = Dispatcher(bot)


@dp.message_handlers(commands = ['start'])
async def start(message: types.Message):
    await message.answer(f'Привествую тебя {message.from_user.username}, что бы узнать команду напиши /info')

@dp.message_handlers(commands = ['info'])
async def info(message: types.Message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton('Яндекс', callback_data='Yandex'))
    markup.add(types.InlineKeyboardButton('Контакт', callback_data='Conact')) 
    markup.add(types.InlineKeyboardButton('Spotify', callback_data='Spotify'))

    await message.answer('Выберите команду', reply_markup=markup)


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'Yandex')
async def Yandex(callback_query: types.CallbackQuery, update, context):
    try:
        await message.answer('Закинь любую фотку!')
        message = update.message
        photo = message.photo[-1]

        photo_file= photo.get_file()
        photo_url = photo_file.file_path
        photo_path = f'photos/{photo_file.file_unique_id}.jpg'  # Путь для сохранения фотографии

        # Сохраняем фотографию на Яндекс.Диск
        upload_photo_to_yandex_disk(photo_url, photo_path)

        message.reply_text("Фотография успешно загружена на Яндекс.Диск.")
    except Exception:
        message.answer('Я не могу загрузить фотку!')
        return

# Функция для загрузки фотографии на Яндекс.Диск
async def upload_photo_to_yandex_disk(photo_url, photo_path):
    headers = {
        'Authorization': f'OAuth {YANDEX_DISK_TOKEN}'
    }

    # Скачиваем фотографию с помощью requests
    response = requests.get(photo_url)
    photo_data = response.content

    # Отправляем фотографию на Яндекс.Диск
    upload_url = f'https://cloud-api.yandex.net/v1/disk/resources/upload?path={photo_path}&overwrite=true'
    response = requests.get(upload_url, headers=headers)
    upload_data = response.json()

    if 'href' in upload_data:
        upload_href = upload_data['href']

        # Загружаем фотографию на Яндекс.Диск
        response = requests.put(upload_href, data=photo_data)
        if response.status_code == 201:
            print(f"Фотография успешно загружена на Яндекс.Диск: {photo_path}")
        else:
            print(f"Ошибка при загрузке фотографии на Яндекс.Диск: {response.text}")
    else:
        print(f"Ошибка при получении ссылки для загрузки на Яндекс.Диск: {upload_data}")

@dp.callback_query_handler(lambda callback_query: callback_query == 'Conact')
async def Conact(callback_query: types.CallbackQuery):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton('Discord', url=''))
    markup.add(types.InlineKeyboardButton('Telegram', url=''))
    await message.answer('Контакты', reply_markup=markup)

@dp.callback_query_handler(lambda callback_query: callback_query == 'Spotify')
async def Spotify(callback_query: types.CallbackQuery, query ):
    url = f'https://api.spotify.com/v1/search?q={query}&type=track'
    headers = {'Authorization':f'Bearer {SPOTIFY_TOKEN}'}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        tracks = data['tracks']['items']
        return tracks
    else:
        return []
async def send_tracks(bot, chat_id, tracks):
    if len(tracks) > 0:
        message = 'Результаты поиска:\n'
        for track in tracks:
            track_name = track['name']
            artists = ', '.join([artist['name'] for artist in track['artists']])
            message += f'- {track_name} by {artists}\n'
    else:
        message = 'Ничего не найдено.'

    await bot.send_message(chat_id=chat_id, text=message)



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)