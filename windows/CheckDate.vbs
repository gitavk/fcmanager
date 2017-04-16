Dim Shtrih
Set Shtrih = CreateObject("AddIn.DrvFR")
Shtrih.Connect()
Shtrih.GetECRStatus()

t = Split(Shtrih.TimeStr, ":")
tsec = int(t(0))*60*60 + int(t(1))*60 +int(t(2))
delta = Abs(timer - tsec)
WScript.StdOut.Write(delta)
WScript.Quit (0)