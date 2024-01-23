import cv2
from rapidocr_onnxruntime import RapidOCR, VisRes

engine = RapidOCR()
vis = VisRes()

img_path = "../assets/1.jpg"
font_path = '../assets/FZYTK.TTF'

# 默认都为True
result, elapse = engine(img_path, use_det=True, use_cls=True, use_rec=True)
print(result)

boxes, txts, scores = list(zip(*result))
res = vis(cv2.imread(img_path), boxes, txts, scores, font_path=font_path)
cv2.imshow("img", res)
cv2.waitKey(0)
