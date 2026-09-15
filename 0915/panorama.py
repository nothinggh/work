import cv2
import numpy as np
import pyrealsense2 as rs
import os
import time

SAVE_DIR = r"D:\prj\work"
SAVE_FILE = os.path.join(SAVE_DIR, "panorama.jpg")

os.makedirs(SAVE_DIR, exist_ok=True)

pipeline = rs.pipeline()
config = rs.config()

config.enable_stream(
    rs.stream.color,
    1280,
    720,
    rs.format.bgr8,
    30
)

pipeline.start(config)

print("RealSense 카메라 시작")
print()
print("촬영 방법")
print("1. 카메라를 왼쪽에서 시작하세요.")
print("2. 화면의 물체가 충분히 겹치도록 천천히 오른쪽으로 이동하세요.")
print("3. SPACE : 촬영 시작")
print("4. S     : 촬영 종료 및 파노라마 생성")
print("5. ESC   : 종료")
print()

frames = []
recording = False
last_capture = 0

try:
    while True:

        frameset = pipeline.wait_for_frames()
        color_frame = frameset.get_color_frame()

        if not color_frame:
            continue

        frame = np.asanyarray(color_frame.get_data())

        display = frame.copy()

        if recording:
            cv2.putText(
                display,
                f"RECORDING  Frames: {len(frames)}",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 0, 255),
                2
            )

            current_time = time.time()

            if current_time - last_capture >= 0.15:
                frames.append(frame.copy())
                last_capture = current_time

        else:
            cv2.putText(
                display,
                "SPACE: START",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2
            )

        cv2.imshow("RealSense Panorama", display)

        key = cv2.waitKey(1) & 0xFF

        if key == 27:
            break

        elif key == 32:
            if not recording:
                frames = []
                recording = True
                last_capture = time.time()
                print("촬영 시작")

        elif key == ord('s'):
            if recording:
                recording = False
                print(f"촬영 종료 - {len(frames)}개 프레임")

                if len(frames) < 5:
                    print("프레임이 너무 적습니다.")
                    continue

                print("파노라마 생성 중...")

                stitcher = cv2.Stitcher_create(
                    cv2.Stitcher_PANORAMA
                )

                status, panorama = stitcher.stitch(frames)

                if status == cv2.Stitcher_OK:

                    cv2.imwrite(
                        SAVE_FILE,
                        panorama
                    )

                    print()
                    print("파노라마 생성 성공!")
                    print(f"저장 위치: {SAVE_FILE}")
                    print(f"크기: {panorama.shape[1]} x {panorama.shape[0]}")
                    print()

                    cv2.imshow(
                        "PANORAMA RESULT",
                        panorama
                    )

                else:
                    print()
                    print("파노라마 생성 실패")
                    print(f"OpenCV Stitcher 오류 코드: {status}")
                    print("카메라를 더 천천히 움직이고")
                    print("촬영 화면이 서로 충분히 겹치도록 해주세요.")

except Exception as e:
    print("오류 발생:")
    print(e)

finally:
    pipeline.stop()
    cv2.destroyAllWindows()