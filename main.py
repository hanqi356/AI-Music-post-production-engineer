"""
AI音乐后期工程师 - 音乐修音软件
主程序入口
"""

import sys
import warnings
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QMenuBar, QStatusBar, QLabel, QAction, QFileDialog, QMessageBox, QPushButton, QSlider, QTextEdit, QListWidget, QComboBox, QCheckBox, QAbstractItemView
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

# 忽略Qt布局警告
warnings.filterwarnings("ignore", ".*Cannot add a null widget.*")
import matplotlib
matplotlib.use('Qt5Agg')

# 设置中文字体支持
import matplotlib.pyplot as plt
from matplotlib import font_manager

# 尝试设置支持中文的字体
try:
    # 优先使用系统支持的中文字体
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans', 'Arial Unicode MS', 'Songti SC', 'PingFang SC']
    plt.rcParams['axes.unicode_minus'] = False  # 正常显示负号
except:
    pass

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import librosa
import soundfile as sf

# 音频播放支持
try:
    import sounddevice as sd
    SOUNDDEVICE_AVAILABLE = True
except ImportError:
    SOUNDDEVICE_AVAILABLE = False
    print("警告: sounddevice库未安装，播放功能将受限")


class AudioProcessor:
    """音频处理器"""
    
    def __init__(self):
        self.audio_data = None
        self.sample_rate = None
        self.original_audio = None
        self.backup_audio = None  # 用于对比功能的备份音频
        
    def load_audio(self, filepath):
        """加载音频文件"""
        try:
            self.audio_data, self.sample_rate = librosa.load(filepath, sr=None)
            self.original_audio = self.audio_data.copy()
            self.backup_audio = self.audio_data.copy()  # 备份原始音频用于对比
            return True
        except Exception as e:
            print(f"加载音频文件失败: {e}")
            return False
    
    def save_audio(self, filepath):
        """保存音频文件"""
        try:
            if self.audio_data is not None:
                sf.write(filepath, self.audio_data, self.sample_rate)
                return True
        except Exception as e:
            print(f"保存音频文件失败: {e}")
        return False
    
    def equalize(self, bands):
        """EQ调节 - 均衡器"""
        if self.audio_data is None or len(bands) == 0:
            return False
            
        try:
            # 导入均衡器模块
            from src.effects.equalizer import Equalizer
            eq = Equalizer(sample_rate=self.sample_rate)
            
            # 设置各频段增益
            eq.set_all_gains(bands)
            
            # 应用均衡器
            processed_audio = eq.apply_equalizer(self.audio_data)
            
            # 防止处理累积误差，确保数值稳定
            processed_audio = np.clip(processed_audio, -1.0, 1.0)
            
            self.audio_data = processed_audio
            
            return True
        except ImportError:
            print("均衡器模块不可用")
            return False
        except Exception as e:
            print(f"EQ调节失败: {e}")
            return False

    def smart_equalize(self, mode='smart', anti_ai=True):
        """智能一键EQ（可选反AI痕迹）"""
        if self.audio_data is None:
            return False
        
        try:
            if anti_ai:
                # 使用反AI痕迹均衡器
                from src.audio_processing.anti_ai_processing import AntiAIEqualizer
                eq = AntiAIEqualizer(sample_rate=self.sample_rate)
                
                # 根据模式选择预设
                mode_presets = {
                    'smart': [0, 0, 0.2, 0.5, 0.8, 0.6, 0.3, 0.1, 0],  # 智能模式
                    'vocal': [0, -0.3, 0, 0.5, 1.0, 1.2, 0.8, 0.3, -0.2],  # 人声模式
                    'instrumental': [0.2, 0.1, 0, 0.3, 0.5, 0.8, 1.0, 0.6, 0.2],  # 乐器模式
                    'mix': [0, 0, 0.1, 0.3, 0.5, 0.4, 0.2, 0.1, 0],  # 混音模式
                    'flat': [0, 0, 0, 0, 0, 0, 0, 0, 0],  # 平坦模式
                    'bright': [0, 0, 0, 0.2, 0.5, 1.0, 1.2, 0.8, 0.3],  # 明亮模式
                    'warm': [0.5, 0.3, 0.1, 0, -0.2, -0.1, 0, 0, -0.3]  # 温暖模式
                }
                
                bands = mode_presets.get(mode, mode_presets['smart'])
                self.audio_data = eq.anti_ai_equalize(
                    self.audio_data, 
                    bands, 
                    preserve_natural=True
                )
            else:
                # 使用传统增强版均衡器
                from src.effects.enhanced_equalizer import EnhancedEqualizer
                eq = EnhancedEqualizer(sample_rate=self.sample_rate)
                processed_audio = eq.one_click_eq(self.audio_data, mode=mode)
                
                # 防止处理累积误差，确保数值稳定
                processed_audio = np.clip(processed_audio, -1.0, 1.0)
                
                self.audio_data = processed_audio
            return True
        except ImportError:
            print("均衡器模块不可用，使用基础EQ")
            # 降级到基础EQ
            return self.equalize([0]*9)  # 应用平坦EQ
        except Exception as e:
            print(f"智能EQ失败: {e}")
            return False

    def pitch_correction(self, semitones=0, strength=1.0):
        """音准调校 - 变调功能"""
        if self.audio_data is None:
            return False
            
        try:
            # 导入音准修正模块
            from src.audio_processing.pitch_correction import PitchCorrector
            corrector = PitchCorrector()
            
            # 使用更高级的音准修正方法
            self.audio_data = corrector.auto_tune(
                self.audio_data,
                self.sample_rate,
                strength=strength,
                pitch_shift_semitones=semitones
            )
            return True
        except ImportError:
            # 如果音准修正模块不可用，使用降级方案
            try:
                self.audio_data = librosa.effects.pitch_shift(
                    y=self.audio_data,
                    sr=self.sample_rate,
                    n_steps=semitones
                )
                return True
            except Exception as e:
                print(f"音准调校失败: {e}")
                return False
        except Exception as e:
            print(f"音准调校失败: {e}")
            return False
    
    def smart_pitch_correction(self, mode='smart', anti_ai=True):
        """智能一键音准校准（可选反AI痕迹）"""
        if self.audio_data is None:
            return False
        
        try:
            if anti_ai:
                # 使用反AI痕迹音准修正
                from src.audio_processing.anti_ai_processing import AntiAIPitchCorrector
                corrector = AntiAIPitchCorrector()
                
                # 根据模式选择参数
                if mode == 'aggressive':
                    strength = 0.9
                    preserve_expression = True
                    expression_intensity = 0.3
                elif mode == 'gentle':
                    strength = 0.5
                    preserve_expression = True
                    expression_intensity = 0.6
                elif mode == 'adaptive':
                    strength = 0.7
                    preserve_expression = True
                    expression_intensity = 0.5
                else:  # smart模式
                    strength = 0.7
                    preserve_expression = True
                    expression_intensity = 0.4
                
                processed_audio = corrector.anti_ai_auto_tune(
                    self.audio_data,
                    self.sample_rate,
                    strength=strength,
                    preserve_expression=preserve_expression,
                    expression_intensity=expression_intensity
                )
                
                # 防止处理累积误差，确保数值稳定
                processed_audio = np.clip(processed_audio, -1.0, 1.0)
                
                self.audio_data = processed_audio
            else:
                # 使用传统增强版音准修正
                from src.audio_processing.enhanced_pitch_correction import EnhancedPitchCorrector
                corrector = EnhancedPitchCorrector()
                processed_audio = corrector.one_click_tune(
                    self.audio_data,
                    self.sample_rate,
                    mode=mode
                )
                
                # 防止处理累积误差，确保数值稳定
                processed_audio = np.clip(processed_audio, -1.0, 1.0)
                
                self.audio_data = processed_audio
            return True
        except ImportError:
            print("音准修正模块不可用，使用基础校准")
            # 降级到基础校准
            return self.pitch_correction(strength=0.5)
        except Exception as e:
            print(f"智能音准校准失败: {e}")
            return False

    def smart_master(self, mode='smart'):
        """智能母带处理"""
        if self.audio_data is None:
            return False
        
        try:
            # 导入增强版母带处理模块
            from src.effects.enhanced_mastering import EnhancedMasteringProcessor
            mastering_proc = EnhancedMasteringProcessor(sample_rate=self.sample_rate)
            
            # 应用智能母带处理
            self.audio_data = mastering_proc.one_click_master(
                self.audio_data,
                mode=mode
            )
            return True
        except ImportError:
            print("增强版母带处理模块不可用，使用基础处理")
            # 降级到基础母带处理
            return self.apply_basic_mastering()
        except Exception as e:
            print(f"智能母带处理失败: {e}")
            return False
    
    def apply_basic_mastering(self):
        """应用基础母带处理作为降级方案"""
        if self.audio_data is None:
            return False
        
        # 简单的响度调整作为基础母带处理
        current_rms = np.sqrt(np.mean(self.audio_data ** 2))
        target_rms = 0.1  # 目标RMS值
        gain = target_rms / (current_rms + 1e-10)
        gain = min(gain, 1.5)  # 限制最大增益
        self.audio_data = self.audio_data * gain
        
        # 应用限制以避免削波
        self.audio_data = np.clip(self.audio_data, -1.0, 1.0)
        
        return True


