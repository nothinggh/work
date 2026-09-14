import cv2
import easyocr
import re
from collections import Counter

def count_text_in_video(video_path, target_word, sample_interval_sec=1.0):
    """
    동영상 내에서 특정 문자열의 등장 횟수를 카운트합니다.
    
    :param video_path: 동영상 파일 경로
    :param target_word: 찾고자 하는 문자열 (예: "Filter")
    :param sample_interval_sec: 몇 초마다 프레임을 검사할지 설정 (기본값: 1초)
    """
    # 1. EasyOCR 리더 초기화 (한국어 + 영어 지원)
    # GPU가 있으면 gpu=True, 없으면 gpu=False로 자동 전환
    reader = easyocr.Reader(['ko', 'en'], gpu=True)
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"동영상을 열 수 없습니다: {video_path}")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps == 0 or not fps:
        fps = 30.0  # 기본값 설정

    # 샘플링할 프레임 간격 계산
    frame_interval = int(fps * sample_interval_sec)
    frame_count = 0
    match_count = 0

    print(f"[{video_path}] 분석 시작...")
    print(f"검색할 단어: '{target_word}' (샘플링 주기: {sample_interval_sec}초)")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # 지정한 간격의 프레임에서만 OCR 수행
        if frame_count % frame_interval == 0:
            current_sec = frame_count / fps
            
            # OCR 수행 (텍스트 리스트 반환)
            results = reader.readtext(frame, detail=0)
            
            # 인식된 모든 텍스트를 하나의 문자열로 결합 후 검색
            frame_text = " ".join(results)
            
            # 대소문자 구분 없이 찾기 (정규표현식)
            matches = re.findall(re.escape(target_word), frame_text, re.IGNORECASE)
            found_in_frame = len(matches)

            if found_in_frame > 0:
                match_count += found_in_frame
                print(f"[{current_sec:.1f}초] '{target_word}' {found_in_frame}개 발견 (프레임 내 텍스트: {results})")

        frame_count += 1

    cap.release()
    print("-" * 50)
    print(f"최종 결과: '{target_word}' 총 {match_count}회 감지됨")
    return match_count

# --- 사용 예시 ---
if __name__ == "__main__":
    video_file = "output.mp4"
    search_keyword = "Filter"  # 찾고자 하는 필터 관련 문자열 입력
    
    count_text_in_video(video_file, search_keyword, sample_interval_sec=0.5)