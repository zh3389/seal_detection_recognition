# -*-coding:utf-8-*-
import cv2
import time
import base64
import uvicorn
import numpy as np
from PIL import Image
from io import BytesIO
from utils.SealDetect import SealDetector
from fastapi import FastAPI, Form, UploadFile
from rapidocr_onnxruntime import RapidOCR, VisRes

app = FastAPI()
ppocr = RapidOCR()


@app.post("/specialFormatFileRecognize/identificationOfIrregularSeals")
async def upload_image(imgFile: UploadFile = Form(...), fileHash: str = Form(default="")):
    buffer = BytesIO()
    try:
        contents = await imgFile.read()  # 接收图片
        if contents is None:  # 检查图像数据是否为None
            raise ValueError("传入的图片为空！")
        np_array = np.frombuffer(contents, np.uint8)  # 将二进制数据转换为 numpy 数组
        image_array = cv2.imdecode(np_array, cv2.IMREAD_COLOR)  # 使用 OpenCV 读取图片
        if image_array is None:  # 确认图片是否成功读取
            raise ValueError("图片读取失败！")

        img_list = SealDetector(image_array).crop_img()
        return_list = []
        for seal_array, obj_type, perimeter, area in img_list:
            text_li = []
            seal_array = SealDetector.clean_seal(seal_array)
            result, elapse_list = ppocr(seal_array)
            if result == None or elapse_list == None:
                continue
            for item in result:
                text_li.append(item[1])
            result_text = "%%".join(text_li)
            image = Image.fromarray(seal_array.astype('uint8'))
            image.save(buffer, format="PNG")
            base64_image = base64.b64encode(buffer.getvalue()).decode('utf-8')
            return_list.append({"content": result_text, "context": result_text, "image": base64_image})

        return {"success": True,
                "code": 200,
                "msg": "Image uploaded and OCR performed successfully",
                "data": {"YZ": return_list}}
    except Exception as e:
        return {"success": False,
                "code": 500,
                "msg": str(e),
                "data": None}


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0",  port=8760)
