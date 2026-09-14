# import numpy as np
# import cv2

# color = cv2.imread("strawberry.jpg", cv2.IMREAD_COLOR)
# print(color.shape)

# height,width,channels = color.shape
# cv2.imshow("Original Image",color)

# b,g,r = cv2. split(color)
# rgb_split=np.concatenate((b,g,r),axis=1)
# cv2.imshow("BGR Channels", rgb_split)

# hsv= cv2.cvtColor(color, cv2.COLOR_BGR2HSV)

# h,s,v = cv2.split(hsv)
# hsv_split = np.concatenate((h,s,v),axis=1)
# cv2.imshow("Split HSV", hsv_split)


################################################################################################################


# QUIZ

# 1. 위 색공간 이미의 링크로 이동해서 각 색 공간의 표현 방법을 이해해보자.
# BGR: OpenCV의 기본 색 공간으로, 각 화소(Pixel)를 Blue, Green, Red 3가지 색상 채널의 조합(0~255)으로 표현합니다.

# 2. HSV color space 가 어떤 경우에 효과적으로 사용될까?
# 특정 색상 영역 추출 및 검출: 조명의 변화(명도 $V$)나 색의 옅고 짙음(채도 $S$)과 무관하게, 순수한 색상($H$)
# 범위만으로 물체를 지정할 수 있어 특정 색상의 물체 추적(예: 빨간 딸기, 조향선 탐지)에 매우 효과적입니다.

# 조명에 강인한 이미지 처리: BGR에서는 조명이 밝아지거나 어두워지면 B, G, R 값이 모두 변하지만, HSV에서는 명도($V$)
# 채널만 변하므로 $H$와 $S$ 값을 유지하여 조명 영향에 잘 견딥니다.

# 3. HSV 로 변환된 이미지를 BGR 이 아닌 RGB 로 다시 변환해서 출력해 보자.

# 4. COLOR_RBG2GRAY를 사용해서 흑백으로 변환해 출력해보자


import cv2
import numpy as np

# 1. 원본 이미지 로드 (BGR)
color = cv2.imread("strawberry.jpg", cv2.IMREAD_COLOR)

if color is None:
    print("이미지를 불러올 수 없습니다. 경로를 확인해 주세요.")
else:
    print("Image Shape:", color.shape)
    height, width, channels = color.shape
    cv2.imshow("Original Image (BGR)", color)

    # BGR 채널 분리 및 출력
    b, g, r = cv2.split(color)
    rgb_split = np.concatenate((b, g, r), axis=1)
    cv2.imshow("BGR Channels", rgb_split)

    # 2. BGR -> HSV 변환 및 채널 분리
    hsv = cv2.cvtColor(color, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    hsv_split = np.concatenate((h, s, v), axis=1)
    cv2.imshow("Split HSV", hsv_split)

    # 3. HSV -> RGB 로 변환 후 출력
    # (참고: imshow는 BGR로 해석하므로 RGB 이미지 출력 시 R/B 채널이 반전되어 보입니다)
    rgb_image = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
    cv2.imshow("HSV to RGB Image", rgb_image)

    # 4. COLOR_BGR2GRAY를 사용해서 흑백(Gray)으로 변환 후 출력
    gray_image = cv2.cvtColor(color, cv2.COLOR_BGR2GRAY)
    cv2.imshow("Gray Image", gray_image)

    # 키 입력 대기 후 모든 창 닫기
    cv2.waitKey(0)
    cv2.destroyAllWindows()