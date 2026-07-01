@echo off
chcp 65001 >nul
title 竞享成果 - 竞赛获奖申报平台
echo ========================================
echo   竞享成果——学生竞赛获奖申报平台
echo   中北大学计算机科学与技术学院
echo ========================================
echo.
echo [1/3] 检查 Python 环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [X] 未找到 Python，请先安装 Python 3.9+
    pause
    exit /b 1
)
echo [✓] Python 环境就绪

echo [2/3] 安装依赖...
pip install -r requirements.txt -q
echo [✓] 依赖安装完成

echo [3/3] 启动服务器...
echo.
echo 平台已启动！请在浏览器中访问:
echo http://localhost:5000
echo.
echo 默认管理员账号: admin  密码: admin123
echo 按 Ctrl+C 停止服务器
echo ========================================
echo.
python app.py
pause
