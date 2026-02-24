"""
AI音乐后期工程师 - 音乐修音软件启动脚本
"""

import sys
import os
import warnings

# 忽略特定的Qt布局警告
warnings.filterwarnings("ignore", ".*Cannot add a null widget.*")

def main():
    """启动主应用程序"""
    try:
        # 导入并运行主应用
        from main import main as app_main
        print("正在启动 AI音乐后期工程师 - 音乐修音软件...")
        print("请在弹出的窗口中使用以下功能：")
        print("- 音准调校：调整音频音高")
        print("- EQ调节：均衡器控制")
        print("- 录音工程：多轨录音和编辑")
        print("- 母带制作：专业音频处理")
        print("\n加载中，请稍候...")
        
        app_main()
        
    except ImportError as e:
        print(f"导入错误: {e}")
        print("请确保已安装所有依赖包: pip install -r requirements.txt")
        input("按回车键退出...")
    except Exception as e:
        print(f"应用程序错误: {e}")
        import traceback
        traceback.print_exc()
        input("按回车键退出...")

if __name__ == "__main__":
    main()