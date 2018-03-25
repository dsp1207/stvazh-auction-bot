#change working path to current.
import os
os.chdir(os.path.dirname(os.path.realpath(__file__)))

from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
import logging
import datetime
import time

import re
import stva
import googlesheets as gs
import gspread

TELEGRAM_TOKEN = "TELEGRAM_BOT_TOKEN"
filename = "queryfile.txt"
google_api_json = "GOOGLE_API_JSON_FILE_NAME"
sheetname = "GOOGLE_SHEETS_NAME"

HELP_STRING = """Here are all the things I can do. Note that I've started collecting data on 15th March of 2018, so all stats are only from that time forward.

track <number>: Track a sequence of numbers. I'll check every Thursday, and notify you if the sequence is found in an active auction.
/highestprice: Tells you the highest price ever paid for a license plate number
/totalrevenue: Tells you the total revenue for license plate number auctions.
/averagerevenue: Tells you how much revenue is being made per week on the auctions.
/averageprice: Tells you how much is paid on average for a license plate.
/about: All you need to know about this bot.
"""

ABOUT_STRING = """I'm a bot that adds functionality to the license plate <a href="https://www.auktion.stva.zh.ch/">auction page</a> of Strassenverkehrsamt Zürich,
which is the DMV for the Canton of Zurich, Switzerland. Stvazh holds auctions for fancy license plate numbers.
The auctions normally run from Thursday 23:01 GMT+1 to Thursday 23:00 GMT+1 or something.

Made by Danny - <a href="https://github.com/dsp1207">Github</a>

"""

updater = Updater(token=TELEGRAM_TOKEN)
dispatcher = updater.dispatcher
queue = updater.job_queue

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


def start(bot, update):
  bot.send_message(chat_id=update.message.chat_id, text="Hello my name is stvazhauctionbot. Cool name, right? I'm the unofficial assistant for Strassenverkehrsamt Zürich license plate auctions. I can help you find the plate of your dreams, or tell you some fun facts about the auctions. To find out more, call for /help")


def help(bot, update):
  bot.send_message(chat_id=update.message.chat_id, text=HELP_STRING)

def about(bot, update):
  bot.send_message(chat_id=update.message.chat_id, text=ABOUT_STRING, parse_mode='HTML')

def totalrevenue(bot, update):
  ws = gs.initWorksheet(google_api_json, sheetname)
  totalrev = gs.totalRevenue(ws)
  bot.send_message(chat_id=update.message.chat_id, text="Total revenue since 2018-3-15 is <b>"+str(totalrev)+" CHF</b>", parse_mode='HTML')

def averagerevenue(bot, update):
  ws = gs.initWorksheet(google_api_json, sheetname)
  averagerev = gs.averageRevenue(ws)
  bot.send_message(chat_id=update.message.chat_id, text="Average revenue per week is <b>"+str(averagerev)+" CHF</b>", parse_mode='HTML')

def averageprice(bot, update):
  ws = gs.initWorksheet(google_api_json, sheetname)
  avgprice = gs.averagePrice(ws)
  bot.send_message(chat_id=update.message.chat_id, text="Average price paid for a license plate is <b>"+str(avgprice)+" CHF</b>", parse_mode='HTML')

def highestprice(bot, update):
  ws = gs.initWorksheet(google_api_json, sheetname)
  max_price_arr = gs.maxPrice(ws)
  bot.send_message(chat_id=update.message.chat_id, text="The highest price paid since 2018-3-15 was <b>"+max_price_arr[0]+" CHF</b> for license plate no <b>"+max_price_arr[1]+"</b> on "+max_price_arr[2], parse_mode='HTML')


def react(bot, update):
  body = update.message.text
  chat_id = update.message.chat_id
  response_message = ""
  track_match = re.search(r'(?<=track )(\d*)',body)
  if(track_match):
    stva.newEntry(str(track_match.group(1)), str(chat_id), filename)
    response_message = "Ok. New auctions go up every Thursday, so I'll shoot you a message when pattern "+track_match.group(1)+" is found."
  track_match = re.search(r'(fun fact)',body)
  if(response_message!=""):
    bot.send_message(chat_id=update.message.chat_id, text=response_message)
  else:
    bot.send_message(chat_id=update.message.chat_id, text="Sorry, I don't understand. Type /help for guidance.")


conversation_handler = MessageHandler(Filters.text, react)

dispatcher.add_handler(conversation_handler)

updater.start_polling()

def weeklyUpdate(bot, job):
  """ calls gs.scanNewEntries and returns the results as array of arrays of chat_id, plate_number, price. Then messages are sent to the guys """
  ws = gs.initWorksheet(google_api_json, sheetname)
  query_arr = stva.readNumFile(filename)
  current_auctions_dict = gs.currentAuctions(ws, query_arr)
  matches_arr = stva.mainSearch(query_arr, current_auctions_dict)
  for result in matches_arr:
    response_message = "Your lucky number "+result[0]+" has been found being auctioned in "+result[1]+" at a current price of "+result[3]+" CHF"
    bot.send_message(chat_id = result[2], text=response_message)

#Attach handlers

help_handler = CommandHandler('help', help)
dispatcher.add_handler(help_handler)

about_handler = CommandHandler('about', about)
dispatcher.add_handler(about_handler)

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

totalrevenue_handler = CommandHandler('totalrevenue', totalrevenue)
dispatcher.add_handler(totalrevenue_handler)

highestprice_handler = CommandHandler('highestprice', highestprice)
dispatcher.add_handler(highestprice_handler)

averageprice_handler = CommandHandler('averageprice', averageprice)
dispatcher.add_handler(averageprice_handler)

averagerevenue_handler = CommandHandler('averagerevenue', averagerevenue)
dispatcher.add_handler(averagerevenue_handler)

# Below here is on-first-start bullshit for figuring out when to first run the notifier (next Thursday at 8.30)

today = datetime.date.today()
thursday = today + datetime.timedelta( (3-today.weekday()) % 7 )
first_weekly = datetime.datetime.combine(thursday, datetime.time(8,30))
now = datetime.datetime.now()

if(first_weekly<now):
    first_weekly = first_weekly+datetime.timedelta(days=7)

first_weekly_unix = time.mktime(first_weekly.timetuple())
now_unix = time.mktime(now.timetuple())

secs_til_first_update = (first_weekly_unix - now_unix)

week_in_mins = 10080

weekly_update_queue = queue.run_repeating(weeklyUpdate, interval=week_in_mins, first=secs_til_first_update)
