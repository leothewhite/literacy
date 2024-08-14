import numpy as np
import platform
from PIL import ImageFont, ImageDraw, Image
from matplotlib import pyplot as plt
 
import uuid
import json
import time
import cv2
import requests


# 이미지를 창에 띄워줌 (시제품에는 사용되지 않음)
def plt_imshow(title='image', img=None, figsize=(8 ,5)):
    plt.figure(figsize=figsize)
 
    if type(img) == list:
        if type(title) == list:
            titles = title
        else:
            titles = []
 
            for i in range(len(img)):
                titles.append(title)
 
        for i in range(len(img)):
            if len(img[i].shape) <= 2:
                rgbImg = cv2.cvtColor(img[i], cv2.COLOR_GRAY2RGB)
            else:
                rgbImg = cv2.cvtColor(img[i], cv2.COLOR_BGR2RGB)
 
            plt.subplot(1, len(img), i + 1), plt.imshow(rgbImg)
            plt.title(titles[i])
            plt.xticks([]), plt.yticks([])
 
        plt.show()
    else:
        if len(img.shape) < 3:
            rgbImg = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        else:
            rgbImg = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
 
        plt.imshow(rgbImg)
        plt.title(title)
        plt.xticks([]), plt.yticks([])
        plt.show()


# 이미지에 텍스트를 넣음 (시제품에 사용되지 않음)
def put_text(image, text, x, y, color=(0, 255, 0), font_size=22):
    if type(image) == np.ndarray:
        color_coverted = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(color_coverted)
 
    if platform.system() == 'Darwin':
        font = 'AppleGothic.ttf'
    elif platform.system() == 'Windows':
        font = 'malgun.ttf'
        
    image_font = ImageFont.truetype(font, font_size)
    font = ImageFont.load_default()
    draw = ImageDraw.Draw(image)
 
    draw.text((x, y), text, font=image_font, fill=color)
    
    numpy_image = np.array(image)
    opencv_image = cv2.cvtColor(numpy_image, cv2.COLOR_RGB2BGR)
 
    return opencv_image


# api key를 외부 파일에서 읽어옴(보안상의 이유로 분리)
key_file = open('./keys/ocr_api_key.txt', 'r')
secret_key = key_file.read()

# request를 보낼 ocr api url
api_url = 'https://8hiktk5tv5.apigw.ntruss.com/custom/v1/33325/5c41bfa54bca338e50b0223ee042f32d6f43570af778c53d13991477b0784015/general'

# 원본 파일(테스트 위해 Untitled.jpg 사용)
path = './Untitled.jpg'
files = [('file', open(path,'rb'))]

# ocr api에 보낼 request 설정
request_json = {'images': [{'format': 'jpg',
                                'name': 'demo'
                               }],
                    'requestId': str(uuid.uuid4()),
                    'version': 'V2',
                    'timestamp': int(round(time.time() * 1000))
                   }


payload = {'message': json.dumps(request_json).encode('UTF-8')}
 
headers = {
  'X-OCR-SECRET': secret_key,
}

# ocr api에 request 보냄
response = requests.request("POST", api_url, headers=headers, data=payload, files=files)
result = response.json()

# 텍스트 추출 결과를 표시할 사본 복사
img = cv2.imread(path)
roi_img = img.copy()
 
f = open('./res.txt', 'w')

content = ''

for field in result['images'][0]['fields']:
    # 사진에 네모 박스 치기
    text = field['inferText']
    vertices_list = field['boundingPoly']['vertices']
    pts = [tuple(vertice.values()) for vertice in vertices_list]
    topLeft = [int(_) for _ in pts[0]]
    topRight = [int(_) for _ in pts[1]]
    bottomRight = [int(_) for _ in pts[2]]
    bottomLeft = [int(_) for _ in pts[3]]
 
    cv2.line(roi_img, topLeft, topRight, (0,255,0), 2)
    cv2.line(roi_img, topRight, bottomRight, (0,255,0), 2)
    cv2.line(roi_img, bottomRight, bottomLeft, (0,255,0), 2)
    cv2.line(roi_img, bottomLeft, topLeft, (0,255,0), 2)
    roi_img = put_text(roi_img, text, topLeft[0], topLeft[1] - 20, font_size=30)
    
    f.write(text+' ')
    content += f'{text} '

f.close()

print(content)

# 창을 띄워 원본 이미지와 네모박스+추출결과 넣은 이미지 표시
plt_imshow(["Original", "ROI"], [img, roi_img], figsize=(16, 10))
