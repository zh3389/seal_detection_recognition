from rapidocr_onnxruntime import RapidOCR

engine = RapidOCR()

img_path = '/app/assets/1.png'

# 默认都为True
result, elapse = engine(img_path, use_det=True, use_cls=True, use_rec=True)
print(result)
