import pysheets
import os
credentials = os.path.join('oddscheck-0ca8c6cebaee.json')

gc = pysheets.login(credentials)
spreadsheet = gc.open_by_key('1ptMK6DDON9vOzrz-nto2mFacadwqVNX49JNQyiizaNc')
sheet = pysheets.sheet(spreadsheet.sheet1)
sheet.get_range(1,1,1,1)