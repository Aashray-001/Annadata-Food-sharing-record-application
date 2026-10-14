@echo off
echo ===================================================
echo Starting Food Donation & Distribution System...
echo ===================================================

rem Optional custom DB credentials (defaults to root / root if not set)
rem set DB_URL=jdbc:mysql://localhost:3306/food_donation_db
rem set DB_USER=root
rem set DB_PASSWORD=root

java --module-path lib --add-modules javafx.controls,javafx.fxml,javafx.graphics -cp "out;lib/*;resources" app.Main

if %errorlevel% neq 0 (
    echo.
    echo [NOTE] If the application failed to start:
    echo 1. Ensure MySQL Server is running on port 3306.
    echo 2. Verify credentials in run.bat or src\db\DatabaseConnection.java
    pause
)
