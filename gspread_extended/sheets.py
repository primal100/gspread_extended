import gspread
from gspread.models import Worksheet, Spreadsheet
from gspread import Client
import json
from oauth2client.client import SignedJwtAssertionCredentials
from operator import attrgetter
import itertools


def authorize(json_credentials_file):
    """Login to Google API using OAuth2 credentials.

    This is a shortcut function which instantiates the :class:`ClientExtended`
    and performes login right away.

    :returns: :class:`Client` instance.

    """
    json_key = json.load(open(json_credentials_file))
    scope = ['https://spreadsheets.google.com/feeds']
    credentials = SignedJwtAssertionCredentials(json_key['client_email'], json_key['private_key'].encode(), scope)
    client = ClientExtended(auth=credentials)
    client.login()
    return client

class ClientExtended(Client):

    def open(self, title):
        """Opens a spreadsheet, returning a :class:`SpreadsheetExtended` instance.

        :param title: A title of a spreadsheet.

        If there's more than one spreadsheet with same title the first one
        will be opened.

        :raises gspread.SpreadsheetNotFound: if no spreadsheet with
                                             specified `title` is found.

        """

        spreadsheet = super(ClientExtended, self).open(title)
        return get_spreadsheet(spreadsheet)

    def open_by_key(self, key):
        """Opens a spreadsheet specified by `key`, returning a :class:`~gspread.Spreadsheet` instance.

        :param key: A key of a spreadsheet as it appears in a URL in a browser.

        :raises gspread.SpreadsheetNotFound: if no spreadsheet with
                                             specified `key` is found.

        """
        spreadsheet = super(ClientExtended, self).open_by_key(key)
        return get_spreadsheet(spreadsheet)

    def open_by_url(self, url):
        """Opens a spreadsheet specified by `url`,
           returning a :class:`~gspread.Spreadsheet` instance.

        :param url: URL of a spreadsheet as it appears in a browser.

        :raises gspread.SpreadsheetNotFound: if no spreadsheet with
                                             specified `url` is found.

        """
        spreadsheet = super(ClientExtended, self).open_by_url(url)
        return get_spreadsheet(spreadsheet)

    def openall(self, title=None):
        """Opens all available spreadsheets,
           returning a list of a :class:`~gspread.Spreadsheet` instances.

        :param title: (optional) If specified can be used to filter
                      spreadsheets by title.

        """
        spreadsheets = super(ClientExtended, self).openall(title=title)
        custom_spreadsheets = []
        for spreadsheet in spreadsheets:
            custom_spreadsheets.append(get_spreadsheet(spreadsheet))
        return custom_spreadsheets

class SpreadsheetExtended(Spreadsheet):

    def add_worksheet(self, title, rows, cols):
        """Adds a new worksheet to a spreadsheet.

        :param title: A title of a new worksheet.
        :param rows: Number of rows.
        :param cols: Number of columns.

        Returns a newly created :class:`worksheets <Worksheet>`.
        """
        worksheet = super(SpreadsheetExtended, self).add_worksheet(title, rows, cols)
        return get_sheet(worksheet)

    def worksheets(self):
        """Returns a list of all :class:`worksheets <Worksheet>`
        in a spreadsheet.

        """
        worksheets = super(SpreadsheetExtended, self).worksheets()
        sheets = []
        for worksheet in worksheets:
            sheets.append(get_sheet(worksheet))
        return sheets

    def worksheet(self, title):
        """Returns a worksheet with specified `title`.

        The returning object is an instance of :class:`Worksheet`.

        :param title: A title of a worksheet. If there're multiple
                      worksheets with the same title, first one will
                      be returned.

        Example. Getting worksheet named 'Annual bonuses'
        """
        worksheet = super(SpreadsheetExtended, self).worksheet(title)
        return get_sheet(worksheet)

    def get_worksheet(self, index):
        """Returns a worksheet with specified `index`.

        The returning object is an instance of :class:`Worksheet`.

        :param index: An index of a worksheet. Indexes start from zero.

        Example. To get first worksheet of a spreadsheet:

        Returns `None` if the worksheet is not found.
        """
        worksheet = super(SpreadsheetExtended, self).get_worksheet(index)
        return get_sheet(worksheet)

