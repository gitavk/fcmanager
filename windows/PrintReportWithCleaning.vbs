Dim Shtrih
Set Shtrih = CreateObject("AddIn.DrvFR")
Shtrih.Connect()
Shtrih.PrintReportWithCleaning()
WScript.StdOut.Write(Shtrih.ResultCode)
WScript.Quit (0)