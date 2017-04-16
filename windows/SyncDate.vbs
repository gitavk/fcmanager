Dim Shtrih
Set Shtrih = CreateObject("AddIn.DrvFR")
Shtrih.Connect()

Shtrih.TimeStr = time
Shtrih.SetTime()
WScript.StdOut.Write(Shtrih.ResultCode)
WScript.Quit (0)