class SheetExtended(Worksheet):
    def __init__(self, spreadsheet, element):
        super(SheetExtended, self).__init__(spreadsheet, element)

    def add_cols(self, cols):
        """Adds cols to worksheet.
        Returns a 2d list of cells from the newly added columns
        :param cols: Cols number to add.
        """
        first_col = self.col_count + 1
        rows = self.row_count
        self.resize(cols=first_col - 1 + cols)
        cell_list = self.range_2d(first_row=1, first_col=first_col, num_rows=rows, num_cols=cols)
        return cell_list

    def add_rows(self, rows):
        """Adds rows to worksheet.
        Returns a 2d list of cells from the newly added rows
        :param rows: Rows number to add.
        """
        first_row = self.row_count + 1
        cols = self.col_count
        self.resize(rows=first_row - 1 + rows)
        cell_list = self.range_2d(first_row=first_row, first_col=1, num_rows=rows, num_cols=cols)
        return cell_list

    def append_cols(self, values):
        """"Adds columns to the worksheet and populates them with values.
        Adds rows to the worksheet if there are more rows in the values than rows in the worksheet.
        Returns a 2d list of cells from the newly appended columns

        :param values: list of lists of values for the new columns.
        """
        rows = len(values)
        cols = len(max(values, key=len))
        if self.row_count < rows:
            self.resize(rows=rows)
        cell_list = self.add_cols(cols)
        cell_list = self.update_cell_values_2d(cell_list, values)
        return cell_list

    def append_rows(self, values):
        """"Adds rows to the worksheet and populates them with values.
        Widens the worksheet if there are more values in any row than columns in the worksheet.
        Returns a 2d list of cells from the newly appended rows

        :param values: list of lists of values for the new rows.
        """
        rows = len(values)
        cols = len(max(values, key=len))
        if self.col_count < cols:
            self.resize(cols=cols)
        cell_list = self.add_rows(rows)
        cell_list = self.update_cell_values_2d(cell_list, values)
        return cell_list

    def col_cells(self, col):
        """"Returns a 1d list of cells from the specified column

        :param col: column to return the cells from
        """
        cell_list = self.get_range(1, col, self.row_count, col)
        return cell_list

    def row_cells(self, row):
        """"Returns a 1d list of cells from the specified column

        :param row: row to return the cells from
        """
        cell_list = self.get_range(row, 1, row, self.col_count)
        return cell_list

    def update_col(self, col, values):
        """"Updates the values in a column.
        Returns the list of cells in the column
        :param col: column to update
        :param values: 1d list of values to update the column with
        """
        cell_list = self.col_cells(col)
        cell_list = self.update_cell_values(cell_list, values)
        return cell_list

    def update_row(self, row, values):
        """"Updates the values in a row
        Returns the list of cells in the row
        :param row: row to update
        :param values: 1d list of values to update the column with
        """
        cell_list = self.row_cells(row)
        cell_list = self.update_cell_values(cell_list, values)
        return cell_list

    def range_2d(self, alphanum=None, first_row=None, first_col=None, num_rows=None, num_cols=None, last_row=None,
                 last_col=None):
        """"Returns a 2d list of cells
        :param alphanum: A string with range value in common format,
                         e.g. 'A1:A5'.
        :param first_row: Optional. The first row in the range. If not set, a value of 1 will be used.
        :param first_col: Optional. The first column  in the range. If not set, a value of 1 will be used.
        :param num_rows: Optional. The number of row in the range. If not set, the value of last_row will be used.
        :param num_cols: Optional. The number of columns in the range. If not set, the value of last_col will be used.
        :param last_row: Optional. The last row in the range. If not set, self.row_count will be used.
        :param last_col Optional. The last columns in the range. If not set, self.col_count will be used.
        """
        if alphanum:
            cell_list = self.range(alphanum)
        else:
            first_row = first_row or 1
            first_col = first_col or 1
            if num_rows:
                last_row = first_row + num_rows - 1
            if num_cols:
                last_col = first_col + num_cols - 1
            last_row = last_row or self.row_count
            last_col = last_col or self.col_count
            cell_list = self.get_range(first_row, first_col, last_row, last_col)
        rows = self.to2d(cell_list)
        return rows

    def get_range(self, first_row, first_col, last_row, last_col):
        """"Returns a 1d list of cells, alternative to the range function
        :param first_row: The first row in the range.
        :param first_col: The first column  in the range.
        :param last_row: The last row in the range.
        :param last_col The last columns in the range.
        """
        first_cell = self.get_addr_int(first_row, first_col)
        last_cell = self.get_addr_int(last_row, last_col)
        alphanum_range = first_cell + ':' + last_cell
        cells = self.range(alphanum_range)
        return cells

    @staticmethod
    def to2d(cell_list):
        """"Returns a 2d list of cells
        :param cell_list: 1d list of cells, for example what is returned from range() or get_range()functions
        """
        min_col = min(cell_list, key=attrgetter('col'))
        max_col = max(cell_list, key=attrgetter('col'))
        num_cols = max_col - min_col + 1
        rows = [cell_list[i:i + num_cols] for i in xrange(0, len(cell_list), num_cols)]
        return rows

    @staticmethod
    def to1d(list2d):
        """"Returns a 1d list of cells
        :param list2d: 2d list of cells or values
        """
        list_1d = []
        for row in list2d:
            list_1d += row
        return list_1d

    def update_cell_values(self, cell_list, values):
        """Updates cells in batch with the given values

        :param cell_list: 1d list of a :class:`Cell` objects to update.
        :param values: 1d list of values to assign to the cells
        """
        for cell, value in itertools.izip(cell_list, values):
            cell.value = value
        self.update_cells(cell_list)
        return cell_list

    def update_cell_values_2d(self, cell_list, values):
        """Updates cells in batch with the given values

        :param cell_list: 2d list of a :class:`Cell` objects to update.
        :param values: 2d list of values to assign to the cells
        """
        cell_list = self.update_cell_values(self.to1d(cell_list), self.to1d(values))
        return self.to2d(cell_list)

    def update_cells_2d(self, cell_list):
        """Updates cells in batch.

        :param cell_list: 2d list of a :class:`Cell` objects to update.

        """
        self.update_cells(self.to1d(cell_list))

def get_spreadsheet(spreadsheet):
    return SpreadsheetExtended(spreadsheet.client, spreadsheet._feed_entry)

def get_sheet(worksheet):
    return SheetExtended(worksheet.spreadsheet, worksheet._element)
