from datetime import datetime
import os
import sqlite3

import cv2
import numpy as np


# ============================================================
# 기본 경로
# ============================================================

BASE_DIR = r"D:\prj\work"

SAVE_PASS_DIR = os.path.join(
    BASE_DIR,
    "dataset",
    "pass"
)

SAVE_NG_DIR = os.path.join(
    BASE_DIR,
    "dataset",
    "ng"
)

DB_PATH = os.path.join(
    BASE_DIR,
    "sensor_data.db"
)

os.makedirs(
    SAVE_PASS_DIR,
    exist_ok=True
)

os.makedirs(
    SAVE_NG_DIR,
    exist_ok=True
)


# ============================================================
# SQLite DB
# ============================================================

class SensorDatabase:

    def __init__(self, db_path):

        self.db_path = db_path

        self.conn = sqlite3.connect(
            self.db_path,
            check_same_thread=False
        )

        self.cursor = self.conn.cursor()

        self.init_table()


    def init_table(self):

        query = """
        CREATE TABLE IF NOT EXISTS sensor_logs (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            timestamp TEXT NOT NULL,

            item_count INTEGER NOT NULL,

            size_width_mm REAL,

            size_height_mm REAL,

            camera_type TEXT,

            status TEXT,

            image_path TEXT

        )
        """

        self.cursor.execute(query)

        self.conn.commit()


    def save_result(
        self,
        item_count,
        width_mm,
        height_mm,
        camera_type,
        status,
        image_path
    ):

        timestamp = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        query = """
        INSERT INTO sensor_logs
        (
            timestamp,
            item_count,
            size_width_mm,
            size_height_mm,
            camera_type,
            status,
            image_path
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """

        self.cursor.execute(
            query,
            (
                timestamp,
                item_count,
                width_mm,
                height_mm,
                camera_type,
                status,
                image_path
            )
        )

        self.conn.commit()

        return self.cursor.lastrowid


    def close(self):

        self.conn.close()


# ============================================================
# 알약 식별
# ============================================================

def identify_pill(
    contour,
    hsv_crop
):

    area = cv2.contourArea(
        contour
    )

    h = hsv_crop[0]
    s = hsv_crop[1]


    # 비오콜 캡슐
    if (
        30 <= h <= 95
        and s > 30
    ):

        return "비오콜 (캡슐)"


    # 부스포론 0.5정
    if (
        400 <= area < 1600
    ):

        return "부스포론 (0.5정)"


    # 모사렌 M5
    if (
        3600 <= area < 5200
    ):

        return "모사렌 (M5)"


    # 티파드 중원형
    if (
        1800 <= area < 3600
    ):

        return "티파드 (중원형)"


    return "미인식알약"


# ============================================================
# 마우스 이벤트
# ============================================================

btn_clicked = False

click_pos = (
    -1,
    -1
)


def mouse_callback(
    event,
    x,
    y,
    flags,
    param
):

    global btn_clicked
    global click_pos

    if event == cv2.EVENT_LBUTTONDOWN:

        btn_clicked = True

        click_pos = (
            x,
            y
        )


# ============================================================
# DB 생성
# ============================================================

db = SensorDatabase(
    DB_PATH
)


# ============================================================
# 카메라 설정
# ============================================================

CAMERA_INDEX = 1

cap = cv2.VideoCapture(
    CAMERA_INDEX,
    cv2.CAP_DSHOW
)


if not cap.isOpened():

    print()
    print("==========================================")
    print("카메라 연결 실패")
    print("==========================================")
    print(
        f"카메라 인덱스 : {CAMERA_INDEX}"
    )
    print()
    print(
        "CAMERA_INDEX = 0 또는 1 또는 2로 변경해보세요."
    )

    db.close()

    exit()


# ============================================================
# 카메라 해상도
# ============================================================

cap.set(
    cv2.CAP_PROP_FRAME_WIDTH,
    1280
)

cap.set(
    cv2.CAP_PROP_FRAME_HEIGHT,
    720
)


# ============================================================
# OpenCV Window
# ============================================================

window_name = "Pill AOI Inspection System"

cv2.namedWindow(
    window_name,
    cv2.WINDOW_NORMAL
)

cv2.setMouseCallback(
    window_name,
    mouse_callback
)


# ============================================================
# 시작 메시지
# ============================================================

