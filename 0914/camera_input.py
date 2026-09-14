import numpy as np
import cv2

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

w = 1280  # 1920
h = 720   # 1080
fps = 30.0

cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('output.mp4', fourcc, fps, (w, h))

while cap.isOpened():
    ret, frame = cap.read()
    if ret is False:
        print("Can't receive frame (stream end?). Exiting...")
        break

    out.write(frame)
    cv2.imshow("Camera", frame)

    key = cv2.waitKey(1)
    if key & 0xFF == ord('q'):
        break

cap.release()
out.release()
cv2.destroyAllWindows()

