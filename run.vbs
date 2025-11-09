Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")
strPath = objFSO.GetParentFolderName(WScript.ScriptFullName)
strBatch = strPath & "\run.bat"
objShell.Run chr(34) & strBatch & Chr(34), 0
Set objShell = Nothing
Set objFSO = Nothing