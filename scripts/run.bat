set PATH=c:\python35\;c:\python35\scripts\;%PATH%
set FILE_FILTER=%2
set TESTS_FILTER="%3"
set RETRIES=%5
set UPDATE_REFS=%6

if not defined RETRIES set RETRIES=2
if not defined UPDATE_REFS set UPDATE_REFS="No"

python -m pip install -r ..\jobs_launcher\install\requirements.txt

python ..\jobs_launcher\executeTests.py --test_filter %TESTS_FILTER% --file_filter %FILE_FILTER% --tests_root ..\jobs --work_root ..\Work\Results --work_dir Inventor --cmd_variables retries %RETRIES% UpdateRefs %UPDATE_REFS%