class PitchCorrectionWidget(QWidget):
    """音准调校界面"""
    
    def __init__(self, processor):
        super().__init__()
        self.processor = processor
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 音准调整滑块
        h_layout = QHBoxLayout()
        h_layout.addWidget(QLabel("音准调整 (半音):"))
        self.pitch_slider = QLabel("0")
        h_layout.addWidget(self.pitch_slider)
        layout.addLayout(h_layout)
        
        # 对比显示控制
        comparison_layout = QHBoxLayout()
        self.show_comparison_checkbox = QCheckBox("显示前后对比")
        self.show_comparison_checkbox.stateChanged.connect(self.toggle_comparison_display)
        comparison_layout.addWidget(self.show_comparison_checkbox)
        layout.addLayout(comparison_layout)
        
        self.pitch_control = None  # 会在主窗口中初始化
        
        # 应用按钮
        btn_layout = QHBoxLayout()
        self.apply_btn = QPushButton("应用音准调整")
        self.apply_btn.clicked.connect(self.apply_pitch_correction)
        btn_layout.addWidget(self.apply_btn)
        
        # 智能一键校准按钮
        self.smart_tune_btn = QPushButton("智能一键校准")
        self.smart_tune_btn.clicked.connect(self.apply_smart_pitch_correction)
        btn_layout.addWidget(self.smart_tune_btn)
        
        # 反AI痕迹选项
        anti_ai_layout = QHBoxLayout()
        self.anti_ai_checkbox = QCheckBox("反AI痕迹处理")
        self.anti_ai_checkbox.setChecked(True)  # 默认启用
        anti_ai_layout.addWidget(self.anti_ai_checkbox)
        
        # 校准模式选择
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("校准模式:"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["智能模式", "激进模式", "温和模式", "自适应模式"])
        mode_layout.addWidget(self.mode_combo)
        
        layout.addLayout(btn_layout)
        layout.addLayout(anti_ai_layout)
        layout.addLayout(mode_layout)
        
        # 音频可视化
        self.canvas = MatplotlibWidget()
        layout.addWidget(self.canvas)
        
        self.setLayout(layout)
    
    def update_visualization(self, show_comparison=False):
        """更新音频可视化"""
        if self.processor.audio_data is not None:
            if show_comparison and self.processor.backup_audio is not None:
                # 显示对比图
                self.canvas.plot_comparison(
                    self.processor.backup_audio[:min(len(self.processor.backup_audio), 10000)],
                    self.processor.audio_data[:min(len(self.processor.audio_data), 10000)],
                    sample_rate=self.processor.sample_rate,
                    plot_type="waveform"
                )
            else:
                self.canvas.plot_waveform(self.processor.audio_data[:10000])  # 只显示前10000个采样点
    
    def apply_pitch_correction(self):
        """应用音准调整"""
        if self.pitch_control:
            semitones = self.pitch_control.value() / 10.0  # 假设滑块范围是-120到120，对应-12到12半音
            # 保存当前处理后的音频作为备份，以便对比
            if self.processor.audio_data is not None:
                self.processor.backup_audio = self.processor.audio_data.copy()
            if self.processor.pitch_correction(semitones):
                self.update_visualization(show_comparison=True)
                QMessageBox.information(self, "成功", "音准调整已应用！")
    
    def toggle_comparison_display(self, state):
        """切换对比显示"""
        if self.processor.audio_data is not None:
            if state == Qt.Checked:
                # 显示对比图
                self.update_visualization(show_comparison=True)
            else:
                # 显示处理后的音频
                self.update_visualization(show_comparison=False)
    
    def apply_smart_pitch_correction(self):
        """应用智能音准校准"""
        # 获取选择的模式
        mode_idx = self.mode_combo.currentIndex()
        modes = ['smart', 'aggressive', 'gentle', 'adaptive']
        selected_mode = modes[mode_idx]
        
        # 获取反AI痕迹选项
        anti_ai = self.anti_ai_checkbox.isChecked()
        
        # 保存当前处理后的音频作为备份，以便对比
        if self.processor.audio_data is not None:
            self.processor.backup_audio = self.processor.audio_data.copy()
        
        # 执行智能校准
        if self.processor.smart_pitch_correction(mode=selected_mode, anti_ai=anti_ai):
            self.update_visualization(show_comparison=True)
            mode_names = ['智能模式', '激进模式', '温和模式', '自适应模式']
            anti_ai_text = "已启用" if anti_ai else "已禁用"
            QMessageBox.information(self, "成功", f"智能音准校准已完成！\n模式: {mode_names[mode_idx]}\n反AI痕迹: {anti_ai_text}")
        else:
            QMessageBox.critical(self, "错误", "智能音准校准失败！")


