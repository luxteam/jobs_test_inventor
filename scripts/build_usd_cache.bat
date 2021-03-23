set TOOL_VERSION=%1
if not defined TOOL_VERSION set TOOL_VERSION=2022
set OUTPUT_PATH=%2
if not defined OUTPUT_PATH set OUTPUT_PATH="..\\cache_building_results"

python build_usd_cache.py --tool "C:\Program Files\Autodesk\Inventor %TOOL_VERSION%\Bin\Inventor.exe" --output_path %OUTPUT_PATH% --assets_path "C:\\TestResources\\usd_inventor_autotests_assets" --tool_name "Autodesk Inventor Professional %TOOL_VERSION%"