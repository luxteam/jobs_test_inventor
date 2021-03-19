set TOOL_VERSION=%1
if not defined TOOL_VERSION set TOOL_VERSION=2022
set OUTPUT_PATH=%2
if not defined OUTPUT_PATH set OUTPUT_PATH="..\\installation_check"

python check_installation.py --tool "C:\Program Files\Autodesk\Inventor %TOOL%\Bin\Inventor.exe" --output_path %OUTPUT_PATH%