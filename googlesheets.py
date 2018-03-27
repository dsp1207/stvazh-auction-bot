from oauth2client.service_account import ServiceAccountCredentials
import gspread
from datetime import date
from datetime import datetime
import datetime

global SCOPES

SCOPES = ["https://spreadsheets.google.com/feeds"]


def initWorksheet(keyfile, sheetname):
  "takes a Google Drive API JSON keyfile and the name of the file to connect to."
  "stores Sheet1 of the file as a Worksheet object in the global worksheet var"
  "keyfile: full path and name of your GDrive API json file"
  "sheetname: name of sheet in your Google Drive"
  credentials = ServiceAccountCredentials.from_json_keyfile_name(keyfile, SCOPES)
  connection = gspread.authorize(credentials)
  worksheet = connection.open(sheetname).sheet1
  return worksheet


def currentAuctions(worksheet):
  """ Returns the active auctions with the latest prices
  takes a worksheet object
  returns a dict with queryplate: current price"""
  plate_col = 1
  #set current row to last non-empty row in date col, then backtraces upwards to the first row with the current date
  last_row = worksheet.col_values(2).index("")
  current_auction_startdate = worksheet.cell(last_row, 2).value
  current_row = worksheet.col_values(2).index(current_auction_startdate)+1
  price_col = worksheet.row_values(current_row).index("")
  current_auctions_dict = {}
  # Create dict of sheet's plates of this week with price {plate no: price, plateno2: price2}
  pointer_row = current_row
  while(worksheet.cell(pointer_row, plate_col).value!=""):
    current_row_plate = worksheet.cell(pointer_row, plate_col).value
    current_row_price = worksheet.cell(pointer_row, price_col).value
    current_auctions_dict[current_row_plate] = current_row_price
    pointer_row+=1
  return current_auctions_dict

def maxPrice(worksheet):
    """takes worksheet object, and checks column 9 and returns array [price, plate, start-date]"""
    last_day_price_col = worksheet.col_values(9)
    ldpc_no_blanks = []
    for item in last_day_price_col:
        if(item!=''):
            ldpc_no_blanks.append(item)
    max_price = max(list(map(int,ldpc_no_blanks)))
    max_price_row = worksheet.col_values(9).index(str(max_price))+1
    max_price_plate = worksheet.cell(max_price_row, 1).value
    max_price_date = worksheet.cell(max_price_row, 2).value
    max_price_date_obj = datetime.datetime.strptime(max_price_date, '%Y-%m-%d')
    max_price_date_obj += datetime.timedelta(days=7)
    max_price_date = max_price_date_obj.strftime("%Y-%m-%d")
    max_price = str(format(int(max_price), ',d'))
    values_list = []
    values_list.append(max_price)
    values_list.append(max_price_plate)
    values_list.append(max_price_date)
    return values_list

def totalRevenue(worksheet):
    """takes worksheet object, and sums column 9 and returns sum of all prices paid as int"""
    last_day_price_col = worksheet.col_values(9)
    ldpc_no_blanks = []
    for item in last_day_price_col:
        if(item!=''):
            ldpc_no_blanks.append(item)
    totalrev = sum(list(map(int,ldpc_no_blanks)))
    totalrev = str(format(int(totalrev), ',d'))
    return totalrev

def averageRevenue(worksheet):
    """takes worksheet object, and sums column 9 and average revenue (/ total auctions / 7) as str nicely formatted"""
    last_day_price_col = worksheet.col_values(9)
    ldpc_no_blanks = []
    for item in last_day_price_col:
        if(item!=''):
            ldpc_no_blanks.append(item)
    averagerev = sum(list(map(int,ldpc_no_blanks)))/(len(ldpc_no_blanks)/7)
    averagerev = str(format(int(averagerev), ',d'))
    return averagerev

def averagePrice(worksheet):
    """takes worksheet object, and sums column 9 and returns average of all prices paid"""
    last_day_price_col = worksheet.col_values(9)
    ldpc_no_blanks = []
    for item in last_day_price_col:
        if(item!=''):
            ldpc_no_blanks.append(item)
    avgprice = sum(list(map(int,ldpc_no_blanks)))/(len(ldpc_no_blanks))
    avgprice = str(format(int(avgprice), ',d'))
    return avgprice

