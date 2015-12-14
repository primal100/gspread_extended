import os

from gspread_extended import sheets

credentials = os.path.join('oddscheck-0ca8c6cebaee.json')

gc = sheets.authorize(credentials)
spreadsheet = gc.open_by_key('1ptMK6DDON9vOzrz-nto2mFacadwqVNX49JNQyiizaNc')