# AI音乐后期工程师 - 音乐修音软件

一款专业的音乐修音软件，支持音准调校、EQ调节、录音工程和母带制作功能。

## 功能特点

- **音准调校**：自动检测并修正音高偏差
- **反AI痕迹处理**：智能保持人声自然特征，避免机器处理痕迹
- **EQ调节**：多频段均衡器，精细频率控制
- **录音工程**：多轨录音和编辑
- **母带制作**：专业级音频母带处理
- **跨平台支持**：Windows、macOS、Linux自动安装运行

## 技术栈

- Python 3.8+
- PyQt5 GUI框架
- Librosa 音频处理库
- NumPy 科学计算库
- SciPy 信号处理库
- pyworld 音高提取库（可选，用于高级音准校正）

## 高级功能可选依赖

### pyworld库（用于高级音准校正）

AI音乐后期工程师使用pyworld库来实现更精确的音准校正功能。虽然这不是必需的依赖（软件有备用方案），但安装pyworld可以获得更好的音准校正效果。

#### 安装方法

1. **自动安装**：
   - 运行 `python install_and_run.py` 将自动尝试安装
   - 或运行 `python install_pyworld.py` 专门安装

2. **手动安装**：
   - Windows用户：参考 `PYWORLD_INSTALLATION.md` 文档
   - macOS/Linux用户：`pip install pyworld`

3. **Windows批处理安装**：
   - 双击 `install_pyworld.bat` 文件

如果安装失败，软件仍可正常运行，但音准校正功能将使用备用方案。

## 跨平台使用方法

### macOS用户特别指南

**推荐方式1 - 一键安装（最简单）：**
双击 `install_macos.sh` 文件
自动安装Python 3.8+和所有依赖，完成后可直接使用

**推荐方式2 - 快速启动：**
双击 `start.sh` 文件启动
（如果提示缺少Python，会自动尝试安装）

**推荐方式3 - 桌面快捷方式：**
```bash
python3 macos_setup.py
```
创建桌面上的快捷启动方式

**推荐方式4 - 创建应用程序包：**
```bash
python3 package_macos.py
```
生成可直接双击使用的.app文件

**备选方式 - 手动运行：**
```bash
chmod +x start.sh
./start.sh
```
或 `python3 install_and_run.py`

### Windows用户
双击 `start.ps1` 或运行 `python install_and_run.py`

### Linux用户
```bash
chmod +x start.sh
./start.sh
```
或运行 `python3 install_and_run.py`

### 方法二：手动安装

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 运行软件：
```bash
python main.py
```

## 系统要求

- **Windows**: Windows 7/8/10/11 (32位或64位)
- **macOS**: macOS 10.9+ (Mavericks及更高版本)
- **Linux**: Ubuntu 16.04+, CentOS 7+, Debian 9+
- **Python版本**: 3.8或更高版本
- **内存**: 4GB RAM（推荐8GB）
- **存储空间**: 500MB可用空间

## macOS用户特别提示

### 最简单使用方式：
**双击 `install_macos.sh` 文件**
- 自动检测并安装Python 3.8+
- 自动安装所有项目依赖
- 完成后可直接使用软件

### DMG安装包方式（推荐）：
我们还提供了标准的macOS .dmg安装包，包含完整的.app应用程序：

1. 使用打包脚本创建DMG安装包：
   ```bash
   chmod +x package_macos.sh
   ./package_macos.sh
   ```

2. 这将生成 `AI音乐后期工程师-安装包.dmg` 文件

3. 双击DMG文件挂载，然后将应用程序拖拽到Applications文件夹

4. 在Launchpad中即可找到AI音乐后期工程师应用

### macOS完整部署方案：
对于开发者或需要完全控制部署过程的用户，我们提供了完整的部署解决方案：

- `complete_macos_setup.py` - 一键完成所有macOS部署步骤
- `create_macos_env.py` - 创建专用Python环境
- `MACOS_DEPLOYMENT_PLAN.md` - 详细的部署方案文档

运行以下命令使用完整部署方案：
```bash
python3 complete_macos_setup.py
```

详细信息请参阅以下文档：
- [MACOS_PACKAGING.md](MACOS_PACKAGING.md) - 打包指南
- [MACOS_DEPLOYMENT.md](MACOS_DEPLOYMENT.md) - 部署指南
- [MACOS_DEPLOYMENT_PLAN.md](MACOS_DEPLOYMENT_PLAN.md) - 部署方案
- [MACOS_QUICK_START.md](MACOS_QUICK_START.md) - 快速入门
- [MACOS_GUIDE.md](MACOS_GUIDE.md) - 使用指南

### 手动设置方式：
1. **安装Python**（如果未安装）：
   - 使用Homebrew：`brew install python3`
   - 或从官网下载：https://www.python.org/downloads/

2. **设置执行权限**：
   ```bash
   chmod +x start.sh
   ```

3. **双击启动**：
   直接双击 `start.sh` 文件即可运行

### 安全提示：
如果系统提示"无法打开"：
- 右键点击文件 → "打开方式" → "终端"
- 或在系统偏好设置 → 安全性与隐私中允许运行

### 快捷方式：
运行 `python3 macos_setup.py` 创建桌面快捷方式

## 核心技术特性

### 反AI痕迹处理
- **自然音高修正**：适度修正音高偏差，保持人声的自然波动
- **表达特征保留**：添加细微颤音、音量变化等人类演唱特征
- **频率响应优化**：智能平滑处理痕迹，避免人工峰值
- **动态范围保持**：维持音频的自然动态特性

### 自动安装特性
- **智能环境检测**：自动识别操作系统和Python版本
- **多版本兼容**：支持Python 3.8+，兼容老版本系统
- **智能pip管理**：自动选择并安装pip命令
- **逐包安装检查**：检测并安装缺失的依赖包
- **错误处理恢复**：提供详细的错误信息和解决建议
- **注册表查找**：Windows系统智能查找Python安装位置
- **多种Python支持**：兼容python、python3、py等多种命令
- **系统优化提示**：根据具体系统提供针对性建议

## 功能特性

### 1. 音准调校
- 智能音准检测与校正
- 多种校正模式（温和、激进、自适应）
- 实时预览效果

### 2. EQ调节
- 9段参数均衡器
- 预设均衡配置
- 实时频谱分析

### 3. 录音工程
- 多轨录音支持
- 轨道编辑功能
- 混音处理

### 4. 母带制作
- 专业母带处理链
- 响度标准化
- 立体声增强

### 5. 一键智能处理
- 智能音准校准：自动检测音频特征并应用最佳校准参数
- 智能EQ调节：自动分析音频类型并应用最佳EQ设置
- 智能母带处理：自动优化音频的整体听感

### 6. 音频对比功能
- **实时对比显示**：处理前后音频波形和频谱对比
- **可视化展示**：蓝色线条表示原始音频，红色线条表示处理后音频
- **灵活控制**：支持标签页独立控制和全局控制
- **多种显示模式**：支持分图对比和叠加显示
- **一键重置**：可随时重置音频到原始状态

## 版权信息

© 2026 AI音乐后期工程师团队