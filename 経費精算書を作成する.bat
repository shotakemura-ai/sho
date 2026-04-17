@echo off
chcp 65001 > nul
echo.
echo  三幸商事株式会社 経費精算書 自動生成
echo.
python "%~dp0expense_report.py"
echo.
pause
