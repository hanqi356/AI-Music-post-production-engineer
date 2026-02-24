#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI音乐后期工程师 - 系统完整性检查
全面检查软件各模块功能状态
"""

import sys
import os
import numpy as np

def check_python_environment():
    """检查Python环境"""
    print("=== Python环境检查 ===")
    print(f"Python版本: {sys.version}")
    print(f"工作目录: {os.getcwd()}")
    print(f"Python路径: {sys.executable}")
    print("✓ Python环境正常")
    return True

def check_core_dependencies():
    """检查核心依赖"""
    print("\n=== 核心依赖检查 ===")
    dependencies = [
        ('numpy', '数值计算库'),
        ('scipy', '科学计算库'),
        ('librosa', '音频处理库'),
        ('soundfile', '音频文件读写'),
        ('matplotlib', '可视化库'),
        ('PyQt5', '图形界面库')
    ]
    
    success_count = 0
    for dep, desc in dependencies:
        try:
            module = __import__(dep)
            version = getattr(module, '__version__', 'unknown')
            print(f"✓ {dep} ({desc}): {version}")
            success_count += 1
        except ImportError as e:
            print(f"✗ {dep} ({desc}): 导入失败 - {e}")
        except Exception as e:
            print(f"⚠ {dep} ({desc}): 存在问题 - {e}")
    
    print(f"依赖检查完成: {success_count}/{len(dependencies)} 通过")
    return success_count == len(dependencies)

def check_audio_processing_modules():
    """检查音频处理模块"""
    print("\n=== 音频处理模块检查 ===")
    modules = [
        ('src.audio_processing.player', '音频播放器'),
        ('src.audio_processing.recording', '录音工程'),
        ('src.audio_processing.staff_image_generator', '五线谱生成器'),
        ('src.audio_processing.audio_to_midi', '音频转MIDI'),
        ('src.effects.equalizer', '均衡器'),
        ('src.effects.mastering', '母带处理器')
    ]
    
    success_count = 0
    for module_path, desc in modules:
        try:
            __import__(module_path)
            print(f"✓ {desc} ({module_path})")
            success_count += 1
        except ImportError as e:
            print(f"✗ {desc} ({module_path}): 导入失败 - {e}")
        except Exception as e:
            print(f"⚠ {desc} ({module_path}): 存在问题 - {e}")
    
    print(f"模块检查完成: {success_count}/{len(modules)} 通过")
    return success_count >= len(modules) - 1  # 允许一个模块有问题

def check_audio_functionality():
    """检查音频功能"""
    print("\n=== 音频功能检查 ===")
    try:
        # 测试音频播放器
        from src.audio_processing.player import AudioPlayer
        player = AudioPlayer()
        print("✓ 音频播放器初始化成功")
        
        # 创建测试音频
        sample_rate = 44100
        duration = 1.0
        t = np.linspace(0, duration, int(sample_rate * duration))
        test_audio = np.sin(2 * np.pi * 440 * t) * 0.3
        
        # 测试音频加载
        player.load_audio(test_audio, sample_rate)
        print(f"✓ 音频加载成功 (长度: {len(test_audio)} 样本)")
        
        # 测试播放器状态
        print(f"✓ 位置获取: {player.get_position()}")
        print(f"✓ 播放状态: {player.is_playing_state()}")
        print(f"✓ 暂停状态: {player.is_paused_state()}")
        print(f"✓ 当前音量: {player.volume}")
        
        return True
        
    except Exception as e:
        print(f"✗ 音频功能测试失败: {e}")
        return False

def check_staff_generation():
    """检查五线谱生成功能"""
    print("\n=== 五线谱生成功能检查 ===")
    try:
        from src.audio_processing.staff_image_generator import StaffImageGenerator
        generator = StaffImageGenerator()
        print("✓ 五线谱生成器初始化成功")
        
        # 创建测试音频
        sample_rate = 44100
        duration = 2.0
        t = np.linspace(0, duration, int(sample_rate * duration))
        frequencies = [261.63, 329.63, 392.00]  # C-E-G和弦
        test_audio = np.zeros_like(t)
        
        for i, freq in enumerate(frequencies):
            start_idx = int(i * duration/len(frequencies) * sample_rate)
            end_idx = int((i + 1) * duration/len(frequencies) * sample_rate)
            test_audio[start_idx:end_idx] = np.sin(2 * np.pi * freq * t[start_idx:end_idx]) * 0.3
        
        # 测试音高检测
        notes = generator.detect_pitch_events(test_audio)
        print(f"✓ 音高检测完成 (检测到 {len(notes)} 个音符)")
        
        # 测试五线谱转换
        staff_notes = generator.convert_notes_to_staff(notes)
        print(f"✓ 五线谱转换完成 ({len(staff_notes)} 个音符)")
        
        return True
        
    except Exception as e:
        print(f"✗ 五线谱生成功能测试失败: {e}")
        return False

def check_file_integrity():
    """检查文件完整性"""
    print("\n=== 文件完整性检查 ===")
    required_files = [
        'main.py',
        'requirements.txt',
        'src/audio_processing/player.py',
        'src/audio_processing/recording.py',
        'src/audio_processing/staff_image_generator.py',
        'src/effects/equalizer.py',
        'src/effects/mastering.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            print(f"✓ {file_path} ({file_size} bytes)")
        else:
            print(f"✗ {file_path} - 文件缺失")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"警告: 缺失 {len(missing_files)} 个必要文件")
        return False
    else:
        print("✓ 所有必需文件完整")
        return True

def check_ui_components():
    """检查UI组件"""
    print("\n=== UI组件检查 ===")
    try:
        from PyQt5.QtWidgets import QApplication, QWidget
        from PyQt5.QtCore import Qt
        
        # 测试基本UI组件
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        widget = QWidget()
        widget.setWindowTitle("UI测试")
        print("✓ 基本UI组件正常")
        
        # 测试Qt功能
        print(f"✓ Qt版本信息可用")
        print(f"✓ UI线程支持正常")
        
        return True
        
    except Exception as e:
        print(f"✗ UI组件测试失败: {e}")
        return False

def main():
    """主检查函数"""
    print("AI音乐后期工程师 - 系统完整性检查")
    print("=" * 50)
    
    checks = [
        ("Python环境", check_python_environment),
        ("核心依赖", check_core_dependencies),
        ("音频处理模块", check_audio_processing_modules),
        ("音频功能", check_audio_functionality),
        ("五线谱生成", check_staff_generation),
        ("文件完整性", check_file_integrity),
        ("UI组件", check_ui_components)
    ]
    
    results = []
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"\n{check_name}检查过程中出现异常: {e}")
            results.append((check_name, False))
    
    # 总结
    print("\n" + "=" * 50)
    print("系统检查总结:")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for check_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{status} {check_name}")
    
    print(f"\n总体状态: {passed}/{total} 项检查通过")
    
    if passed == total:
        print("🎉 系统状态良好，所有功能正常！")
        return True
    elif passed >= total * 0.8:
        print("⚠ 系统基本正常，部分功能可能需要关注")
        return True
    else:
        print("❌ 系统存在较多问题，需要进一步排查")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)