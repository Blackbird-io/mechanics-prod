'This VBScript will open, save, and close an Excel file in order to calculate
'the formulas contained therein.

Option Explicit

Dim xlApp, xlBook

Set xlApp = GetObject("","Excel.Application")
xlApp.Visible = False

Set xlBook = xlApp.Workbooks.Open("FILENAME_PLACEHOLDER")
xlBook.Save
xlBook.Close
Set xlBook = Nothing

xlApp.Quit
Set xlApp = Nothing