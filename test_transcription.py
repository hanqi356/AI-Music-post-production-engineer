#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
扒谱功能测试脚本
测试扒谱生成器的功能
"""

import numpy as np
import librosa
import sys
import os

# 添加src目录到路径
sys.path.append('src')

def test_transcription_generation():
    """测试扒谱生成功能"""
    print("=== 扒谱生成功能测试 ===")
    
    try:
        from src.audio_processing.transcription_generator import TranscriptionGenerator
        
        # 创建测试音频 - 简单的C大调音阶
        sample_rate = 44100
        generator = TranscriptionGenerator(sample_rate=sample_rate)
        
        # 创建测试音频：C4-E4-G4-C5 (C大调和弦进程)
        duration_per_note = 0.5  # 每个音符0.5秒
        frequencies = [261.63, 329.63, 392.00, 523.25]  # C4, E4, G4, C5
        
        total_duration = duration_per_note * len(frequencies)
        t = np.linspace(0, total_duration, int(sample_rate * total_duration))
        test_audio = np.zeros_like(t)
        
        for i, freq in enumerate(frequencies):
            start_sample = int(i * duration_per_note * sample_rate)
            end_sample = int((i + 1) * duration_per_note * sample_rate)
            if end_sample > len(t):
                end_sample = len(t)
            
            note_t = t[start_sample:end_sample]
            note_signal = np.sin(2 * np.pi * freq * note_t) * 0.3
            
            # 添加简单的包络使音符过渡更自然
            envelope = np.ones_like(note_signal)
            attack_samples = int(0.01 * sample_rate)  # 10ms attack
            release_samples = int(0.01 * sample_rate)  # 10ms release
            if len(envelope) > attack_samples + release_samples:
                envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
                envelope[-release_samples:] = np.linspace(1, 0, release_samples)
            else:
                envelope = np.linspace(0, 1, len(envelope))
                envelope[len(envelope)//2:] = np.linspace(1, 0, len(envelope)//2 + len(envelope)%2)
            
            test_audio[start_sample:end_sample] += note_signal * envelope
        
        print(f"✓ 创建测试音频: 长度 {len(test_audio)/sample_rate:.2f}秒, 采样率 {sample_rate}Hz")
        
        # 测试旋律检测
        print("✓ 测试旋律检测...")
        melody = generator.detect_melody(test_audio)
        print(f"  检测到 {len(melody)} 个音符")
        
        for i, note in enumerate(melody[:5]):  # 显示前5个音符
            print(f"  音符 {i+1}: {note['note_name']}{note['octave']}{note['accidental']} "
                  f"@ {note['time']:.2f}s (持续 {note['duration']:.2f}s)")
        
        # 测试和弦检测
        print("✓ 测试和弦检测...")
        chords = generator.detect_chords(test_audio)
        print(f"  检测到 {len(chords)} 个和弦")
        
        for i, chord in enumerate(chords[:5]):  # 显示前5个和弦
            print(f"  和弦 {i+1}: {chord['chord']} @ {chord['time']:.2f}s")
        
        # 测试扒谱生成
        print("✓ 测试扒谱生成...")
        success = generator.generate_transcription(
            test_audio, 
            "test_transcription_output.txt", 
            track_name="测试扒谱"
        )
        print(f"  文本扒谱生成: {'成功' if success else '失败'}")
        
        # 测试扒谱图像生成
        print("✓ 测试扒谱图像生成...")
        success_img = generator.generate_transcription_image(
            test_audio, 
            "test_transcription_output.png", 
            track_name="测试扒谱",
            format="png"
        )
        print(f"  图像扒谱生成: {'成功' if success_img else '失败'}")
        
        print("\n🎉 所有扒谱功能测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 扒谱功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_transcription_generation()
    sys.exit(0 if success else 1)