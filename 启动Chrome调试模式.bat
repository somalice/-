@echo off
echo =======================================
echo   Chrome调试模式启动器
echo =======================================
echo.
echo 正在关闭所有Chrome浏览器...
taskkill /F /IM chrome.exe 2>nul
timeout /t 2 /nobreak

echo.
echo 正在启动Chrome调试模式...
echo （这将使用您的默认Chrome配置，保持登录状态）
echo.
echo =======================================
echo.

start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222

echo 等待Chrome启动...
timeout /t 5 /nobreak

echo.
echo =======================================
echo   Chrome调试模式已就绪！
echo =======================================
echo.
echo 现在您可以运行下载器程序了
echo.
pause
