#!/bin/python3

from datastore import get
from datetime import datetime
import telebot
import re
import os
import platform
import sys
import psutil
import time

p = psutil.Process(os.getpid())
p.create_time() 


token = os.environ.get('BOT_TOKEN')
if token is None:
    try:
        token = input('Enter token: ')
        if len (token) != 46:
            sys.exit()
    except KeyboardInterrupt:
        sys.exit()
    
pattern = re.compile(r'^([0-9]{7}|[0-9]{8})$')

with open('message.txt', 'r', encoding="utf-8") as f:
    body_message = f.read()


def telegram_bot(token):

    bot = telebot.TeleBot(token)

    @bot.message_handler(commands=['start', 'help'])
    def start_welcome(message):
        print("New chat started with id: {}".format(message.chat.id))
        with open(f'chats/{message.chat.id}_{message.chat.username}.log', 'a+', encoding="utf-8") as f:
            pass
        bot.send_message(message.chat.id, 'היי. אני בוט שמחפש נתוני רכב במאגר של משרד התחבורה. פשוט תכתוב לי את המספר ואני אחפש אותו.')

    @bot.message_handler(commands=['log'])
    def read_log(message):
        try:
            with open(f'chats/{message.chat.id}_{message.chat.username}.log', 'r', encoding="utf-8") as f:
                log = f.read()
            if len(log) > 0:
                with open(f'chats/{message.chat.id}_{message.chat.username}.log', 'rb') as f:
                    bot.send_document(message.chat.id, f)
                f.close()
            else:
                bot.send_message(message.chat.id, 'מידע לא נמצא')
        except:
            bot.send_message(message.chat.id, 'מידע לא נמצא')

    @bot.message_handler(commands=['info'])
    def env_info(message):
        message_text = """OS: {os} \nBot uptime: {uptime} \nDisk usage: {disk} \nRAM usage: {ram} \nCPU usage: {cpu} \nPython version: {python}"""
        uptime = str(datetime.now() - datetime.fromtimestamp(p.create_time())).split('.')[0]
        bot.send_message(message.chat.id, message_text.format(os=platform.platform(), python=sys.version, uptime= uptime, disk=psutil.disk_usage('/').percent, ram=psutil.virtual_memory().percent, cpu=psutil.cpu_percent()))

        

    @bot.message_handler(regexp="^([0-9]{7}|[0-9]{8})$")
    def process_license(message):
        try:
            time = datetime.now().strftime('%Y.%m.%d %H:%M')
            with open(f'chats/{message.chat.id}_{message.chat.username}.log', 'a+', encoding="utf-8") as f:
                f.write(f'{time}, {message.text}\n')
            license = get(message.text)
            print("License request: {}".format(message.text))
            if license is None:
                bot.send_message(
                    message.chat.id, 'לא נמצא רכב עם מספר הרישום הזה.')
            else:
                license = license.dict()
                license['mivchan_acharon_dt'] = datetime.strptime(
                    license['mivchan_acharon_dt'], '%Y-%m-%dT%H:%M:%S').strftime('%d.%m.%Y')
                license['tokef_dt'] = datetime.strptime(
                    license['tokef_dt'], '%Y-%m-%dT%H:%M:%S').strftime('%d.%m.%Y')
                bot.reply_to(message, body_message.format(
                    **license), parse_mode='HTML')
        except Exception as e:
            bot.reply_to(message, '' + str(e))

    @bot.message_handler(content_types=['text'])
    def send_text(message):
        if message.text.lower() == 'hi':
            bot.send_message(message.chat.id, 'שלום!')
        else:
            bot.send_message(
                message.chat.id, 'סליחה, אני לא מבין אותך.  הזן את מספר הרישיון המורכב מ-7 או 8 ספרות')

    while True:
        try:
            bot.infinity_polling(timeout=10, interval=3)
        except Exception as e:
            time.sleep(5)
            print(e)
            


if __name__ == '__main__':
    telegram_bot(token)