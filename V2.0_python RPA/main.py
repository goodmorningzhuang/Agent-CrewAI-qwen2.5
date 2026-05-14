import os
import sys

# 导入所有技能
try:
    from skills.text_skill import run_ppt_skill
    from skills.image_skill import cartoonize_image
    from skills.txt_skill import run_txt_skill
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    print("提示：请检查 skills 文件夹内是否有正确的 __init__.py 文件。")
    sys.exit(1)

def main():
    # 基础路径配置
    BASE_PATH = r"C:\Users\user\Desktop\test-ai"
    PPT_DIR = os.path.join(BASE_PATH, "PPT")
    IMG_DIR = os.path.join(BASE_PATH, "image")
    
    while True:
        print("\n" + "="*45)
        print("🤖 硬件BU全能助手 Agent | 全动态文件名版")
        print("="*45)
        print("1. 🚀 优化 PPT 文案 (.pptx)")
        print("2. 📝 优化文本文件 (.txt)")
        print("3. 🎨 图片漫画化处理 (.png/.jpg)")
        print("q. 退出程序")
        print("-" * 45)
        
        choice = input("请输入指令编号: ").strip().lower()

        # --- 1. 处理 PPT ---
        if choice == '1':
            ppt_name = input("\n请输入 PPT 文件夹下的文件名 (如 test.pptx): ").strip()
            # 自动补齐后缀名，防止忘输
            if not ppt_name.endswith(".pptx"):
                ppt_name += ".pptx"
            
            input_path = os.path.join(PPT_DIR, ppt_name)
            if os.path.exists(input_path):
                print(f"⌛ 正在处理 PPT: {ppt_name} ...")
                run_ppt_skill(ppt_name)
            else:
                print(f"❌ 错误：在 /PPT 文件夹下找不到文件 '{ppt_name}'")

        # --- 2. 处理 TXT ---
        elif choice == '2':
            txt_name = input("\n请输入 PPT 文件夹下的文本名 (如 memo.txt): ").strip()
            if not txt_name.endswith(".txt"):
                txt_name += ".txt"
                
            input_path = os.path.join(PPT_DIR, txt_name)
            if os.path.exists(input_path):
                run_txt_skill(txt_name)
            else:
                print(f"❌ 错误：在 /PPT 文件夹下找不到文件 '{txt_name}'")

        # --- 3. 处理图片 ---
        elif choice == '3':
            img_name = input("\n请输入 image 文件夹下的图片名 (如 pic.png): ").strip()
            input_path = os.path.join(IMG_DIR, img_name)
            output_path = os.path.join(IMG_DIR, f"cartoon_{img_name}")

            if os.path.exists(input_path):
                print(f"🎨 正在处理图片...")
                if cartoonize_image(input_path, output_path):
                    print(f"✨ 处理成功！保存至: {output_path}")
                else:
                    print("❌ 处理失败。")
            else:
                print(f"❌ 错误：在 /image 文件夹下找不到文件 '{img_name}'")

        elif choice == 'q':
            print("👋 辛苦了，Agent 正在退出...")
            break
        
        else:
            print("⚠️ 无效输入，请输入 1, 2, 3 或 q。")

if __name__ == "__main__":
    main()