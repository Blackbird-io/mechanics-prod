'This VBScript will open, collapse the rows attractively, save, and close an
'Excel file.

Option Explicit

Dim xlApp, xlBook
Dim ws, i

Set xlApp = GetObject("","Excel.Application")
xlApp.Visible = False

Set xlBook = xlApp.Workbooks.Open("FILENAME_PLACEHOLDER")

For Each ws in xlBook.Worksheets
    For i = 1 to 8
        ws.Outline.ShowLevels 9-i, 9-i
    Next
Next

xlBook.Save
xlBook.Close

Set xlBook = Nothing
Set i = Nothing
Set ws = Nothing

xlApp.Quit
Set xlApp = Nothing