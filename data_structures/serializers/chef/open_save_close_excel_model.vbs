'This VBScript will open, save, and close an Excel file in order to calculate
'the formulas contained therein.

Option Explicit

Dim xlApp, xlBook
Dim i

Set xlApp = GetObject("","Excel.Application")
xlApp.Visible = True

Set xlBook = xlApp.Workbooks.Open("FILENAME_PLACEHOLDER")
xlBook.Save
xlBook.Close

For i = 1 to xlBook.Worksheets.Count
    Dim ActiveSheet: ActiveSheet = xlBook.Worksheets(i)
    ActiveSheet.Outline.ShowLevels RowLevels:=1, ColumnLevels:=1
Next

Set xlBook = Nothing
Set i = Nothing

xlApp.Quit
Set xlApp = Nothing