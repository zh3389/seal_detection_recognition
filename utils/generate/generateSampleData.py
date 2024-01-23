import os
import random
import uuid
from PIL import Image


def overlay_images(background_path, stamp_path, output_path):
    # 打开背景图和印章图
    background = Image.open(background_path)
    stamp = Image.open(stamp_path)

    # 随机选择印章位置
    bg_width, bg_height = background.size
    stamp_width, stamp_height = stamp.size
    min_width = 50
    max_height = 150
    divisor = None
    for i in range(100):
        if i == 0:
            continue
        if stamp_width // i > min_width and stamp_height // i < max_height:
            divisor = i
            break
    stamp = stamp.resize((stamp_width//divisor, stamp_height//divisor))
    stamp_width, stamp_height = stamp_width//divisor, stamp_height//divisor
    print((stamp_width * stamp_height) / (bg_width / bg_height))

    x_position = random.randint(0, bg_width - stamp_width)
    y_position = random.randint(0, bg_height - stamp_height)

    # 将印章图叠加到背景图上
    background.paste(stamp, (x_position, y_position), stamp)

    # 保存输出图像
    background.save(output_path)


def process_images(folder_A, folder_B, output_folder):
    # 确保输出文件夹存在
    os.makedirs(output_folder, exist_ok=True)

    # 获取A文件夹和B文件夹内的所有图像文件路径
    background_images = [os.path.join(folder_A, file) for file in os.listdir(folder_A) if
                         file.endswith(('.jpg', '.png'))]
    stamp_images = [os.path.join(folder_B, file) for file in os.listdir(folder_B) if file.endswith('.png')]

    # 对每个背景图应用印章
    for background_path in background_images:
        # 从B文件夹中随机选择一个印章图
        stamp_path = random.choice(stamp_images)

        # 构建输出文件路径
        output_filename = os.path.basename(background_path)
        output_path = os.path.join(output_folder, f"{uuid.uuid4()}{output_filename}")
        try:
            # 叠加图像并保存
            overlay_images(background_path, stamp_path, output_path)
        except Exception as e:
            # print(f"Error processing {background_path}: {e}")
            pass


# 使用示例
folder_A = './generate_doc_img'
folder_B = './generate_seal_img'
output_folder = './generateData'
process_images(folder_A, folder_B, output_folder)
