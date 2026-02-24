# AI音乐后期工程师 - Windows PowerShell 启动脚本
# 兼容Windows 7/8/10/11

# 获取脚本所在目录
try {
    $ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
} catch {
    # PowerShell 2.0兼容写法
    $ScriptDir = Split-Path -Parent $PSCommandPath
}

Set-Location $ScriptDir

Write-Host "AI音乐后期工程师 - Windows启动脚本" -ForegroundColor Green
Write-Host ("=" * 50)

# 显示系统信息
$OS = Get-WmiObject -Class Win32_OperatingSystem
Write-Host "系统: $($OS.Caption) ($($OS.Version))" -ForegroundColor Cyan
Write-Host "架构: $([System.Environment]::Is64BitOperatingSystem ? "64位" : "32位")" -ForegroundColor Cyan

# 检查Python版本
Write-Host "检查Python环境..." -ForegroundColor Yellow

$PythonCmd = $null
$PythonVersion = $null
$PythonFullVersion = $null

# 尝试不同的Python命令
$PythonCommands = @("python", "python3", "py", "python2")

foreach ($cmd in $PythonCommands) {
    try {
        $versionOutput = & $cmd --version 2>$null
        if ($versionOutput -match "Python ([\d]+\.[\d]+)(\.[\d]+)?") {
            $PythonCmd = $cmd
            $PythonVersion = $matches[1]
            $PythonFullVersion = $matches[0]
            Write-Host "✓ 找到Python: $PythonFullVersion" -ForegroundColor Green
            break
        }
    } catch {
        continue
    }
}

# 如果没找到，尝试从注册表查找
if (-not $PythonCmd) {
    Write-Host "尝试从注册表查找Python..." -ForegroundColor Yellow
    try {
        $pythonPaths = @(
            "HKLM:\SOFTWARE\Python\PythonCore",
            "HKCU:\SOFTWARE\Python\PythonCore",
            "HKLM:\SOFTWARE\Wow6432Node\Python\PythonCore"
        )
        
        foreach ($regPath in $pythonPaths) {
            if (Test-Path $regPath) {
                $versions = Get-ChildItem $regPath -ErrorAction SilentlyContinue
                foreach ($version in $versions) {
                    if ($version.PSChildName -match "^([\d]+\.[\d]+)") {
                        $majorMinor = $matches[1]
                        if ([double]$majorMinor -ge 3.8) {
                            $installPath = (Get-ItemProperty "$($version.PSPath)\InstallPath" -ErrorAction SilentlyContinue)."(default)"
                            if ($installPath -and (Test-Path "$installPath\python.exe")) {
                                $PythonCmd = "$installPath\python.exe"
                                $PythonVersion = $majorMinor
                                Write-Host "✓ 从注册表找到Python: $PythonCmd (版本: $PythonVersion)" -ForegroundColor Green
                                break
                            }
                        }
                    }
                }
                if ($PythonCmd) { break }
            }
        }
    } catch {
        Write-Host "注册表查找失败: $_" -ForegroundColor Yellow
    }
}

