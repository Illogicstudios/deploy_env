rem \---- Illogic Dir
SET ILLOGIC_DIR=%~dp0src

SET ILLOGIC_DIR_MAYA=%ILLOGIC_DIR%\maya
SET SCRIPT_MAYA=%ILLOGIC_DIR%\maya\scripts
SET NETWORK_INSTALL=%ILLOGIC_DIR%\networkInstall
SET LIB_DIR=%ILLOGIC_DIR_MAYA%\lib

rem \---- Shelf
SET MAYA_SHELF_PATH=%ILLOGIC_DIR_MAYA%\shelfs
SET XBMLANGPATH=%ILLOGIC_DIR_MAYA%\icons\trashtown_icon;%ILLOGIC_DIR_MAYA%\icons

rem \---- Scripts
SET PYTHONPATH=%PYTHONPATH%;%SCRIPT_MAYA%\shader_maker;%NETWORK_INSTALL%\script;

rem \---- Color
SET MAYA_COLOR_MANAGEMENT_POLICY_FILE=%ILLOGIC_DIR_MAYA%\colorManagement\cm_aces2.0.xml

rem \---- Current Project
SET CURRENT_PROJECT=trashtown_2112

REM == Start maya and launch statupSettings (FPS, Unit ect...)
start C:\"Program Files"\Autodesk\Maya2022\bin\maya.exe %1 %*