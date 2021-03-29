set PATH=c:\python35\;c:\python35\scripts\;%PATH%
set FILE_FILTER=%1
set TESTS_FILTER="%2"
set TOOL=%3
set RETRIES=%4
set UPDATE_REFS=%5

if not defined TOOL set TOOL=2022
if not defined RETRIES set RETRIES=2
if not defined UPDATE_REFS set UPDATE_REFS="No"

python -m pip install -r ..\jobs_launcher\install\requirements.txt

python ..\jobs_launcher\executeTests.py --test_filter %TESTS_FILTER% --file_filter %FILE_FILTER% --tests_root ..\jobs --work_root ..\Work\Results --work_dir Inventor --cmd_variables Tool "C:\Program Files\Autodesk\Inventor %TOOL%\Bin\Inventor.exe" ResPath "C:\TestResources\usd_inventor_autotests_assets" retries %RETRIES% UpdateRefs %UPDATE_REFS% ToolName "Autodesk Inventor Professional %TOOL%"