print()
print("==========================================")
print("     Pill AOI Inspection System")
print("==========================================")
print()
print(
    f"DB : {DB_PATH}"
)
print()
print("판정 기준")
print("-----------------------------")
print("0 ~ 3개  : NG")
print("4개 이상 : PASS")
print("미인식   : NG")
print("-----------------------------")
print()
print("PASS / NG 모두 결과 저장 버튼을")
print("클릭하면 이미지와 DB에 저장됩니다.")
print()
print("Q : 프로그램 종료")
print()


# ============================================================
# 메인 루프
# ============================================================

while cap.isOpened():

    ret, frame = cap.read()


    if not ret:

        print(
            "카메라 영상을 읽을 수 없습니다."
        )

        break


    # ========================================================
    # 이미지 크기
    # ========================================================

    h_img, w_img, _ = frame.shape


    # ========================================================
    # 오른쪽 UI 패널
    # ========================================================

    panel_width = 270


    display_frame = np.zeros(
        (
            h_img,
            w_img + panel_width,
            3
        ),
        dtype=np.uint8
    )


    display_frame[
        :,
        :w_img
    ] = frame.copy()


    display_frame[
        :,
        w_img:
    ] = (
        40,
        40,
        40
    )


    # ========================================================
    # ROI
    # ========================================================

    roi_x1 = int(
        w_img * 0.15
    )

    roi_y1 = int(
        h_img * 0.15
    )

    roi_x2 = int(
        w_img * 0.85
    )

    roi_y2 = int(
        h_img * 0.85
    )


    roi_frame = frame[
        roi_y1:roi_y2,
        roi_x1:roi_x2
    ]


    # ========================================================
    # Gray
    # ========================================================

    gray_roi = cv2.cvtColor(
        roi_frame,
        cv2.COLOR_BGR2GRAY
    )


    # ========================================================
    # Blur
    # ========================================================

    blurred_roi = cv2.GaussianBlur(
        gray_roi,
        (
            5,
            5
        ),
        0
    )


    # ========================================================
    # Adaptive Threshold
    # ========================================================

    thresh_roi = cv2.adaptiveThreshold(
        blurred_roi,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        15,
        3
    )


    # ========================================================
    # Morphology
    # ========================================================

    kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE,
        (
            3,
            3
        )
    )


    clean_thresh = cv2.morphologyEx(
        thresh_roi,
        cv2.MORPH_OPEN,
        kernel,
        iterations=1
    )


    clean_thresh = cv2.morphologyEx(
        clean_thresh,
        cv2.MORPH_CLOSE,
        kernel,
        iterations=2
    )


    # ========================================================
    # Contour
    # ========================================================

    contours, _ = cv2.findContours(
        clean_thresh,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )


    # ========================================================
    # 알약 후보
    # ========================================================

    valid_pills = [

        cnt

        for cnt in contours

        if (
            400
            < cv2.contourArea(cnt)
            < 25000
        )

    ]


    pill_cnt = len(
        valid_pills
    )


    # ========================================================
    # HSV
    # ========================================================

    hsv_roi = cv2.cvtColor(
        roi_frame,
        cv2.COLOR_BGR2HSV
    )


    unknown_exist = False

    pill_names = []


    # ========================================================
    # 알약 분석
    # ========================================================

    for cnt in valid_pills:

        x, y, w, h = cv2.boundingRect(
            cnt
        )


        mask = np.zeros(
            gray_roi.shape,
            dtype=np.uint8
        )


        cv2.drawContours(
            mask,
            [cnt],
            -1,
            255,
            -1
        )


        hsv_crop = cv2.mean(
            hsv_roi,
            mask=mask
        )


        pill_name = identify_pill(
            cnt,
            hsv_crop
        )


        pill_names.append(
            pill_name
        )


        abs_x = (
            x + roi_x1
        )

        abs_y = (
            y + roi_y1
        )


        # ====================================================
        # 미인식
        # ====================================================

        if pill_name == "미인식알약":

            box_color = (
                0,
                165,
                255
            )

            unknown_exist = True

        else:

            box_color = (
                0,
                255,
                0
            )


        # ====================================================
        # Bounding Box
        # ====================================================

        cv2.rectangle(
            display_frame,

            (
                abs_x,
                abs_y
            ),

            (
                abs_x + w,
                abs_y + h
            ),

            box_color,

            2
        )


        # ====================================================
        # 이름 표시
        # ====================================================

        text_y = max(
            abs_y - 8,
            25
        )


        cv2.putText(
            display_frame,

            pill_name,

            (
                abs_x,
                text_y
            ),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.55,

            box_color,

            2,

            cv2.LINE_AA
        )


    # ========================================================
    # 판정
    # ========================================================

    # 4개 미만이면 NG
    # 4개 이상이면 PASS
    # 미인식 알약이 있으면 NG

    is_pass = (
        pill_cnt >= 4
        and not unknown_exist
    )


    if is_pass:

        status_text = "PASS"

        status_color = (
            0,
            255,
            0
        )

    else:

        status_text = "NG"

        status_color = (
            0,
            0,
            255
        )


    # ========================================================
    # ROI 표시
    # ========================================================

    cv2.rectangle(
        display_frame,

        (
            roi_x1,
            roi_y1
        ),

        (
            roi_x2,
            roi_y2
        ),

        (
            255,
            255,
            0
        ),

        2
    )


    cv2.putText(
        display_frame,

        "INSPECTION ROI",

        (
            roi_x1,
            max(
                roi_y1 - 10,
                25
            )
        ),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.6,

        (
            255,
            255,
            0
        ),

        2,

        cv2.LINE_AA
    )


    # ========================================================
    # 화면 상단 PASS / NG
    # ========================================================

    cv2.putText(
        display_frame,

        status_text,

        (
            20,
            45
        ),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.9,

        status_color,

        3,

        cv2.LINE_AA
    )


    # ========================================================
    # 검출 개수
    # ========================================================

    cv2.putText(
        display_frame,

        f"Pills : {pill_cnt} ea",

        (
            20,
            82
        ),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.65,

        (
            255,
            255,
            255
        ),

        2,

        cv2.LINE_AA
    )


    # ========================================================
    # 오른쪽 패널
    # ========================================================

    panel_x = w_img


    # ========================================================
    # 패널 제목
    # ========================================================

    cv2.putText(
        display_frame,

        "AOI RESULT",

        (
            panel_x + 20,
            45
        ),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.65,

        (
            255,
            255,
            255
        ),

        2,

        cv2.LINE_AA
    )


    # ========================================================
    # PASS / NG 상태 박스
    # ========================================================

    if is_pass:

        result_bg = (
            0,
            150,
            0
        )

        result_text = "PASS"

    else:

        result_bg = (
            0,
            0,
            180
        )

        result_text = "NG"


    cv2.rectangle(
        display_frame,

        (
            panel_x + 20,
            65
        ),

        (
            panel_x + 250,
            130
        ),

        result_bg,

        -1
    )


    cv2.rectangle(
        display_frame,

        (
            panel_x + 20,
            65
        ),

        (
            panel_x + 250,
            130
        ),

        (
            255,
            255,
            255
        ),

        2
    )


    cv2.putText(
        display_frame,

        result_text,

        (
            panel_x + 90,
            110
        ),

        cv2.FONT_HERSHEY_SIMPLEX,

        1.0,

        (
            255,
            255,
            255
        ),

        3,

        cv2.LINE_AA
    )


    # ========================================================
    # 알약 개수
    # ========================================================

    cv2.putText(
        display_frame,

        "PILL COUNT",

        (
            panel_x + 20,
            175
        ),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.5,

        (
            180,
            180,
            180
        ),

        1,

        cv2.LINE_AA
    )


    cv2.putText(
        display_frame,

        f"{pill_cnt} / 5",

        (
            panel_x + 20,
            210
        ),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.9,

        (
            255,
            255,
            255
        ),

        2,

        cv2.LINE_AA
    )


    # ========================================================
    # 미인식 알약
    # ========================================================

    cv2.putText(
        display_frame,

        "UNKNOWN",

        (
            panel_x + 20,
            255
        ),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.5,

        (
            180,
            180,
            180
        ),

        1,

        cv2.LINE_AA
    )


    if unknown_exist:

        unknown_text = "YES"

        unknown_color = (
            0,
            165,
            255
        )

    else:

        unknown_text = "NO"

        unknown_color = (
            0,
            255,
            0
        )


    cv2.putText(
        display_frame,

        unknown_text,

        (
            panel_x + 20,
            290
        ),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.8,

        unknown_color,

        2,

        cv2.LINE_AA
    )


    # ========================================================
    # 저장 버튼
    # ========================================================

    btn_x1 = panel_x + 20
    btn_y1 = 340

    btn_x2 = panel_x + 250
    btn_y2 = 425


    # PASS / NG 모두 저장 버튼 활성화

    if is_pass:

        btn_bg_color = (
            0,
            180,
            0
        )

        btn_label = "SAVE PASS"

    else:

        btn_bg_color = (
            0,
            0,
            200
        )

        btn_label = "SAVE NG"


    # ========================================================
    # 버튼 배경
    # ========================================================

    cv2.rectangle(
        display_frame,

        (
            btn_x1,
            btn_y1
        ),

        (
            btn_x2,
            btn_y2
        ),

        btn_bg_color,

        -1
    )


    # ========================================================
    # 버튼 테두리
    # ========================================================

    cv2.rectangle(
        display_frame,

        (
            btn_x1,
            btn_y1
        ),

        (
            btn_x2,
            btn_y2
        ),

        (
            255,
            255,
            255
        ),

        2
    )


    # ========================================================
    # 버튼 글자
    # ========================================================

    cv2.putText(
        display_frame,

        btn_label,

        (
            btn_x1 + 45,
            btn_y1 + 55
        ),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.75,

        (
            255,
            255,
            255
        ),

        2,

        cv2.LINE_AA
    )


    # ========================================================
    # 안내
    # ========================================================

    cv2.putText(
        display_frame,

        "CLICK TO SAVE",

        (
            panel_x + 45,
            btn_y2 + 35
        ),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.5,

        (
            200,
            200,
            200
        ),

        1,

        cv2.LINE_AA
    )


    # ========================================================
    # 검사 시간
    # ========================================================

    current_time = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )


    cv2.putText(
        display_frame,

        current_time,

        (
            panel_x + 20,
            h_img - 30
        ),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.45,

        (
            150,
            150,
            150
        ),

        1,

        cv2.LINE_AA
    )


    # ========================================================
    # 마우스 버튼 클릭
    # ========================================================

    if btn_clicked:

        cx, cy = click_pos

        btn_clicked = False


        # 버튼 영역 클릭 확인

        if (
            btn_x1 <= cx <= btn_x2
            and
            btn_y1 <= cy <= btn_y2
        ):


            # ==================================================
            # PASS 저장
            # ==================================================

            if is_pass:

                timestamp = datetime.now().strftime(
                    "%Y%m%d_%H%M%S"
                )


                image_filename = (
                    f"PASS_{timestamp}.jpg"
                )


                image_path = os.path.join(
                    SAVE_PASS_DIR,
                    image_filename
                )


                status = "PASS"


            # ==================================================
            # NG 저장
            # ==================================================

            else:

                timestamp = datetime.now().strftime(
                    "%Y%m%d_%H%M%S"
                )


                image_filename = (
                    f"NG_{timestamp}.jpg"
                )


                image_path = os.path.join(
                    SAVE_NG_DIR,
                    image_filename
                )


                status = "NG"


            # ==================================================
            # 이미지 저장
            # ==================================================

            save_success = cv2.imwrite(
                image_path,
                display_frame
            )


            # ==================================================
            # DB 저장
            # ==================================================

            db_id = db.save_result(

                item_count=pill_cnt,

                width_mm=0.0,

                height_mm=0.0,

                camera_type="USB Webcam",

                status=status,

                image_path=image_path
            )


            # ==================================================
            # 저장 결과 출력
            # ==================================================

            print()
            print("==========================================")
            print("           검사 결과 저장")
            print("==========================================")
            print(
                f"DB ID       : {db_id}"
            )
            print(
                f"검출 개수    : {pill_cnt} 개"
            )
            print(
                f"판정         : {status}"
            )
            print(
                f"미인식       : "
                f"{'YES' if unknown_exist else 'NO'}"
            )
            print(
                f"검사 시간    : {current_time}"
            )
            print(
                f"이미지 저장  : "
                f"{'성공' if save_success else '실패'}"
            )
            print(
                f"이미지 경로  : {image_path}"
            )
            print(
                f"DB 경로      : {DB_PATH}"
            )
            print("==========================================")
            print()


    # ========================================================
    # 화면 출력
    # ========================================================

    cv2.imshow(
        window_name,
        display_frame
    )


    # ========================================================
    # 키보드
    # ========================================================

    key = cv2.waitKey(1) & 0xFF


    if key == ord("q"):

        print()
        print(
            "프로그램을 종료합니다."
        )

        break


# ============================================================
# 종료
# ============================================================

cap.release()

cv2.destroyAllWindows()

db.close()


print()
print("==========================================")
print("프로그램 종료")
print("==========================================")
print(
    f"DB 위치 : {DB_PATH}"
)
print()