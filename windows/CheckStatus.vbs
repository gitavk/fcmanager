Dim Shtrih
Set Shtrih = CreateObject("AddIn.DrvFR")
Shtrih.Connect()
Shtrih.GetECRStatus()

WScript.StdOut.Write(Shtrih.ECRMode)
WScript.Quit (0)