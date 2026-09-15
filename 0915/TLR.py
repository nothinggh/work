# import cv2

# cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

# topLeft = (50,50)
# bottomRight = (300, 300)

# while(cap.isOpened()):
#     ret, frame = cap.read()

#     cv2.line(frame, topLeft, bottomRight, (0, 255, 0), 5)

#     cv2.rectangle(frame,[pt+30 for pt in topLeft],[pt-30 for pt in bottomRight], (0, 0, 255), 5)

#     font = cv2.FONT_HERSHEY_SIMPLEX
#     cv2.putText(frame, 'me',[pt+80 for pt in topLeft], font, 2, (0, 255, 255), 10)

#     cv2.imshow("Camera", frame)


#################################################################################################################


# Text 문구, Font, 색상, 크기, 굵기, 출력 위치 등 모든 값을 변경해 보기
# 동그라미를 그리는 함수를 찾아서 적용해 보기
# 마우스 왼쪽 버튼을 click 하면 해당 위치에 동그라미가 그려지도록 코드를 추가해 보기(Reference:cv2.EVENT_LBUTTONDOWN) 

import cv2
import os

# 클릭한 마우스 위치를 저장할 리스트
circles = []

# 마우스 이벤트 콜백 함수 정의
def draw_circle(event, x, y, flags, param):
    global circles
    # 마우스 왼쪽 버튼을 눌렀을 때
    if event == cv2.EVENT_LBUTTONDOWN:
        # 클릭한 위치 좌표(x, y)를 리스트에 추가
        circles.append((x, y))
        print(f"🖱️ 마우스 클릭 위치 추가: ({x}, {y})")

def get_video_source():
    # 0번~3번 인덱스 중 연결된 카메라 찾기
    for idx in range(4):
        cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None:
                print(f"✅ 웹캠 연결 성공 (인덱스: {idx})")
                return cap
            cap.release()

    # 웹캠이 없을 경우 파일 재생
    video_path = 'output.mp4'
    if os.path.exists(video_path):
        print(f"⚠️ 카메라가 없습니다. '{video_path}' 동영상으로 대체합니다.")
        return cv2.VideoCapture(video_path)

    return None

cap = get_video_source()

if cap is None or not cap.isOpened():
    print("❌ 사용 가능한 카메라 또는 동영상을 찾을 수 없습니다.")
    exit()

# 윈도우 창을 먼저 생성해야 마우스 콜백을 연결할 수 있습니다.
win_name = "Camera View"
cv2.namedWindow(win_name)
cv2.setMouseCallback(win_name, draw_circle)

topLeft = (50, 50)
bottomRight = (300, 300)

print("🎥 카메라 화면 실행 중... (화면을 마우스 클릭하면 원이 그려집니다 / 'c': 초기화, 'q': 종료)")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret or frame is None:
        print("프레임을 가져올 수 없어 종료합니다.")
        break

    # 1. 초록색 대각선 (BGR: 0, 255, 0)
    cv2.line(frame, topLeft, bottomRight, (0, 255, 0), 5)

    # 2. 빨간색 사각형 (BGR: 0, 0, 255)
    rect_top_left = tuple(pt + 30 for pt in topLeft)
    rect_bottom_right = tuple(pt - 30 for pt in bottomRight)
    cv2.rectangle(frame, rect_top_left, rect_bottom_right, (0, 0, 255), 5)

    # 3. 기본 동그라미(원) 예시
    cv2.circle(frame, (175, 175), 60, (255, 0, 255), 4, cv2.LINE_AA)
    cv2.circle(frame, (400, 150), 30, (0, 255, 128), -1, cv2.LINE_AA)

    # -------------------------------------------------------------
    # 4. 마우스 클릭한 모든 위치에 동그라미 그리기 추가
    # -------------------------------------------------------------
    for center in circles:
        # 클릭한 좌표 중심에 주황색 채워진 원 그리기
        cv2.circle(frame, center, 15, (0, 165, 255), -1, cv2.LINE_AA)

    # 5. 텍스트 그리기
    cv2.putText(
        frame, 
        "Click anywhere to draw circles!", 
        (50, 380), 
        cv2.FONT_HERSHEY_DUPLEX, 
        0.8, 
        (255, 255, 0), 
        2, 
        cv2.LINE_AA
    )

    # 6. 실시간 화면 출력
    cv2.imshow(win_name, frame)

    key = cv2.waitKey(1) & 0xFF
    # 'q' 키를 누르면 화면 창 종료
    if key == ord('q'):
        break
    # 'c' 키를 누르면 그려진 원 모두 지우기
    elif key == ord('c'):
        circles.clear()
        print("🧹 그렸던 원 목록 초기화 완료")

cap.release()
cv2.destroyAllWindows()