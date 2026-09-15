# import cv2

# topLeft = (50, 50)
# bold = 0

# cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)


# def on_bold_trackbar(value):
#     global bold
#     bold = value


# cv2.namedWindow("Camera")
# cv2.createTrackbar("bold", "Camera", bold, 10, on_bold_trackbar)

# while cap.isOpened():
#     ret, frame = cap.read()
#     if ret is False:
#         print("Can't receive frame(stream end?). Exiting ...")
#         break

#     cv2.putText(frame, "TEXT", topLeft,
#                 cv2.FONT_HERSHEY_SIMPLEX, 2,
#                 (0, 255, 255), 1 + bold)

#     cv2.imshow("Camera", frame)
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# cap.release()
# cv2.destroyAllWindows()


#########################################################################


# Trackbar 를 control 해서 TEXT 의 굵기가 변하는 것을 확인해 보자.
# Trackbar 를 추가해서 font size를 변경, 적용해 보자.
# RGB Trackbar를 각각 추가해서 글자의 font color를 변경해 보자.

import cv2

topLeft = (50, 50)
bold = 0
font_scale_int = 10

r_val = 0
g_val = 255
b_val = 255


def on_bold_trackbar(value):
    global bold
    bold = value


def on_scale_trackbar(value):
    global font_scale_int
    font_scale_int = value


def on_r_trackbar(value):
    global r_val
    r_val = value


def on_g_trackbar(value):
    global g_val
    g_val = value


def on_b_trackbar(value):
    global b_val
    b_val = value


# 카메라 연결
cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)

# --- [카메라 프레임 크기 변경 설정] ---
# 원하는 너비(Width)와 높이(Height)를 설정합니다. (예: 1280x720)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
# --------------------------------------

cv2.namedWindow("Camera")

cv2.createTrackbar("bold", "Camera", bold, 10, on_bold_trackbar)
cv2.createTrackbar("scale", "Camera", font_scale_int, 50, on_scale_trackbar)
cv2.createTrackbar("R", "Camera", r_val, 255, on_r_trackbar)
cv2.createTrackbar("G", "Camera", g_val, 255, on_g_trackbar)
cv2.createTrackbar("B", "Camera", b_val, 255, on_b_trackbar)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Can't receive frame(stream end?). Exiting ...")
        break

    actual_scale = max(1, font_scale_int) / 10.0
    text_color = (b_val, g_val, r_val)

    cv2.putText(
        frame,
        "TEXT",
        topLeft,
        cv2.FONT_HERSHEY_SIMPLEX,
        actual_scale,
        text_color,
        1 + bold,
    )

    cv2.imshow("Camera", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()