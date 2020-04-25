#Импортируем системные библиотеки
import datetime
import requests
import urllib.request
import subprocess
import os
from os import environ

#Импортируем библиотеку бота
from bot.bot import Bot
from bot.handler import CommandHandler, HelpCommandHandler, StartCommandHandler, UnknownCommandHandler, MessageHandler
from bot.filter import Filter

TOKEN = "///"

 
bot = Bot(token=TOKEN)

# временные файлы храним в /tmp, чтобы не переполнить хранилище
result_storage_path = 'tmp'


#Приветствие бота
bot_text = '''
Bip-bop человек,

Я классифицирую картинки используя нейронную сеть 🚀

Пришли мне картинку и я классифицирую её для тебя 🤟

Created with ❤️ by Artem Solovev.
'''


def send_welcome(bot, event):
 bot.send_text(chat_id=event.from_chat, text = bot_text)


def handle_image(bot, event):

  # Определение наименования изображения  
  image_name = save_image_from_message(bot, event)

  # Определение объектов на фото
  object_recognition_image(image_name)
  # Классификация изображения
  classify_image(image_name)

  image = open('.data/darknet/predictions.jpg','rb')
  class_result = result_file()
  output = 'Изображение классифицируется как:\n'
  output += class_result
  output += '\n🚀 Дай мне еще фото! 🚀'

  bot.send_file(chat_id=event.from_chat, file = image, caption = 'Идентифицированные объекты, если таковые имеются! 👻')
  bot.send_text(chat_id=event.from_chat, text = output)
  cleanup_remove_image(image_name)  

# ----------- Вспомогательные функции ---------------

def save_image_from_message(bot, event):
    
  bot.send_text(chat_id=event.from_chat, text = '🔥 Анализирую изображение, терпение! 🔥')
  
  # Ищем file_id изображения
  image_id = [p['payload']['fileId'] for p in event.data['parts']][0]
  
  # Забираем url изображения
  image_api = bot.get_file_info(image_id).url
  r = requests.get(image_api)
  image_url = r.json()['url']
  
  # Создаём временную папку, если отсутствует
  if not os.path.exists(result_storage_path):
    os.makedirs(result_storage_path)
  
  # Сохраняем изображение
  image_name = "{0}.jpg".format(image_id)
  urllib.request.urlretrieve(image_url, "{0}/{1}".format(result_storage_path,image_name))
  
  return image_name


def classify_image(image_name):
  command_class = 'cd .data/darknet && ./darknet classifier predict cfg/imagenet1k.data cfg/darknet19.cfg darknet19.weights ../../{0}/{1} > ../../{0}/results.txt'.format(result_storage_path, image_name)
  os.system(command_class)

  
def object_recognition_image(image_name):
  command_yolo = 'cd .data/darknet && ./darknet detect cfg/yolov3-tiny.cfg yolov3-tiny.weights ../../{0}/{1}'.format(result_storage_path, image_name)
  os.system(command_yolo)

def result_file():
    with open("/home/icq_nn_bot/tmp/results.txt", "r") as file:
        content = file.read()
    return content

def cleanup_remove_image(image_name):
  os.remove('/home/icq_nn_bot/{0}/{1}'.format(result_storage_path, image_name))

def main():
    bot.dispatcher.add_handler(StartCommandHandler(callback=send_welcome))
    bot.dispatcher.add_handler(MessageHandler(filters=Filter.image,callback=handle_image))
    bot.start_polling()
    bot.idle()

if __name__ == "__main__":
    main()