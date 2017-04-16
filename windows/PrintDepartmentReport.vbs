Dim Shtrih
Set Shtrih = CreateObject("AddIn.DrvFR")
Shtrih.Connect()
Shtrih.PrintDepartmentReport()
WScript.StdOut.Write(Shtrih.ResultCode)
'WScript.Echo(Shtrih.ResultCode)
WScript.Quit (0)