rem \---- Illogic Dir
SET ILLOGIC_DIR=%~dp0src

SET ILLOGIC_DIR_MAYA=%ILLOGIC_DIR%\maya
SET SCRIPT_MAYA=%ILLOGIC_DIR%\maya\scripts
SET NETWORK_INSTALL=%ILLOGIC_DIR%\networkInstall

rem \---- Shelf
SET MAYA_SHELF_PATH=%ILLOGIC_DIR_MAYA%\shelfs
SET XBMLANGPATH=%ILLOGIC_DIR_MAYA%\icons\startup_image;%ILLOGIC_DIR_MAYA%\icons

rem \---- Scripts
SET PYTHONPATH=%PYTHONPATH%;%SCRIPT_MAYA%\common;%SCRIPT_MAYA%\bug_out_bag;%SCRIPT_MAYA%\shader_maker;%SCRIPT_MAYA%\studio;%NETWORK_INSTALL%\script;

rem \---- Color
SET MAYA_COLOR_MANAGEMENT_POLICY_FILE=%ILLOGIC_DIR_MAYA%\colorManagement\cm_aces2.0.xml

REM == Start maya and launch statupSettings (FPS, Unit ect...)
start C:\"Program Files"\Autodesk\Maya2022\bin\maya.exe %1 %*
