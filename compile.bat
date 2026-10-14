@echo off
echo ===================================================
echo Compiling Food Donation & Distribution System...
echo ===================================================

if not exist "out" mkdir "out"

dir /s /b src\*.java > sources.txt
javac --module-path lib --add-modules javafx.controls,javafx.fxml,javafx.graphics -cp "lib/*" -d out @sources.txt

if %errorlevel% neq 0 (
    echo [ERROR] Compilation failed. Please check errors above.
    pause
    exit /b %errorlevel%
)

echo Copying resources to out directory...
xcopy /s /e /y /i resources\* out\ > nul

echo [SUCCESS] Compilation completed successfully!
pause
