import urllib.request
from bs4 import BeautifulSoup
import re
import os

querynumbers = []

filename = "queryfile.txt" # Full name of file of numbers to be scanned for. File should contain individual numbers on each line.

def readNumFile(file):
  """ reads file, returns array of arrays
  data in file should be string separated by '|' and ',' """
  working_dir = os.path.dirname(os.path.realpath(__file__))
  query_nums_path = os.path.join(working_dir, file)
  query_nums_file = open(query_nums_path,"r")
  temparr = query_nums_file.read().split("|")
  arr = []
  for item in temparr:
    if(item!=""):
      arr.append(item.split(","))
  query_nums_file.close()
  return arr

def newEntry(query_num, chat_id, file):
  working_dir = os.path.dirname(os.path.realpath(__file__))
  query_nums_path = os.path.join(working_dir, file)
  with open(query_nums_path,"a") as query_nums_file:
    query_nums_file.write(query_num+","+chat_id+"|")

def scanAuction():
  """ Scans STVAZH Auction site and returns all plates as dict with plate numbers as keys and prices as values """
  soup = BeautifulSoup(urllib.request.urlopen('https://www.auktion.stva.zh.ch/').read(), "html.parser")
  plate_array = soup.select('.plate')
  plate_array_pretty = []
  plates = {}
  for item in plate_array:
    plate_array_pretty.append(item.prettify())
  for item in plate_array_pretty:
    plate_price = re.findall(r'(\d{1,3}\'?\d{1,3})(?=\sCHF)',item)[0].replace("'","")
    plate_number = re.findall(r'(ZH )(\d*)',item)[0][1]
    plates[plate_number]=plate_price
  return plates

def scanPlates(querynum, plates):
  """ Scans a dict of plates for querynum.
  Returns 1 if the querynum is found, and 0 if it isn't
  querynum: String of the Sequence of numbers to look for
  plates: dict, with keys to scan for query-num """
  for key in plates:
    if(key.find(querynum)!=-1):
      return key
  return 0

def mainSearch(query_arr, plates_dict):
  """ Searches a dict's keys for a list of strings. TO DO: Returns arr of arrs with [querystring, plate, chat_id, price]
  query_arr: List of strings to search for, [querystring, chat_id]
  plates_dict: Dict to search through"""
  results_arr = []
  for num in query_arr:
    scan_result = scanPlates(num[0], plates_dict)
    if (scan_result != 0):
      single_arr = []
      single_arr.append(num[0])
      single_arr.append(scan_result)
      single_arr.append(num[1])
      single_arr.append(plates_dict[scan_result])
      results_arr.append(single_arr)
      print(num[0]+" has been found being auctioned in plate: "+scan_result+" at a current price of "+plates_dict[scan_result]+" CHF. Now send message to Chat ID: "+num[1])
  return results_arr