import os
import random
import sqlite3
from datetime import datetime, timedelta


# 1. DB 저장 및 자동 생성 전용 클래스
class SensorDatabase:

    def __init__(self, db_dir=r"D:\prj\work", db_name="sensor_data.db"):
        # 디렉터리 경로가 존재하지 않으면 생성
        if not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
            print(f"-> 디렉터리가 생성되었습니다: {db_dir}")

        self.db_path = os.path.join(db_dir, db_name)

        # DB 파일 존재 여부 미리 확인 (로그 출력용)
        is_new_db = not os.path.exists(self.db_path)

        # sqlite3.connect는 파일이 없으면 자동으로 신규 DB 파일을 만듭니다.
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()

        if is_new_db:
            print(f"-> 신규 데이터베이스 생성 완료: {self.db_path}")
        else:
            print(f"-> 기존 데이터베이스 연결 완료: {self.db_path}")

        # 테이블이 없을 경우에만 생성
        self._init_table()

    def _init_table(self):
        """센싱 데이터를 저장할 테이블 생성 (없을 때만)"""
        query = """
        CREATE TABLE IF NOT EXISTS sensor_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            item_count INTEGER NOT NULL,
            size_width_mm REAL,
            size_height_mm REAL,
            camera_type TEXT
        );
        """
        self.cursor.execute(query)
        self.conn.commit()

    def save_sensing_data(
        self,
        count,
        width_mm=0.0,
        height_mm=0.0,
        camera_type="RealSense",
        timestamp=None,
    ):
        """센싱된 데이터를 DB에 추가"""
        if timestamp is None:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        else:
            now = timestamp

        query = """
        INSERT INTO sensor_logs (timestamp, item_count, size_width_mm, size_height_mm, camera_type)
        VALUES (?, ?, ?, ?, ?);
        """
        self.cursor.execute(
            query, (now, count, width_mm, height_mm, camera_type)
        )
        self.conn.commit()
        print(
            f"[{now}] DB 저장 완료 | 카운트: {count}개 | 크기: {width_mm:.1f}x{height_mm:.1f}mm | 카메라: {camera_type}"
        )

    def close(self):
        """DB 연결 종료"""
        self.conn.close()


# ==========================================
# 2. 수량 최대 5개 조건의 10개 데이터 추가 저장 실행 코드
# ==========================================
if __name__ == "__main__":
    # DB 매니저 초기화
    db = SensorDatabase(db_dir=r"D:\prj\work", db_name="sensor_data.db")

    # 샘플 카메라 목록
    cameras = [
        "RealSense D435",
        "RealSense D455",
        "FHD Webcam",
        "Basler industrial",
    ]

    print("\n--- 수량 최대 5개 조건 데이터 10개 추가 저장 시작 ---")

    base_time = datetime.now()

    # 10개의 임의 센싱 데이터 생성 및 저장
    for i in range(1, 11):
        # 시간대를 1분 간격으로 생성
        sensing_time = (base_time - timedelta(minutes=10 - i)).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        # 수량 범위를 1 ~ 5개로 제한
        item_count = random.randint(1, 5)
        width = round(random.uniform(5.0, 25.0), 1)
        height = round(random.uniform(3.0, 15.0), 1)
        cam = random.choice(cameras)

        # 데이터 저장 실행
        db.save_sensing_data(
            count=item_count,
            width_mm=width,
            height_mm=height,
            camera_type=cam,
            timestamp=sensing_time,
        )

    print("--- 10개 데이터 저장 완료 ---\n")

    # 저장된 전체 데이터 개수 확인
    db.cursor.execute("SELECT COUNT(*) FROM sensor_logs;")
    total_records = db.cursor.fetchone()[0]
    print(f"현재 'sensor_logs' 테이블의 총 레코드 수: {total_records}개")

    # 작업 완료 후 DB 닫기
    db.close()