class EQWidget(QWidget):
    """EQ调节界面"""
    
    def __init__(self, processor):
        super().__init__()
        self.processor = processor
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # EQ频段控制
        self.eq_controls = []
        
        eq_bands = [
            ("低频 (20Hz-250Hz)", -12, 12),
            ("中低频 (250Hz-500Hz)", -12, 12),
            ("中频 (500Hz-2kHz)", -12, 12),
            ("中高频 (2kHz-4kHz)", -12, 12),
            ("高频 (4kHz-20kHz)", -12, 12)
        ]
        
        for band_name, min_val, max_val in eq_bands:
            h_layout = QHBoxLayout()
            h_layout.addWidget(QLabel(band_name))
            label = QLabel("0 dB")
            h_layout.addWidget(label)
            # slider将在主窗口初始化后添加
            layout.addLayout(h_layout)
            
            self.eq_controls.append({
                'name': band_name,
                'slider': None,  # 将在主窗口中初始化
                'label': label
            })
        
        # 应用EQ按钮
        eq_button_layout = QHBoxLayout()
        self.apply_eq_btn = QPushButton("应用EQ调节")
        self.apply_eq_btn.clicked.connect(self.apply_eq)
        eq_button_layout.addWidget(self.apply_eq_btn)
        
        # 智能EQ按钮
        self.smart_eq_btn = QPushButton("智能一键EQ")
        self.smart_eq_btn.clicked.connect(self.apply_smart_eq)
        eq_button_layout.addWidget(self.smart_eq_btn)
        
        # 反AI痕迹选项
        eq_anti_ai_layout = QHBoxLayout()
        self.eq_anti_ai_checkbox = QCheckBox("反AI痕迹处理")
        self.eq_anti_ai_checkbox.setChecked(True)  # 默认启用
        eq_anti_ai_layout.addWidget(self.eq_anti_ai_checkbox)
        
        # 对比显示控制
        eq_comparison_layout = QHBoxLayout()
        self.eq_show_comparison_checkbox = QCheckBox("显示前后对比")
        self.eq_show_comparison_checkbox.stateChanged.connect(self.toggle_eq_comparison_display)
        eq_comparison_layout.addWidget(self.eq_show_comparison_checkbox)
        
        # EQ模式选择
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("EQ模式:"))
        self.eq_mode_combo = QComboBox()
        self.eq_mode_combo.addItems(["智能模式", "人声模式", "乐器模式", "混音模式", "平坦模式", "明亮模式", "温暖模式"])
        mode_layout.addWidget(self.eq_mode_combo)
        
        layout.addLayout(eq_button_layout)
        layout.addLayout(eq_anti_ai_layout)
        layout.addLayout(eq_comparison_layout)
        layout.addLayout(mode_layout)
        
        # 频谱可视化
        self.spectrum_canvas = MatplotlibWidget()
        layout.addWidget(self.spectrum_canvas)
        
        self.setLayout(layout)
    
    def update_spectrum(self, show_comparison=False):
        """更新频谱可视化"""
        if self.processor.audio_data is not None:
            if show_comparison and self.processor.backup_audio is not None:
                # 显示对比图
                self.spectrum_canvas.plot_comparison(
                    self.processor.backup_audio[:min(len(self.processor.backup_audio), 8192)],
                    self.processor.audio_data[:min(len(self.processor.audio_data), 8192)],
                    sample_rate=self.processor.sample_rate,
                    plot_type="spectrum"
                )
            else:
                # 计算频谱
                spectrum = np.abs(np.fft.fft(self.processor.audio_data[:8192]))  # 取前8192个点
                frequencies = np.fft.fftfreq(len(self.processor.audio_data[:8192]), 1/self.processor.sample_rate)
                self.spectrum_canvas.plot_spectrum(frequencies[:len(frequencies)//2], spectrum[:len(spectrum)//2])
    
    def apply_eq(self):
        """应用EQ调节"""
        bands = []
        for control in self.eq_controls:
            gain = control['slider'].value() / 10.0  # 假设滑块范围映射到-12到12dB
            bands.append(gain)
        
        # 保存当前处理后的音频作为备份，以便对比
        if self.processor.audio_data is not None:
            self.processor.backup_audio = self.processor.audio_data.copy()
        
        if self.processor.equalize(bands):
            self.update_spectrum(show_comparison=True)
            QMessageBox.information(self, "成功", "EQ调节已应用！")
    
    def toggle_eq_comparison_display(self, state):
        """切换EQ对比显示"""
        if self.processor.audio_data is not None:
            if state == Qt.Checked:
                # 显示对比图
                self.update_spectrum(show_comparison=True)
            else:
                # 显示处理后的音频
                self.update_spectrum(show_comparison=False)
    
    def apply_smart_eq(self):
        """应用智能EQ"""
        # 获取选择的模式
        mode_idx = self.eq_mode_combo.currentIndex()
        modes = ['smart', 'vocal', 'instrumental', 'mix', 'flat', 'bright', 'warm']
        selected_mode = modes[mode_idx]
        
        # 获取反AI痕迹选项
        anti_ai = self.eq_anti_ai_checkbox.isChecked()
        
        # 保存当前处理后的音频作为备份，以便对比
        if self.processor.audio_data is not None:
            self.processor.backup_audio = self.processor.audio_data.copy()
        
        # 执行智能EQ
        if self.processor.smart_equalize(mode=selected_mode, anti_ai=anti_ai):
            self.update_spectrum(show_comparison=True)
            mode_names = ['智能模式', '人声模式', '乐器模式', '混音模式', '平坦模式', '明亮模式', '温暖模式']
            anti_ai_text = "已启用" if anti_ai else "已禁用"
            QMessageBox.information(self, "成功", f"智能EQ已完成！\n模式: {mode_names[mode_idx]}\n反AI痕迹: {anti_ai_text}")
        else:
            QMessageBox.critical(self, "错误", "智能EQ失败！")


class RecordingEngineeringWidget(QWidget):
    """录音工程界面"""
    
    def __init__(self, processor):
        super().__init__()
        self.processor = processor
        self.recording_session = None
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 初始化录音会话
        from src.audio_processing.recording import RecordingSession
        from src.audio_processing.audio_to_midi import AudioToMidiConverter
        self.recording_session = RecordingSession(sample_rate=self.processor.sample_rate if self.processor.sample_rate else 44100)
        
        # 初始化时添加一个默认音轨
        self.recording_session.multi_track_editor.add_track()
        
        # 录音控制
        recording_layout = QHBoxLayout()
        self.record_btn = QPushButton("开始录音")
        self.stop_btn = QPushButton("停止录音")
        self.play_btn = QPushButton("播放")
        self.add_track_btn = QPushButton("添加空音轨")
        self.load_track_btn = QPushButton("加载外部音轨")
        
        self.record_btn.clicked.connect(self.start_recording)
        self.stop_btn.clicked.connect(self.stop_recording)
        self.play_btn.clicked.connect(self.play_session)
        self.add_track_btn.clicked.connect(self.add_track)
        self.load_track_btn.clicked.connect(self.load_external_track)
        
        recording_layout.addWidget(self.record_btn)
        recording_layout.addWidget(self.stop_btn)
        recording_layout.addWidget(self.play_btn)
        recording_layout.addWidget(self.add_track_btn)
        recording_layout.addWidget(self.load_track_btn)
        
        layout.addLayout(recording_layout)
        
        # 轨道管理
        tracks_label = QLabel("轨道管理:")
        layout.addWidget(tracks_label)
        
        # 音轨列表
        self.tracks_list = QListWidget()
        self.tracks_list.setSelectionMode(QAbstractItemView.SingleSelection)  # 单选模式
        layout.addWidget(self.tracks_list)
        
        # 初始化音轨列表显示
        self.update_tracks_list()
        
        # 混音控制
        mix_layout = QHBoxLayout()
        self.mix_btn = QPushButton("混音")
        self.export_btn = QPushButton("导出项目")
        self.midi_btn = QPushButton("转换为MIDI")
        self.staff_btn = QPushButton("生成五线谱")
        
        self.mix_btn.clicked.connect(self.mix_tracks)
        self.export_btn.clicked.connect(self.export_project)
        self.midi_btn.clicked.connect(self.convert_to_midi)
        self.staff_btn.clicked.connect(self.generate_staff)
        
        mix_layout.addWidget(self.mix_btn)
        mix_layout.addWidget(self.export_btn)
        mix_layout.addWidget(self.midi_btn)
        mix_layout.addWidget(self.staff_btn)
        
        layout.addLayout(mix_layout)
        
        self.setLayout(layout)
    
    def start_recording(self):
        """开始录音"""
        if self.recording_session:
            self.recording_session.recorder.start_recording()
            QMessageBox.information(self, "提示", "开始录音...")
    
    def stop_recording(self):
        """停止录音"""
        if self.recording_session:
            recorded_audio = self.recording_session.recorder.stop_recording()
            if len(recorded_audio) > 0:
                # 添加到当前选中的音轨或新建音轨
                current_track_idx = self.tracks_list.currentRow()
                if current_track_idx >= 0:
                    self.recording_session.multi_track_editor.tracks[current_track_idx].audio_data = recorded_audio
                else:
                    # 添加新音轨
                    track_idx = self.recording_session.multi_track_editor.add_track()
                    self.recording_session.multi_track_editor.tracks[track_idx].audio_data = recorded_audio
                self.update_tracks_list()
                QMessageBox.information(self, "成功", "录音完成并添加到音轨！")
    
    def play_session(self):
        """播放会话"""
        if self.recording_session:
            self.recording_session.play_session()
            
    def add_track(self):
        """添加音轨"""
        if self.recording_session:
            self.recording_session.multi_track_editor.add_track()
            self.update_tracks_list()
            
    def load_external_track(self):
        """加载外部音轨文件"""
        if not self.recording_session:
            QMessageBox.warning(self, "警告", "录音会话未初始化！")
            return
            
        # 选择音频文件
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "选择音频文件",
            "",
            "音频文件 (*.wav *.mp3 *.flac *.aiff *.ogg);;所有文件 (*.*)"
        )
        
        if not filepath:
            return
            
        try:
            # 加载音频文件
            audio_data, sample_rate = librosa.load(filepath, sr=None)
            
            # 创建新音轨
            track_idx = self.recording_session.multi_track_editor.add_track()
            track = self.recording_session.multi_track_editor.tracks[track_idx]
            
            # 设置音轨音频数据
            track.audio_data = audio_data
            track.sample_rate = sample_rate
            
            # 从文件名提取音轨名称
            import os
            filename = os.path.basename(filepath)
            name_without_ext = os.path.splitext(filename)[0]
            track.name = f"{name_without_ext}"[:20]  # 限制名称长度
            
            # 更新界面
            self.update_tracks_list()
            
            QMessageBox.information(
                self, 
                "成功", 
                f"外部音轨加载成功！\n文件: {filename}\n采样率: {sample_rate}Hz\n长度: {len(audio_data)/sample_rate:.2f}秒"
            )
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载音频文件失败: {str(e)}")
    def update_tracks_list(self):
        """更新音轨列表"""
        if self.recording_session:
            self.tracks_list.clear()
            for i, track in enumerate(self.recording_session.multi_track_editor.tracks):
                self.tracks_list.addItem(f"音轨 {i+1}: {track.name} ({'静音' if track.muted else '正常'})")
    
    def mix_tracks(self):
        """混音"""
        if self.recording_session:
            mixed_audio = self.recording_session.multi_track_editor.mix_down()
            if len(mixed_audio) > 0:
                # 更新处理器的音频数据
                if len(mixed_audio.shape) > 1:
                    # 立体声转单声道用于后续处理
                    self.processor.audio_data = np.mean(mixed_audio, axis=1)
                else:
                    self.processor.audio_data = mixed_audio
                QMessageBox.information(self, "成功", f"混音完成！输出长度: {len(mixed_audio)} 样本")
            
    def export_project(self):
        """导出项目"""
        if self.recording_session:
            filepath, _ = QFileDialog.getSaveFileName(
                self, 
                "导出项目", 
                "", 
                "WAV文件 (*.wav);;FLAC文件 (*.flac)"
            )
            
            if filepath:
                if self.recording_session.multi_track_editor.export_project(filepath):
                    QMessageBox.information(self, "成功", "项目已导出！")
                else:
                    QMessageBox.critical(self, "错误", "导出失败！")

    def convert_to_midi(self):
        """将音轨转换为MIDI文件"""
        if self.recording_session and self.recording_session.multi_track_editor.tracks:
            # 获取当前选中的音轨
            current_track_idx = self.tracks_list.currentRow()
            if current_track_idx >= 0 and current_track_idx < len(self.recording_session.multi_track_editor.tracks):
                track = self.recording_session.multi_track_editor.tracks[current_track_idx]
                
                if track.audio_data is not None and len(track.audio_data) > 0:
                    # 选择MIDI文件保存路径
                    midi_filepath, _ = QFileDialog.getSaveFileName(
                        self,
                        "保存MIDI文件",
                        "",
                        "MIDI文件 (*.mid);;所有文件 (*.*)"
                    )
                    
                    if midi_filepath:
                        try:
                            # 创建MIDI转换器
                            converter = AudioToMidiConverter(sample_rate=track.sample_rate)
                            
                            # 执行转换
                            success = converter.convert_audio_to_midi(
                                track.audio_data,
                                midi_filepath,
                                track_name=track.name
                            )
                            
                            if success:
                                QMessageBox.information(self, "成功", f"音频已成功转换为MIDI文件！\n保存至: {midi_filepath}")
                            else:
                                QMessageBox.critical(self, "错误", "MIDI转换失败！")
                        except Exception as e:
                            QMessageBox.critical(self, "错误", f"MIDI转换过程中出现错误: {str(e)}")
                else:
                    QMessageBox.warning(self, "警告", "所选音轨中没有音频数据！")
            else:
                QMessageBox.warning(self, "警告", "请选择一个音轨进行转换！")
        else:
            QMessageBox.warning(self, "警告", "没有可用的音轨数据！")

    def generate_staff(self):
        """生成五线谱图片"""
        if self.recording_session and self.recording_session.multi_track_editor.tracks:
            # 获取当前选中的音轨
            current_track_idx = self.tracks_list.currentRow()
            if current_track_idx >= 0 and current_track_idx < len(self.recording_session.multi_track_editor.tracks):
                track = self.recording_session.multi_track_editor.tracks[current_track_idx]
                
                if track.audio_data is not None and len(track.audio_data) > 0:
                    # 选择五线谱图片保存路径
                    staff_filepath, selected_filter = QFileDialog.getSaveFileName(
                        self,
                        "保存五线谱图片",
                        "",
                        "PNG图片 (*.png);;SVG矢量图 (*.svg);;所有文件 (*.*)"
                    )
                    
                    if staff_filepath:
                        try:
                            # 确定图片格式
                            if "SVG" in selected_filter:
                                format_type = "svg"
                                if not staff_filepath.endswith('.svg'):
                                    staff_filepath += '.svg'
                            else:
                                format_type = "png"
                                if not staff_filepath.endswith('.png'):
                                    staff_filepath += '.png'
                            
                            # 创建图形化五线谱生成器
                            from src.audio_processing.staff_image_generator import StaffImageGenerator
                            generator = StaffImageGenerator(sample_rate=track.sample_rate)
                            
                            # 执行转换
                            success = generator.generate_staff_image(
                                track.audio_data,
                                staff_filepath,
                                track_name=track.name,
                                format=format_type
                            )
                            
                            if success:
                                QMessageBox.information(self, "成功", f"音频已成功转换为五线谱图片！\n保存至: {staff_filepath}\n格式: {format_type.upper()}")
                            else:
                                QMessageBox.critical(self, "错误", "五线谱图片生成失败！")
                        except Exception as e:
                            QMessageBox.critical(self, "错误", f"五线谱图片生成过程中出现错误: {str(e)}")
                else:
                    QMessageBox.warning(self, "警告", "所选音轨中没有音频数据！")
            else:
                QMessageBox.warning(self, "警告", "请选择一个音轨进行转换！")
        else:
            QMessageBox.warning(self, "警告", "没有可用的音轨数据！")


class MasteringWidget(QWidget):
    """母带制作界面"""
    
    def __init__(self, processor):
        super().__init__()
        self.processor = processor
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 母带处理参数
        params_layout = QHBoxLayout()
        
        # 压缩器
        compressor_group = QVBoxLayout()
        compressor_group.addWidget(QLabel("压缩器:"))
        self.compressor_threshold = QSlider(Qt.Horizontal)
        self.compressor_threshold.setRange(-60, 0)  # -60dB 到 0dB
        self.compressor_threshold.setValue(-20)
        self.compressor_threshold_label = QLabel("-20dB")
        compressor_group.addWidget(self.compressor_threshold_label)
        compressor_group.addWidget(self.compressor_threshold)
        params_layout.addLayout(compressor_group)
        
        # 限制器
        limiter_group = QVBoxLayout()
        limiter_group.addWidget(QLabel("限制器:"))
        self.limiter_ceiling = QSlider(Qt.Horizontal)
        self.limiter_ceiling.setRange(-20, 0)  # -20dB 到 0dB
        self.limiter_ceiling.setValue(-1)
        self.limiter_ceiling_label = QLabel("-1dB")
        limiter_group.addWidget(self.limiter_ceiling_label)
        limiter_group.addWidget(self.limiter_ceiling)
        params_layout.addLayout(limiter_group)
        
        # 立体声增强
        stereo_group = QVBoxLayout()
        stereo_group.addWidget(QLabel("立体声增强:"))
        self.stereo_width = QSlider(Qt.Horizontal)
        self.stereo_width.setRange(0, 200)  # 0% 到 200%
        self.stereo_width.setValue(100)
        self.stereo_width_label = QLabel("1.0x")
        stereo_group.addWidget(self.stereo_width_label)
        stereo_group.addWidget(self.stereo_width)
        params_layout.addLayout(stereo_group)
        
        layout.addLayout(params_layout)
        
        # 连接信号
        self.compressor_threshold.valueChanged.connect(self.update_compressor_label)
        self.limiter_ceiling.valueChanged.connect(self.update_limiter_label)
        self.stereo_width.valueChanged.connect(self.update_stereo_label)
        
        # 预设选择
        preset_layout = QHBoxLayout()
        preset_layout.addWidget(QLabel("预设:"))
        self.preset_combo = QComboBox()
        self.preset_combo.addItems(["平衡", "响亮", "动态"])
        preset_layout.addWidget(self.preset_combo)
        
        layout.addLayout(preset_layout)
        
        # 应用母带处理
        mastering_button_layout = QHBoxLayout()
        self.apply_mastering_btn = QPushButton("应用母带处理")
        self.apply_mastering_btn.clicked.connect(self.apply_mastering)
        mastering_button_layout.addWidget(self.apply_mastering_btn)
        
        # 智能母带处理按钮
        self.smart_master_btn = QPushButton("智能一键母带")
        self.smart_master_btn.clicked.connect(self.apply_smart_mastering)
        mastering_button_layout.addWidget(self.smart_master_btn)
        
        # 对比显示控制
        master_comparison_layout = QHBoxLayout()
        self.master_show_comparison_checkbox = QCheckBox("显示前后对比")
        self.master_show_comparison_checkbox.stateChanged.connect(self.toggle_master_comparison_display)
        master_comparison_layout.addWidget(self.master_show_comparison_checkbox)
        
        # 母带模式选择
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("母带模式:"))
        self.master_mode_combo = QComboBox()
        self.master_mode_combo.addItems(["智能模式", "响亮模式", "动态模式", "广播模式", "流媒体模式", "黑胶模式"])
        mode_layout.addWidget(self.master_mode_combo)
        
        layout.addLayout(mastering_button_layout)
        layout.addLayout(master_comparison_layout)
        layout.addLayout(mode_layout)
        
        # 母带预览
        self.mastering_preview = MatplotlibWidget()
        layout.addWidget(self.mastering_preview)
        
        self.setLayout(layout)
    
    def update_compressor_label(self, value):
        """更新压缩器标签"""
        self.compressor_threshold_label.setText(f"{value}dB")
    
    def update_limiter_label(self, value):
        """更新限制器标签"""
        self.limiter_ceiling_label.setText(f"{value}dB")
    
    def update_stereo_label(self, value):
        """更新立体声宽度标签"""
        self.stereo_width_label.setText(f"{value/100.0:.1f}x")
    
    def apply_mastering(self):
        """应用母带处理"""
        try:
            # 导入母带处理模块
            from src.effects.mastering import MasteringProcessor, Compressor, Limiter, StereoEnhancer
            
            # 保存当前处理后的音频作为备份，以便对比
            if self.processor.audio_data is not None:
                self.processor.backup_audio = self.processor.audio_data.copy()
            
            # 创建母带处理器
            mastering_proc = MasteringProcessor(sample_rate=self.processor.sample_rate)
            
            # 获取参数值
            threshold = self.compressor_threshold.value()
            ceiling = self.limiter_ceiling.value()
            stereo_width = self.stereo_width.value() / 100.0  # 转换为比例
            
            # 设置参数
            mastering_proc.chain.compressor = Compressor(
                threshold_db=threshold,
                sample_rate=self.processor.sample_rate
            )
            mastering_proc.chain.limiter = Limiter(
                threshold_db=ceiling,
                sample_rate=self.processor.sample_rate,
                high_freq_protection=False  # 暂时关闭避免新问题
            )
            mastering_proc.chain.stereo_enhancer = StereoEnhancer(width_factor=stereo_width)
            
            # 获取预设选择
            preset_idx = self.preset_combo.currentIndex()
            presets = ['balanced', 'loud', 'dynamic']
            selected_preset = presets[preset_idx]
            
            # 应用母带处理
            if self.processor.audio_data is not None:
                processed_audio = mastering_proc.process_audio(
                    self.processor.audio_data, 
                    preset=selected_preset
                )
                
                # 防止处理累积误差，确保数值稳定
                processed_audio = np.clip(processed_audio, -1.0, 1.0)
                
                self.processor.audio_data = processed_audio
                
                # 更新预览
                self.mastering_preview.plot_comparison(
                    self.processor.backup_audio[:min(len(self.processor.backup_audio), 10000)],
                    self.processor.audio_data[:min(len(self.processor.audio_data), 10000)],
                    sample_rate=self.processor.sample_rate,
                    plot_type="waveform"
                )
                
                QMessageBox.information(
                    self, 
                    "成功", 
                    f"母带处理已完成！\n参数: 阈值={threshold}dB, 限制={ceiling}dB, 立体声宽度={stereo_width:.1f}x"
                )
            else:
                QMessageBox.warning(self, "警告", "没有音频数据可供处理！")
        
        except ImportError:
            QMessageBox.critical(self, "错误", "母带处理模块不可用，请检查依赖！")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"母带处理失败: {str(e)}")
    
    def toggle_master_comparison_display(self, state):
        """切换母带对比显示"""
        if self.processor.audio_data is not None:
            if state == Qt.Checked:
                # 显示对比图
                self.mastering_preview.plot_comparison(
                    self.processor.backup_audio[:min(len(self.processor.backup_audio), 10000)],
                    self.processor.audio_data[:min(len(self.processor.audio_data), 10000)],
                    sample_rate=self.processor.sample_rate,
                    plot_type="waveform"
                )
            else:
                # 显示处理后的音频
                time_axis = np.linspace(0, len(self.processor.audio_data)/self.processor.sample_rate, 
                                      num=min(len(self.processor.audio_data), 10000))
                audio_slice = self.processor.audio_data[:min(len(self.processor.audio_data), 10000)]
                self.mastering_preview.figure.clear()
                ax = self.mastering_preview.figure.add_subplot(111)
                ax.plot(time_axis, audio_slice)
                ax.set_title("音频波形预览")
                ax.set_xlabel("时间 (秒)")
                ax.set_ylabel("幅度")
                self.mastering_preview.canvas.draw()
    
    def apply_smart_mastering(self):
        """应用智能母带处理"""
        # 获取选择的模式
        mode_idx = self.master_mode_combo.currentIndex()
        modes = ['smart', 'loud', 'dynamic', 'radio', 'streaming', 'vinyl']
        selected_mode = modes[mode_idx]
        
        # 保存当前处理后的音频作为备份，以便对比
        if self.processor.audio_data is not None:
            self.processor.backup_audio = self.processor.audio_data.copy()
        
        # 执行智能母带处理
        if self.processor.smart_master(mode=selected_mode):
            # 更新预览
            self.mastering_preview.plot_comparison(
                self.processor.backup_audio[:min(len(self.processor.backup_audio), 10000)],
                self.processor.audio_data[:min(len(self.processor.audio_data), 10000)],
                sample_rate=self.processor.sample_rate,
                plot_type="waveform"
            )
            
            mode_names = ['智能模式', '响亮模式', '动态模式', '广播模式', '流媒体模式', '黑胶模式']
            QMessageBox.information(self, "成功", f"智能母带处理已完成！\n使用模式: {mode_names[mode_idx]}")
        else:
            QMessageBox.critical(self, "错误", "智能母带处理失败！")