if (-not $PythonCmd) {
    Write-Host "未找到合适的Python版本，尝试自动安装..." -ForegroundColor Yellow
    
    # 尝试自动安装Python
    $installSuccess = $false
    
    # 方法1: 使用Chocolatey (如果已安装)
    if (Get-Command "choco" -ErrorAction SilentlyContinue) {
        Write-Host "使用Chocolatey安装Python..." -ForegroundColor Cyan
        try {
            Start-Process -FilePath "choco" -ArgumentList "install", "python", "-y" -Wait -NoNewWindow
            $installSuccess = $true
        } catch {
            Write-Host "Chocolatey安装失败: $_" -ForegroundColor Red
        }
    }
    
    # 方法2: 使用Scoop (如果已安装)
    if (-not $installSuccess -and (Get-Command "scoop" -ErrorAction SilentlyContinue)) {
        Write-Host "使用Scoop安装Python..." -ForegroundColor Cyan
        try {
            Start-Process -FilePath "scoop" -ArgumentList "install", "python" -Wait -NoNewWindow
            $installSuccess = $true
        } catch {
            Write-Host "Scoop安装失败: $_" -ForegroundColor Red
        }
    }
    
    # 方法3: 下载并安装官方Python
    if (-not $installSuccess) {
        Write-Host "下载官方Python安装包..." -ForegroundColor Cyan
        try {
            $pythonUrl = "https://www.python.org/ftp/python/3.11.0/python-3.11.0-amd64.exe"
            $installerPath = "$env:TEMP\python-installer.exe"
            
            Write-Host "正在下载Python安装包..." -ForegroundColor Yellow
            Invoke-WebRequest -Uri $pythonUrl -OutFile $installerPath -UseBasicParsing
            
            Write-Host "正在安装Python..." -ForegroundColor Yellow
            Start-Process -FilePath $installerPath -ArgumentList "/quiet", "InstallAllUsers=1", "PrependPath=1", "Include_test=0" -Wait
            
            # 清理安装包
            Remove-Item $installerPath -Force
            $installSuccess = $true
            
        } catch {
            Write-Host "自动安装失败: $_" -ForegroundColor Red
        }
    }
    
    # 安装后重新检查
    if ($installSuccess) {
        Write-Host "重新检查Python安装..." -ForegroundColor Yellow
        Start-Sleep -Seconds 3  # 等待安装完成
        
        # 刷新环境变量
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        
        # 再次查找Python
        foreach ($cmd in @("python", "python3")) {
            try {
                $versionOutput = & $cmd --version 2>$null
                if ($versionOutput -match "Python ([\d]+\.[\d]+)(\.[\d]+)?") {
                    $PythonCmd = $cmd
                    $PythonVersion = $matches[1]
                    $PythonFullVersion = $matches[0]
                    Write-Host "✓ 安装成功，找到Python: $PythonFullVersion" -ForegroundColor Green
                    break
                }
            } catch {
                continue
            }
        }
    }
    
    # 如果仍然失败，提供手动安装指导
    if (-not $PythonCmd) {
        Write-Host "✗ 自动安装失败" -ForegroundColor Red
        Write-Host "请手动安装Python 3.8或更高版本" -ForegroundColor Red
        Write-Host ""
        Write-Host "手动安装步骤:" -ForegroundColor Yellow
        Write-Host "1. 访问 https://www.python.org/downloads/" -ForegroundColor Yellow
        Write-Host "2. 下载Python 3.8或更高版本"
        Write-Host "3. 安装时勾选 Add Python to PATH"
        Write-Host "4. 重启命令提示符或PowerShell"
        Read-Host "按回车键退出"
        exit 1
    }
}

# 检查Python版本是否符合要求
$RequiredVersion = "3.8"
if ([double]$PythonVersion -lt [double]$RequiredVersion) {
    Write-Host "✗ 错误: 需要Python $RequiredVersion或更高版本" -ForegroundColor Red
    Write-Host "当前版本: $PythonVersion" -ForegroundColor Red
    Read-Host "按回车键退出"
    exit 1
}

Write-Host "✓ Python版本检查通过: $PythonVersion" -ForegroundColor Green

# 检查pip可用性
Write-Host "检查pip..." -ForegroundColor Yellow
try {
    $pipCheck = & $PythonCmd -m pip --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ pip可用" -ForegroundColor Green
    } else {
        Write-Host "✗ pip不可用，尝试安装..." -ForegroundColor Yellow
        & $PythonCmd -m ensurepip --upgrade
        if ($LASTEXITCODE -ne 0) {
            Write-Host "✗ pip安装失败，请手动安装" -ForegroundColor Red
            Read-Host "按回车键退出"
            exit 1
        }
        Write-Host "✓ pip安装成功" -ForegroundColor Green
    }
} catch {
    Write-Host "✗ pip检查失败: $_" -ForegroundColor Red
    Read-Host "按回车键退出"
    exit 1
}

# 运行自动安装脚本
Write-Host ("=" * 50) -ForegroundColor Green
Write-Host "启动AI音乐后期工程师..." -ForegroundColor Yellow

try {
    & $PythonCmd install_and_run.py
    $exitCode = $LASTEXITCODE
    
    Write-Host ("=" * 50) -ForegroundColor Green
    if ($exitCode -eq 0) {
        Write-Host "✓ 程序正常退出" -ForegroundColor Green
    } else {
        Write-Host "✗ 程序异常退出 (退出码: $exitCode)" -ForegroundColor Red
        Write-Host ""
        Write-Host "可能的解决方案:" -ForegroundColor Yellow
        Write-Host "1. 检查音频设备权限"
        Write-Host "2. 重新安装依赖: & $PythonCmd -m pip install -r requirements.txt"
        Write-Host "3. 以管理员身份运行"
        Write-Host "4. 检查防病毒软件是否阻止"
    }
    Read-Host "按回车键关闭窗口"
} catch {
    Write-Host "✗ 运行出错: $_" -ForegroundColor Red
    Read-Host "按回车键关闭窗口"
}