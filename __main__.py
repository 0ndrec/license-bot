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
        bot.send_message(message.chat.id, 'Hi. I am a bot looking for vehicle data in the database of the Ministry of Transport. Just write me the car number.')

    @bot.message_handler(commands=['log'])
    def read_log(message):
        try:
            with open(f'chats/{message.chat.id}_{message.chat.username}.log', 'r', encoding="utf-8") as f:
                log = f.read()
            if len(log) > 0:
                with open(f'chats/{message.chat.id}_{message.chat.username}.log', 'rb') as f:
                    # Read last 5 lines of the file, and send them to the user
                    lines = f.readlines()[-5:]
                    bot.send_message(message.chat.id, f'Last 5 requests:\n{"".join(lines).decode("utf-8")}')
                    #bot.send_document(message.chat.id, f)
                f.close()
            else:
                bot.send_message(message.chat.id, 'Information not found')
        except:
            bot.send_message(message.chat.id, 'Information not found')

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
                    message.chat.id, 'No vehicle found with this registration number.')
            else:
                license = license.dict()
                #'%Y-%m-%dT%H:%M:%S'
                license['mivchan_acharon_dt'] = datetime.strptime(
                    license['mivchan_acharon_dt'], '%Y-%m-%d').strftime('%d.%m.%Y')
                license['tokef_dt'] = datetime.strptime(
                    license['tokef_dt'], '%Y-%m-%d').strftime('%d.%m.%Y')
                bot.reply_to(message, body_message.format(
                    **license), parse_mode='HTML')
        except Exception as e:
            bot.reply_to(message, '' + str(e))

    @bot.message_handler(content_types=['text'])
    def send_text(message):
        if message.text.lower() == 'ping':
            bot.send_message(message.chat.id, 'pong')
        else:
            bot.send_message(
                message.chat.id, 'Enter the 7 or 8 digit license number')

    while True:
        try:
            bot.infinity_polling(timeout=10, interval=3)
        except Exception as e:
            time.sleep(5)
            print(e)
            


if __name__ == '__main__':
    telegram_bot(token)