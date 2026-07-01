@echo off
chcp 65001 >nul
title 竞享成果 - 公网模式

echo ========================================
echo   竞享成果 — 联网部署模式
echo ========================================
echo.
echo 正在启动服务器...
start "Flask" python app.py
timeout /t 3 >nul

echo.
echo 正在启动外网隧道...
echo 如果是第一次使用，请先去 https://ngrok.com 注册免费账号
echo 然后运行: ngrok config add-authtoken 你的token
echo.
ngrok http 5000

pause
