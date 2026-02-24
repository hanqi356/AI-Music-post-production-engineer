@echo off
echo.
echo ========================================
echo AI音乐后期工程师 - pyworld库安装脚本
echo ========================================
echo.

echo 正在检查Python...
python --version
if errorlevel 1 (
    echo 错误: 未找到Python，请确保已安装Python 3.8+
    pause
    exit /b 1
)

echo.
echo 正在尝试安装pyworld库...
python -m pip install pyworld

if errorlevel 1 (
    echo.
    echo 安装失败，可能的原因：
    echo 1. Windows系统需要预编译的wheel文件
    echo 2. 需要安装Visual Studio Build Tools
    echo.
    echo 请参考 PYWORLD_INSTALLATION.md 文档获取详细安装指导
    echo.
    echo 或者尝试以下方法：
    echo 1. 下载预编译wheel文件: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyworld
    echo 2. 使用命令: pip install 下载的wheel文件路径
    echo.
) else (
    echo.
    echo ✓ pyworld库安装成功！
    echo.
    echo 验证安装...
    python -c "import pyworld; print('pyworld版本:', pyworld.__version__)"
)

echo.
echo 按任意键退出...
pause >nul