import numpy as np
import cv2

# 이미지 파일 읽기
img = cv2.imread("my_input.jpg")

# 창 크기 조절이 가능한 윈도우 생성
cv2.namedWindow("image", cv2.WINDOW_NORMAL)

# 이미지의 차원 정보 출력 (높이, 너비, 채널)
print(img.shape)

# 화면에 이미지 표시
cv2.imshow("image", img)

# 키 입력을 대기하고 입력받은 키의 ASCII 값을 가져옴 (64비트 환경 호환용 & 0xFF 적용)
key = cv2.waitKey(0) & 0xFF

# 소문자 's' (ASCII 값: ord('s')) 키가 입력된 경우에만 저장
if key == ord('s'):
    cv2.imwrite("out.png", img)
    print("이미지가 'out.png'로 저장되었습니다.")
else:
    print("저장하지 않고 종료합니다.")

# 모든 윈도우 창 닫기
cv2.destroyAllWindows()