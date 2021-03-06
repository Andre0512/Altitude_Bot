#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
import yaml
from telegram import ReplyKeyboardMarkup, KeyboardButton, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from googlemaps import elevation, Client

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def get_yml(file):
    result = {}
    with open(os.path.join(os.path.dirname(__file__), file), 'rb') as ymlfile:
        result = yaml.load(ymlfile)
    return result


def get_altitude(latitude, longitude):
    maps = Client(key=get_yml('./config.yml')['altitude']['mapstoken'])

    req = elevation.elevation(maps, (latitude, longitude))[0]
    altitude = req['elevation']
    return altitude


def start(bot, update):
    if get_language(update):
        salutation = 'Hallo ' + update.message.from_user.first_name + " ✌🏻\n"
        text = "Sende mir einen Standort und ich sage dir auf welcher Höhe über dem  Meerespiegel dieser liegt 🙂"
        keyboard_text = 'Aktuellen Standort senden 📍'
    else:
        salutation = 'Hello ' + update.message.from_user.first_name + " ✌🏻\n"
        text = 'Send me a location and I will tell you at what altitude this is above sea level 🙂'
        keyboard_text = 'Send current location 📍'

    if update.message.text == '/start':
        text = salutation + text
    keyboard = ReplyKeyboardMarkup([[KeyboardButton(text=keyboard_text, request_location=True)]], resize_keyboard=True)
    update.message.reply_text(text=text, reply_markup=keyboard)


def help(bot, update):
    update.message.reply_text('Help!')


def get_language(update):
    try:
        language = update.message.from_user.language_code
    except:
        language = 'en'
    if language.split('-')[0] == 'de':
        return True
    else:
        return False


def location(bot, update):
    location = update.message.location
    altitude = get_altitude(location.latitude, location.longitude)
    altitude = round(altitude, 2)
    if get_language(update):
        altitude = str(altitude).replace('.', ',')
        reply_text = "Du bist auf einer Höhe von *" + altitude + "* Metern 😁"
    else:
        reply_text = "You are at an altitude of " + str(altitude) + " meters 😁"
    update.message.reply_text(reply_text, parse_mode=ParseMode.MARKDOWN)
    user = update.message.from_user
    name = user.first_name + " " + user.last_name if user.last_name else user.first_name
    log = ("\n" + name + " " + str(user.id) + " " + user.language_code +
           " (" + str(location.latitude) + ", " + str(location.longitude) + ")")
    file = open("log.txt", "a")
    file.write(log)
    file.close()


def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def main():
    updater = Updater(get_yml('./config.yml')['altitude']['bottoken'])

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    dp.add_handler(MessageHandler(Filters.location, location))
    dp.add_handler(MessageHandler(Filters.text, start))
    dp.add_handler(CallbackQueryHandler(button, pass_chat_data=True))

    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
