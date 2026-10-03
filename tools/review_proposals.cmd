@echo off
rem Shows the latest proposals, then lets you approve / reject by typing.
setlocal
cd /d "%~dp0.."
python pipeline\analyst.py status
echo.
python pipeline\analyst.py review
echo.
echo  To decide, copy one of the Approve / Reject lines above into this window, e.g.
echo     python pipeline\analyst.py approve ^<stamp^> --ids p1,p3
echo  Rows marked BLOCKED broke a rule and cannot be approved until analysis.json is fixed.
echo  The same text is saved as proposals\^<stamp^>\REVIEW.md
cmd /k