class MatplotlibWidget(QWidget):
    """Matplotlib绘图组件"""
    
    def __init__(self):
        super().__init__()
        
        self.figure = Figure(figsize=(10, 6))
        self.canvas = FigureCanvas(self.figure)
        
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
    
    def plot_waveform(self, audio_data):
        """绘制波形图"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.plot(audio_data)
        ax.set_title("音频波形")
        ax.set_xlabel("采样点")
        ax.set_ylabel("幅度")
        self.canvas.draw()
    
    def plot_spectrum(self, frequencies, spectrum):
        """绘制频谱图"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.plot(frequencies, spectrum)
        ax.set_title("音频频谱")
        ax.set_xlabel("频率 (Hz)")
        ax.set_ylabel("幅度")
        ax.set_xlim([0, 5000])  # 只显示到5kHz
        self.canvas.draw()
    
    def plot_comparison(self, original_audio, processed_audio, sample_rate=22050, plot_type="waveform"):
        """绘制原始音频和处理后音频的对比图"""
        self.figure.clear()
        
        if plot_type == "waveform":
            # 绘制波形对比
            ax1 = self.figure.add_subplot(211)
            time_axis = np.linspace(0, len(original_audio)/sample_rate, num=len(original_audio))
            ax1.plot(time_axis, original_audio, label="原始音频", color='blue')
            ax1.set_title("原始音频波形")
            ax1.set_xlabel("时间 (秒)")
            ax1.set_ylabel("幅度")
            ax1.legend()
            ax1.grid(True)
            
            ax2 = self.figure.add_subplot(212)
            time_axis = np.linspace(0, len(processed_audio)/sample_rate, num=len(processed_audio))
            ax2.plot(time_axis, processed_audio, label="处理后音频", color='red')
            ax2.set_title("处理后音频波形")
            ax2.set_xlabel("时间 (秒)")
            ax2.set_ylabel("幅度")
            ax2.legend()
            ax2.grid(True)
            
        elif plot_type == "spectrum":
            # 计算频谱
            original_spectrum = np.abs(np.fft.fft(original_audio[:8192]))
            processed_spectrum = np.abs(np.fft.fft(processed_audio[:8192]))
            freqs = np.fft.fftfreq(len(original_audio[:8192]), 1/sample_rate)
            
            ax1 = self.figure.add_subplot(211)
            ax1.plot(freqs[:len(freqs)//2], 20*np.log10(original_spectrum[:len(original_spectrum)//2]+1e-10), 
                   label="原始音频", color='blue')
            ax1.set_title("原始音频频谱")
            ax1.set_xlabel("频率 (Hz)")
            ax1.set_ylabel("幅度 (dB)")
            ax1.set_xlim([0, 5000])
            ax1.legend()
            ax1.grid(True)
            
            ax2 = self.figure.add_subplot(212)
            ax2.plot(freqs[:len(freqs)//2], 20*np.log10(processed_spectrum[:len(processed_spectrum)//2]+1e-10), 
                   label="处理后音频", color='red')
            ax2.set_title("处理后音频频谱")
            ax2.set_xlabel("频率 (Hz)")
            ax2.set_ylabel("幅度 (dB)")
            ax2.set_xlim([0, 5000])
            ax2.legend()
            ax2.grid(True)
        
        self.figure.tight_layout()
        self.canvas.draw()
    
    def plot_overlay(self, original_audio, processed_audio, sample_rate=22050, plot_type="waveform"):
        """绘制原始音频和处理后音频的叠加图"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        if plot_type == "waveform":
            # 绘制波形叠加
            time_axis_orig = np.linspace(0, len(original_audio)/sample_rate, num=len(original_audio))
            time_axis_proc = np.linspace(0, len(processed_audio)/sample_rate, num=len(processed_audio))
            
            ax.plot(time_axis_orig, original_audio, label="原始音频", alpha=0.7, color='blue')
            ax.plot(time_axis_proc, processed_audio, label="处理后音频", alpha=0.7, color='red')
            ax.set_title("音频波形对比（叠加）")
            ax.set_xlabel("时间 (秒)")
            ax.set_ylabel("幅度")
        
        elif plot_type == "spectrum":
            # 计算频谱并绘制叠加
            original_spectrum = np.abs(np.fft.fft(original_audio[:8192]))
            processed_spectrum = np.abs(np.fft.fft(processed_audio[:8192]))
            freqs = np.fft.fftfreq(len(original_audio[:8192]), 1/sample_rate)
            
            ax.plot(freqs[:len(freqs)//2], 20*np.log10(original_spectrum[:len(original_spectrum)//2]+1e-10), 
                   label="原始音频", alpha=0.7, color='blue')
            ax.plot(freqs[:len(freqs)//2], 20*np.log10(processed_spectrum[:len(processed_spectrum)//2]+1e-10), 
                   label="处理后音频", alpha=0.7, color='red')
            ax.set_title("音频频谱对比（叠加）")
            ax.set_xlabel("频率 (Hz)")
            ax.set_ylabel("幅度 (dB)")
            ax.set_xlim([0, 5000])
        
        ax.legend()
        ax.grid(True)
        self.figure.tight_layout()
        self.canvas.draw()


class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        self.processor = AudioProcessor()
        self.player = None
        self.current_playback_mode = "processed"  # 默认播放处理后音频
        self.compare_mode = None
        self.init_ui()
        self.init_player()
        
    def init_ui(self):
        self.setWindowTitle("AI音乐后期工程师 - 音乐修音软件")
        self.setGeometry(100, 100, 1200, 800)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 添加播放控制栏
        self.add_playback_controls(main_layout)
        
        # 菜单栏
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu('文件')
        
        load_action = QAction('加载音频', self)
        load_action.triggered.connect(self.load_audio)
        file_menu.addAction(load_action)
        
        save_action = QAction('保存音频', self)
        save_action.triggered.connect(self.save_audio)
        file_menu.addAction(save_action)
        
        # 视图菜单
        view_menu = menubar.addMenu('视图')
        
        self.compare_action = QAction('切换对比显示', self)
        self.compare_action.setCheckable(True)
        self.compare_action.triggered.connect(self.toggle_global_comparison)
        view_menu.addAction(self.compare_action)
        
        # 工具菜单
        tools_menu = menubar.addMenu('工具')
        
        reset_action = QAction('重置音频', self)
        reset_action.triggered.connect(self.reset_audio)
        tools_menu.addAction(reset_action)
        
        # 创建选项卡
        self.tabs = QTabWidget()
        self.pitch_tab = PitchCorrectionWidget(self.processor)
        self.eq_tab = EQWidget(self.processor)
        self.recording_tab = RecordingEngineeringWidget(self.processor)
        self.mastering_tab = MasteringWidget(self.processor)
        
        self.tabs.addTab(self.pitch_tab, "音准调校")
        self.tabs.addTab(self.eq_tab, "EQ调节")
        self.tabs.addTab(self.recording_tab, "录音工程")
        self.tabs.addTab(self.mastering_tab, "母带制作")
        
        main_layout.addWidget(self.tabs)
        
        # 状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪")
        
        # 初始化控件引用
        self.init_controls()
        
    def add_playback_controls(self, main_layout):
        """添加播放控制界面"""
        # 播放控制组
        playback_group = QVBoxLayout()
        
        # 播放控制按钮
        playback_buttons_layout = QHBoxLayout()
        
        self.play_btn = QPushButton("播放")
        self.play_btn.clicked.connect(self.play_audio)
        self.play_btn.setEnabled(False)
        playback_buttons_layout.addWidget(self.play_btn)
        
        self.pause_btn = QPushButton("暂停")
        self.pause_btn.clicked.connect(self.pause_audio)
        self.pause_btn.setEnabled(False)
        playback_buttons_layout.addWidget(self.pause_btn)
        
        self.stop_btn = QPushButton("停止")
        self.stop_btn.clicked.connect(self.stop_audio)
        self.stop_btn.setEnabled(False)
        playback_buttons_layout.addWidget(self.stop_btn)
        
        # 对比播放按钮
        self.compare_btn = QPushButton("对比播放")
        self.compare_btn.clicked.connect(self.toggle_compare_playback)
        self.compare_btn.setEnabled(False)
        self.compare_btn.setToolTip("在处理后音频和原始音频间切换播放")
        playback_buttons_layout.addWidget(self.compare_btn)
        
        # 音量控制
        volume_layout = QHBoxLayout()
        volume_layout.addWidget(QLabel("音量:"))
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(100)
        self.volume_slider.valueChanged.connect(self.set_volume)
        volume_layout.addWidget(self.volume_slider)
        
        # 播放模式选择
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("播放模式:"))
        self.playback_mode_combo = QComboBox()
        self.playback_mode_combo.addItems(["处理后音频", "原始音频", "A/B对比"])
        self.playback_mode_combo.setCurrentIndex(0)
        self.playback_mode_combo.currentIndexChanged.connect(self.on_playback_mode_changed)
        mode_layout.addWidget(self.playback_mode_combo)
        playback_group.addLayout(mode_layout)
        
        # 进度条
        self.progress_slider = QSlider(Qt.Horizontal)
        self.progress_slider.setRange(0, 1000)
        self.progress_slider.sliderPressed.connect(self.progress_slider_pressed)
        self.progress_slider.sliderReleased.connect(self.progress_slider_released)
        self.progress_slider.sliderMoved.connect(self.progress_slider_moved)
        
        # 时间显示
        time_layout = QHBoxLayout()
        self.current_time_label = QLabel("00:00")
        self.total_time_label = QLabel("00:00")
        time_layout.addWidget(self.current_time_label)
        time_layout.addStretch()
        time_layout.addWidget(self.total_time_label)
        
        # 组装播放控制界面
        playback_group.addLayout(playback_buttons_layout)
        playback_group.addLayout(volume_layout)
        playback_group.addWidget(self.progress_slider)
        playback_group.addLayout(time_layout)
        
        # 添加到主布局
        main_layout.addLayout(playback_group)
        
        # 添加分隔线
        separator = QLabel()
        separator.setFrameStyle(QLabel.HLine)
        separator.setFixedHeight(2)
        main_layout.addWidget(separator)
    
    def init_player(self):
        """初始化音频播放器"""
        if SOUNDDEVICE_AVAILABLE:
            try:
                from src.audio_processing.player import AudioPlayer
                self.player = AudioPlayer(sample_rate=44100)
                
                # 连接播放器信号
                self.player.playback_started.connect(self.on_playback_started)
                self.player.playback_paused.connect(self.on_playback_paused)
                self.player.playback_stopped.connect(self.on_playback_stopped)
                self.player.playback_finished.connect(self.on_playback_finished)
                self.player.position_changed.connect(self.on_position_changed)
                self.player.duration_changed.connect(self.on_duration_changed)
                
                print("音频播放器初始化成功")
            except Exception as e:
                print(f"音频播放器初始化失败: {e}")
                self.player = None
        else:
            print("sounddevice库不可用，播放功能受限")
            self.player = None
    
    def init_controls(self):
        """初始化控件引用"""
        # 音准滑块
        self.pitch_slider = QSlider(Qt.Horizontal)
        self.pitch_slider.setRange(-120, 120)  # -12到12半音，乘以10
        self.pitch_slider.setValue(0)
        self.pitch_slider.valueChanged.connect(self.on_pitch_changed)
    
    # 播放控制方法
    def play_audio(self):
        """播放当前处理后的音频"""
        if not self.player or self.processor.audio_data is None:
            QMessageBox.warning(self, "警告", "请先加载音频文件！")
            return
            
        # 检查是否有处理痕迹
        has_processing = not np.array_equal(self.processor.audio_data, self.processor.original_audio)
        
        # 加载当前音频数据
        if self.player.load_audio(self.processor.audio_data, self.processor.sample_rate):
            self.player.play()
            
            # 显示处理状态
            if has_processing:
                processed_time = self.player.get_duration_seconds()
                self.status_bar.showMessage(f"播放处理后音频 ({processed_time:.1f}秒) - 可随时对比原始音频")
            else:
                self.status_bar.showMessage("播放原始音频")
    
    def pause_audio(self):
        """暂停音频"""
        if self.player:
            self.player.pause()
    
    def stop_audio(self):
        """停止音频"""
        if self.player:
            self.player.stop()
    
    def set_volume(self, value):
        """设置音量"""
        if self.player:
            volume = value / 100.0
            self.player.set_volume(volume)
    
    def toggle_compare_playback(self):
        """切换对比播放模式"""
        if not self.player or self.processor.audio_data is None or self.processor.original_audio is None:
            return
            
        # 切换播放源
        if hasattr(self, 'compare_mode') and self.compare_mode == "processed":
            # 切换到原始音频
            self.player.load_audio(self.processor.original_audio, self.processor.sample_rate)
            self.compare_mode = "original"
            self.compare_btn.setText("播放处理后")
            self.status_bar.showMessage("播放原始音频 - 点击对比播放切换回处理后")
        else:
            # 切换到处理后音频
            self.player.load_audio(self.processor.audio_data, self.processor.sample_rate)
            self.compare_mode = "processed"
            self.compare_btn.setText("播放原始")
            self.status_bar.showMessage("播放处理后音频 - 点击对比播放切换回原始")
            
        # 重新开始播放
        if self.player.is_playing_state() or self.player.is_paused_state():
            self.player.play()
    
    def on_playback_mode_changed(self, index):
        """播放模式改变事件"""
        if not self.player or self.processor.audio_data is None:
            return
            
        modes = ["processed", "original", "ab_compare"]
        self.current_playback_mode = modes[index]
        
        if index == 0:  # 处理后音频
            self.player.load_audio(self.processor.audio_data, self.processor.sample_rate)
            self.status_bar.showMessage("已切换到处理后音频")
        elif index == 1:  # 原始音频
            if self.processor.original_audio is not None:
                self.player.load_audio(self.processor.original_audio, self.processor.sample_rate)
                self.status_bar.showMessage("已切换到原始音频")
        elif index == 2:  # A/B对比
            self.status_bar.showMessage("A/B对比模式: 自动切换处理前后音频")
    
    def progress_slider_pressed(self):
        """进度条按下事件"""
        if self.player:
            self.player.pause()
    
    def progress_slider_released(self):
        """进度条释放事件"""
        if self.player:
            # 计算新的播放位置
            progress = self.progress_slider.value() / 1000.0
            new_position = int(progress * self.player.get_duration())
            self.player.set_position(new_position)
            if self.player.is_paused_state():
                self.player.play()
    
    def progress_slider_moved(self, value):
        """进度条移动事件"""
        if self.player:
            # 更新时间显示
            progress = value / 1000.0
            total_seconds = self.player.get_duration_seconds()
            current_seconds = progress * total_seconds
            self.current_time_label.setText(self.format_time(current_seconds))
    
    def format_time(self, seconds):
        """格式化时间显示"""
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"
    
    # 播放器信号处理
    def on_playback_started(self):
        """播放开始信号处理"""
        self.play_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)
        self.stop_btn.setEnabled(True)
        self.compare_btn.setEnabled(True)
        
        # 显示当前播放状态
        if hasattr(self, 'compare_mode') and self.compare_mode == "original":
            self.status_bar.showMessage("正在播放原始音频...")
        else:
            self.status_bar.showMessage("正在播放处理后音频...")
    
    def on_playback_paused(self):
        """播放暂停信号处理"""
        self.play_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.status_bar.showMessage("已暂停")
    
    def on_playback_stopped(self):
        """播放停止信号处理"""
        self.play_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        self.compare_btn.setEnabled(True)
        self.progress_slider.setValue(0)
        self.current_time_label.setText("00:00")
        
        # 重置对比模式
        if hasattr(self, 'compare_mode'):
            delattr(self, 'compare_mode')
            self.compare_btn.setText("对比播放")
        
        self.status_bar.showMessage("就绪")
    
    def on_playback_finished(self):
        """播放完成信号处理"""
        self.on_playback_stopped()
        self.status_bar.showMessage("播放完成")
    
    def on_position_changed(self, position):
        """播放位置改变信号处理"""
        if self.player:
            # 更新进度条
            duration = self.player.get_duration()
            if duration > 0:
                progress = int((position / duration) * 1000)
                self.progress_slider.setValue(progress)
            
            # 更新时间显示
            current_seconds = self.player.get_position_seconds()
            self.current_time_label.setText(self.format_time(current_seconds))
    
    def on_duration_changed(self, duration):
        """音频长度改变信号处理"""
        if self.player:
            total_seconds = self.player.get_duration_seconds()
            self.total_time_label.setText(self.format_time(total_seconds))
            
            # 启用播放按钮
            self.play_btn.setEnabled(True)
            self.pause_btn.setEnabled(False)
            self.stop_btn.setEnabled(False)
        
        # 将滑块添加到音准标签旁边
        if self.pitch_tab.layout() and self.pitch_tab.layout().itemAt(0):
            pitch_layout = self.pitch_tab.layout().itemAt(0).layout()
            if pitch_layout:
                pitch_layout.addWidget(self.pitch_slider)
        
        # 更新音准标签
        self.pitch_tab.pitch_slider = QLabel("0")
        # 重新排列布局以包含标签
        if self.pitch_tab.layout() and self.pitch_tab.layout().itemAt(0):
            pitch_layout = self.pitch_tab.layout().itemAt(0).layout()
            if pitch_layout:
                pitch_layout.insertWidget(1, self.pitch_tab.pitch_slider)
        
        # EQ控制滑块
        for i, control in enumerate(self.eq_tab.eq_controls):
            slider = QSlider(Qt.Horizontal)
            slider.setRange(-120, 120)  # -12到12dB，乘以10
            slider.setValue(0)
            slider.valueChanged.connect(lambda val, idx=i: self.on_eq_changed(val, idx))
            control['slider'] = slider
            
            # 将滑块插入到布局中
            if self.eq_tab.layout() and self.eq_tab.layout().itemAt(i):
                layout_item = self.eq_tab.layout().itemAt(i).layout()
                if layout_item:
                    layout_item.addWidget(slider)
    
    def on_pitch_changed(self, value):
        """音准变化回调"""
        pitch_value = value / 10.0
        self.pitch_tab.pitch_slider.setText(f"{pitch_value:+.1f}")
    
    def on_eq_changed(self, value, band_index):
        """EQ变化回调"""
        gain_value = value / 10.0
        control = self.eq_tab.eq_controls[band_index]
        control['label'].setText(f"{gain_value:+.1f} dB")
    
    def load_audio(self):
        """加载音频文件"""
        filepath, _ = QFileDialog.getOpenFileName(
            self, 
            "选择音频文件", 
            "", 
            "音频文件 (*.wav *.mp3 *.flac *.m4a *.ogg *.aiff)"
        )
        
        if filepath:
            if self.processor.load_audio(filepath):
                self.status_bar.showMessage(f"已加载: {filepath}")
                
                # 更新可视化
                self.pitch_tab.update_visualization()
                self.eq_tab.update_spectrum()
                # 母带制作预览也可以显示波形
                if self.processor.audio_data is not None:
                    time_axis = np.linspace(0, len(self.processor.audio_data)/self.processor.sample_rate, 
                                          num=min(len(self.processor.audio_data), 10000))
                    audio_slice = self.processor.audio_data[:min(len(self.processor.audio_data), 10000)]
                    self.mastering_tab.mastering_preview.figure.clear()
                    ax = self.mastering_tab.mastering_preview.figure.add_subplot(111)
                    ax.plot(time_axis, audio_slice)
                    ax.set_title("音频波形预览")
                    ax.set_xlabel("时间 (秒)")
                    ax.set_ylabel("幅度")
                    self.mastering_tab.mastering_preview.canvas.draw()
                
                # 更新播放器
                if self.player:
                    self.player.load_audio(self.processor.audio_data, self.processor.sample_rate)
                    self.status_bar.showMessage(f"已加载: {filepath} | 可播放")
                
                QMessageBox.information(self, "成功", "音频文件已加载！")
            else:
                QMessageBox.critical(self, "错误", "无法加载音频文件！")
    
    def save_audio(self):
        """保存音频文件"""
        filepath, _ = QFileDialog.getSaveFileName(
            self, 
            "保存音频文件", 
            "", 
            "WAV文件 (*.wav);;MP3文件 (*.mp3)"
        )
        
        if filepath:
            if self.processor.save_audio(filepath):
                self.status_bar.showMessage(f"已保存: {filepath}")
                QMessageBox.information(self, "成功", "音频文件已保存！")
            else:
                QMessageBox.critical(self, "错误", "无法保存音频文件！")
    
    def reset_audio(self):
        """重置音频"""
        if self.processor.original_audio is not None:
            self.processor.audio_data = self.processor.original_audio.copy()
            self.processor.backup_audio = self.processor.original_audio.copy()
            self.status_bar.showMessage("音频已重置！")
            
            # 更新可视化
            self.pitch_tab.update_visualization()
            self.eq_tab.update_spectrum()
            # 母带制作预览也可以显示波形
            if self.processor.audio_data is not None:
                time_axis = np.linspace(0, len(self.processor.audio_data)/self.processor.sample_rate, 
                                          num=min(len(self.processor.audio_data), 10000))
                audio_slice = self.processor.audio_data[:min(len(self.processor.audio_data), 10000)]
                self.mastering_tab.mastering_preview.figure.clear()
                ax = self.mastering_tab.mastering_preview.figure.add_subplot(111)
                ax.plot(time_axis, audio_slice)
                ax.set_title("音频波形预览")
                ax.set_xlabel("时间 (秒)")
                ax.set_ylabel("幅度")
                self.mastering_tab.mastering_preview.canvas.draw()
            
            QMessageBox.information(self, "成功", "音频已重置！")
        else:
            QMessageBox.warning(self, "警告", "没有加载任何音频文件！")
    
    def toggle_global_comparison(self, state):
        """切换全局对比显示"""
        self.pitch_tab.show_comparison_checkbox.setChecked(state)
        self.eq_tab.eq_show_comparison_checkbox.setChecked(state)
        self.mastering_tab.master_show_comparison_checkbox.setChecked(state)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()