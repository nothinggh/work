# import numpy as np
# import cv2

# cap = cv2.VideoCapture("ronaldinho.mp4")

# while(cap.isOpened()):
#     ret, frame = cap.read()

#     if ret is False:
#         print("Can't receive frame (stream end?). Exiting...")
#         break
#     cv2.imshow("Frame", frame)

#     key = cv2.waitKey(1)
#     if key & 0xFF == ord('q'):
#         break
#     cap.release()
#     cv2.destroyAllWindows()


# 정상적인 재생속도로 수정하기
# 동영상이 끝까지 재생되면 다시 처음부터 반복 될 수 있도록 수정해 보기
# 동영상 크기를 반으로 resize 해서 출력해 보기
# 동영상 재생 중 'c'키 입력을 받으면 해당 프레임을 이미지 파일로 저장하게 코드를 수정해 보기.
# 파일 이름은 001.jpg, 002.jpg 등으로 overwrite 되지 않게 하자.

import os
import cv2

cap = cv2.VideoCapture("nonaldinho.mp4")

# 원본 비디오의 FPS(초당 프레임 수) 가져오기
fps = cap.get(cv2.CAP_PROP_FPS)

# FPS 기반 프레임당 대기 시간(ms) 계산 (FPS가 0 이하일 경우 예외 처리)
delay = int(1000 / fps) if fps > 0 else 30

# 저장될 이미지 파일 이름을 구분하기 위한 번호
save_count = 1

# 비디오가 끝나면 다시 처음 프레임부터 재생
while True:
    ret, frame = cap.read()

    if not ret:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        ret, frame = cap.read()
        if not ret:
            break

    # 영상 크기를 반으로 resize 해서 출력
    resized_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
    cv2.imshow("Resized Frame", resized_frame)

    # 계산된 delay 시간만큼 대기
    key = cv2.waitKey(delay) & 0xFF

    # 'c' 키 입력 시 현재 프레임 이미지를 저장
    if key == ord('c'):
        # 001.jpg, 002.jpg 형태로 저장되고, 이미 존재하는 파일 이름은 건너뛰어 overwrite 방지
        save_name = f"{save_count:03d}.jpg"
        while os.path.exists(save_name):
            save_count += 1
            save_name = f"{save_count:03d}.jpg"

        success = cv2.imwrite(save_name, frame)
        if success:
            print(f"Saved {save_name}")
        else:
            print(f"Failed to save {save_name}")

        save_count += 1

    # 'q' 키 입력 시 종료
    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()