import os

# 定义目录路径
directory_path = r"C:\Users\wangfan\Desktop\车轮、气密性图片\整车声密性图片存放"

# 检查目录是否存在
if os.path.exists(directory_path):
    # 获取目录下所有文件
    files = os.listdir(directory_path)

    # 定义常见图片格式
    image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.ico')

    # 筛选出图片文件
    image_files = [f for f in files if f.lower().endswith(image_extensions)]

    # 打印图片文件名
    print(f"找到 {len(image_files)} 个图片文件：\n")
    for idx, image_file in enumerate(image_files, 1):
        print(f"{idx}. {image_file}")

    # 如果没有找到图片文件
    if not image_files:
        print("该目录下没有找到图片文件")
        print("\n目录下所有文件：")
        for f in files:
            print(f"  - {f}")
else:
    print(f"错误：目录不存在 - {directory_path}")

