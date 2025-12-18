Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "C:\Users\KhalidSiddiqui\Projects\AI-Note-Taker"
WshShell.Run """C:\Users\KhalidSiddiqui\miniconda3\envs\ai-note-taker\pythonw.exe"" meeting_recorder.py", 0, False
