# import numpy as np
# import cv2

# img = cv2.imread("my_input.jpg")

# cropped = img[50:450, 100:400]

# resized = cv2.resize(cropped, (400, 200))

# cv2.imshow("Original", img)
# cv2.imshow("Cropped image", cropped)
# cv2.imshow("Resized image", resized)

# cv2.waitKey(0)
# cv2.destroyAllWindows()


####################################################################


import cv2
import numpy as np

# 이미지 로드
img_path = "my_input.jpg"
img = cv2.imread(img_path)

# 이미지 로드 확인
if img is None:
    print(f"Error: 이미지를 불러올 수 없습니다. '{img_path}' 경로를 확인해주세요.")
else:
    # 1. input image 의 size 확인해보기
    # img.shape는 (높이, 너비, 채널) 튜플을 반환합니다.
    height, width, channels = img.shape
    print(f"[1] 원본 이미지 크기: 너비 {width}px, 높이 {height}px (채널: {channels})")

    # 2. 이미지의 얼굴 영역만 crop해서 display 해보기
    # 슬라이싱 형태: img[y_start:y_end, x_start:x_end]
    # NOTE: 사용하시는 이미지의 얼굴 위치에 맞게 좌표 범위를 조정해주세요.
    face_cropped = img[400:450, 100:400]
    cv2.imshow("2. Cropped Face", face_cropped)

    # 3. 원본 이미지의 정확히 1.5배만큼 확대해서 파일로 저장해보기
    # dsize=(0, 0)으로 설정하고 fx, fy 비율 인자를 사용하여 정확히 1.5배 확대합니다.
    resized_1_5x = cv2.resize(img, (0, 0), fx=1.5, fy=1.5, interpolation=cv2.INTER_LINEAR)
    cv2.imwrite("resized_1_5x.jpg", resized_1_5x)
    print(f"[3] 1.5배 확대 이미지 저장 완료 ('resized_1_5x.jpg') - 새로운 크기: {resized_1_5x.shape[1]}x{resized_1_5x.shape[0]}")

    # 4. openCV 의 rotate API 를 사용해서 우측으로 90도만큼 회전된 이미지를 출력해보기
    # 시계 방향(우측) 90도 회전에는 cv2.ROTATE_90_CLOCKWISE 플래그를 사용합니다.
    rotated_90_cw = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
    cv2.imshow("4. Rotated 90 Deg Clockwise", rotated_90_cw)

    # 원본 이미지 출력 및 대기 처리
    cv2.imshow("Original Image", img)
    
    cv2.waitKey(0)
    cv2.destroyAllWindows()
