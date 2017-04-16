Dim Shtrih
Set Shtrih = CreateObject("AddIn.DrvFR")
Shtrih.Connect()
Shtrih.RepeatDocument()
WScript.StdOut.Write(Shtrih.ResultCode)
WScript.Quit (0)