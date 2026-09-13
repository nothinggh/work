import sqlite3
import pandas as pd
import streamlit as st
import requests
from PIL import Image
from io import BytesIO

# ==========================================
# 1. 데이터베이스 모듈 (Database Logic)
# ==========================================

DB_PATH = 'library.db'

def get_db_connection():
    """DB 연결 객체를 반환합니다."""
    return sqlite3.connect(DB_PATH)

def init_db():
    """데이터베이스 테이블을 생성하고 기본 데이터를 초기화합니다."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            book_id TEXT PRIMARY KEY,       -- 도서번호 (ISBN)
            title TEXT NOT NULL,            -- 책제목
            author TEXT NOT NULL,           -- 저자
            rating_aladin REAL,             -- 알라딘 평점
            rating_kyobo REAL,              -- 교보문고 평점
            rating_yes24 REAL,              -- YES24 평점
            rating_interpark REAL,          -- 인터파크 평점
            avg_rating REAL,                -- 4개 서점 평점 평균
            is_borrowed INTEGER,            -- 대출 여부 (0: 대출 가능, 1: 대출 중)
            cover_url TEXT                  -- 표지 이미지 URL
        )
    ''')
    
    # 기본 더미 데이터
    books_data = [
        ("9791188850389", "성공하는 사람들의 7가지 습관", "스티븐 코비", 4.8, 4.7, 4.9, 4.6, 0, "https://contents.kyobobook.co.kr/sih/fit-in/458x0/pdt/9788934965954.jpg"),
        ("9791191043297", "불편한 편의점", "김호연", 4.9, 4.8, 4.9, 4.7, 0, "https://contents.kyobobook.co.kr/sih/fit-in/458x0/pdt/9791191043297.jpg"),
        ("9791165341909", "돈의 속성", "김승호", 4.7, 4.6, 4.8, 4.5, 1, "https://contents.kyobobook.co.kr/sih/fit-in/458x0/pdt/9791165341909.jpg"),
        ("9791197449405", "세이노의 가르침", "세이노", 4.6, 4.5, 4.7, 4.6, 0, "https://contents.kyobobook.co.kr/sih/fit-in/458x0/pdt/9791197449405.jpg"),
        ("9791191891287", "역행자", "자청", 4.5, 4.6, 4.5, 4.4, 0, "https://contents.kyobobook.co.kr/sih/fit-in/458x0/pdt/9791191891287.jpg"),
        ("9791187142560", "아몬드", "손원평", 4.8, 4.9, 4.8, 4.7, 1, "https://contents.kyobobook.co.kr/sih/fit-in/458x0/pdt/9791187142560.jpg"),
        ("9791168340770", "원씽 (The One Thing)", "게리 켈러", 4.7, 4.8, 4.7, 4.6, 0, "https://contents.kyobobook.co.kr/sih/fit-in/458x0/pdt/9791168340770.jpg"),
        ("9791190090018", "데일 카네기 인간관계론", "데일 카네기", 4.9, 4.8, 4.9, 4.8, 0, "https://contents.kyobobook.co.kr/sih/fit-in/458x0/pdt/9791190090018.jpg"),
        ("9788936433598", "채식주의자", "한강", 4.4, 4.3, 4.5, 4.2, 0, "https://contents.kyobobook.co.kr/sih/fit-in/458x0/pdt/9788936433598.jpg"),
        ("9791162540640", "원자적 습관 (Atomic Habits)", "제임스 클리어", 4.8, 4.9, 4.8, 4.8, 1, "https://contents.kyobobook.co.kr/sih/fit-in/458x0/pdt/9791162540640.jpg")
    ]
    
    for book in books_data:
        b_id, title, author, r1, r2, r3, r4, is_b, cover = book
        avg = round((r1 + r2 + r3 + r4) / 4, 2)
        cursor.execute('''
            INSERT OR IGNORE INTO books 
            (book_id, title, author, rating_aladin, rating_kyobo, rating_yes24, rating_interpark, avg_rating, is_borrowed, cover_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (b_id, title, author, r1, r2, r3, r4, avg, is_b, cover))
        
    conn.commit()
    conn.close()

def load_all_books():
    """전체 도서 데이터를 가져옵니다."""
    conn = get_db_connection()
    df = pd.read_sql("SELECT * FROM books ORDER BY title ASC", conn)
    conn.close()
    return df

def insert_book(book_id, title, author, r_aladin, r_kyobo, r_yes, r_interpark, is_borrowed, cover_url):
    """새로운 도서를 추가합니다."""
    conn = get_db_connection()
    cursor = conn.cursor()
    avg_rating = round((r_aladin + r_kyobo + r_yes + r_interpark) / 4, 2)
    
    cursor.execute('''
        INSERT INTO books (book_id, title, author, rating_aladin, rating_kyobo, rating_yes24, rating_interpark, avg_rating, is_borrowed, cover_url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (book_id, title, author, r_aladin, r_kyobo, r_yes, r_interpark, avg_rating, is_borrowed, cover_url))
    
    conn.commit()
    conn.close()

def update_book(book_id, title, author, r_aladin, r_kyobo, r_yes, r_interpark, is_borrowed, cover_url):
    """기존 도서 정보를 수정합니다."""
    conn = get_db_connection()
    cursor = conn.cursor()
    avg_rating = round((r_aladin + r_kyobo + r_yes + r_interpark) / 4, 2)
    
    cursor.execute('''
        UPDATE books 
        SET title=?, author=?, rating_aladin=?, rating_kyobo=?, rating_yes24=?, rating_interpark=?, avg_rating=?, is_borrowed=?, cover_url=?
        WHERE book_id=?
    ''', (title, author, r_aladin, r_kyobo, r_yes, r_interpark, avg_rating, is_borrowed, cover_url, book_id))
    
    conn.commit()
    conn.close()

def delete_book(book_id):
    """도서를 삭제합니다."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM books WHERE book_id = ?", (book_id,))
    conn.commit()
    conn.close()


# ==========================================
# 2. 이미지 로더 및 네트워크 보완 (Image Handler)
# ==========================================

@st.cache_data(ttl=3600)
def fetch_image_from_url(url_str):
    """
    서점별 (알라딘, 교보, YES24 등) 이미지 핫링크 차단을 방지하기 위한 우회 다운로드 로직입니다.
    """
    if not url_str or not url_str.startswith("http"):
        return None

    referer = "https://www.google.com/"
    if "aladin.co.kr" in url_str:
        referer = "https://www.aladin.co.kr/"
    elif "kyobobook.co.kr" in url_str:
        referer = "https://www.kyobobook.co.kr/"
    elif "yes24.com" in url_str:
        referer = "https://www.yes24.com/"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': referer,
        'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8'
    }
    try:
        response = requests.get(url_str, headers=headers, timeout=5)
        if response.status_code == 200:
            return response.content
    except Exception:
        pass
    return None

def render_book_cover(cover_url, width=85):
    """도서 표지 이미지를 안전하게 출력합니다."""
    img_bytes = fetch_image_from_url(cover_url)
    if img_bytes:
        try:
            img = Image.open(BytesIO(img_bytes))
            st.image(img, width=width)
            return
        except Exception:
            pass
    st.caption("📷 표지 없음")


# ==========================================
# 3. UI 렌더링 모듈 (Views)
# ==========================================

def render_book_card(row):
    """도서 1개 항목에 대한 카드를 출력합니다."""
    col_cover, col_info = st.columns([1, 7])
    
    with col_cover:
        render_book_cover(row['cover_url'])
        
    with col_info:
        col_title, col_status = st.columns([3.5, 1.2])
        with col_title:
            st.markdown(
                f"<h3 style='margin:0; padding:0; display:inline-block;'>{row['title']}</h3> "
                f"<span style='color: #666; font-size: 0.85em; margin-left: 8px;'>"
                f"<b>저자:</b> {row['author']} | <b>ISBN:</b> {row['book_id']}"
                f"</span>", 
                unsafe_allow_html=True
            )
        with col_status:
            if row['is_borrowed'] == 0:
                st.markdown("<span style='background-color:#E8F5E9; color:#2E7D32; padding:3px 10px; border-radius:12px; font-weight:bold; font-size:0.8em;'>🟢 대출 가능</span>", unsafe_allow_html=True)
            else:
                st.markdown("<span style='background-color:#FFEBEE; color:#C62828; padding:3px 10px; border-radius:12px; font-weight:bold; font-size:0.8em;'>🔴 대출 중</span>", unsafe_allow_html=True)

        st.markdown(
            f"<div style='margin-top: 8px; font-size: 0.85em; background-color: #f8f9fa; padding: 6px 12px; border-radius: 6px; border: 1px solid #eee;'>"
            f"<b>📊 4개 서점 평점:</b> "
            f"알라딘 <b>⭐ {row['rating_aladin']}</b> | "
            f"교보 <b>⭐ {row['rating_kyobo']}</b> | "
            f"YES24 <b>⭐ {row['rating_yes24']}</b> | "
            f"인터파크 <b>⭐ {row['rating_interpark']}</b> "
            f"&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; "
            f"<span style='color: #d97706; font-weight: bold;'>통합 평균: ⭐ {row['avg_rating']} / 5.0</span>"
            f"</div>",
            unsafe_allow_html=True
        )


# --- 1) 도서 목록 검색 화면 (상단 헤더/필터 고정 적용) ---
def view_search_books(df):
    # CSS를 적용해 상단 검색 영역을 고정(Sticky)시킵니다.
    st.markdown("""
        <style>
            div[data-testid="stVerticalBlock"] > div:has(div.sticky-header) {
                position: sticky;
                top: 2.875rem;
                background-color: white;
                z-index: 999;
                padding-bottom: 15px;
                border-bottom: 1px solid #f0f0f0;
            }
        </style>
    """, unsafe_allow_html=True)

    header_container = st.container()
    
    with header_container:
        st.markdown('<div class="sticky-header"></div>', unsafe_allow_html=True)
        st.subheader("🔍 도서 목록 검색")
        
        col1, col2 = st.columns(2)
        with col1:
            search_target = st.selectbox("검색 항목", ["전체", "책 제목", "작가명"])
            search_kw = st.text_input("검색어 입력", placeholder="예: 한강, 세이노, 습관")
        with col2:
            status_filter = st.radio("대출 상태 필터", ["전체", "대출 가능만", "대출 중만"], horizontal=True)
            min_rating = st.slider("최소 통합 평점 기준", 0.0, 5.0, 0.0, 0.1)

    # 필터링 적용
    filtered_df = df.copy()

    if search_kw:
        kw = search_kw.strip().lower()
        if search_target == "책 제목":
            filtered_df = filtered_df[filtered_df['title'].str.lower().str.contains(kw, na=False)]
        elif search_target == "작가명":
            filtered_df = filtered_df[filtered_df['author'].str.lower().str.contains(kw, na=False)]
        else:
            filtered_df = filtered_df[
                filtered_df['title'].str.lower().str.contains(kw, na=False) |
                filtered_df['author'].str.lower().str.contains(kw, na=False)
            ]

    if status_filter == "대출 가능만":
        filtered_df = filtered_df[filtered_df['is_borrowed'] == 0]
    elif status_filter == "대출 중만":
        filtered_df = filtered_df[filtered_df['is_borrowed'] == 1]

    filtered_df = filtered_df[filtered_df['avg_rating'] >= min_rating]

    st.caption(f"총 **{len(filtered_df)}개**의 도서가 검색되었습니다.")
    st.divider()

    if filtered_df.empty:
        st.warning("검색 결과가 없습니다.")
    else:
        for _, row in filtered_df.iterrows():
            render_book_card(row)
            st.divider()


# --- 2) 도서 목록 추가 화면 ---
def view_add_book(df):
    st.subheader("➕ 신규 도서 등록")
    
    with st.form("add_book_form"):
        col1, col2 = st.columns(2)
        with col1:
            book_id = st.text_input("ISBN / 도서 번호 (필수)", placeholder="예: 9791191043297")
            title = st.text_input("책 제목 (필수)", placeholder="예: 미움받을 용기")
            author = st.text_input("작가명 (필수)", placeholder="예: 기시미 이치로")
            is_borrowed = st.selectbox("대출 상태", options=[0, 1], format_func=lambda x: "대출 가능" if x == 0 else "대출 중")
        
        with col2:
            r_aladin = st.number_input("알라딘 평점", 0.0, 5.0, 4.5, 0.1)
            r_kyobo = st.number_input("교보문고 평점", 0.0, 5.0, 4.5, 0.1)
            r_yes = st.number_input("YES24 평점", 0.0, 5.0, 4.5, 0.1)
            r_interpark = st.number_input("인터파크 평점", 0.0, 5.0, 4.5, 0.1)
        
        cover_url = st.text_input("표지 이미지 URL", placeholder="https://example.com/image.jpg")
        
        if cover_url:
            st.caption("📷 입력 이미지 미리보기")
            render_book_cover(cover_url, width=100)

        submitted = st.form_submit_button("도서 추가하기", use_container_width=True)

        if submitted:
            if not book_id.strip() or not title.strip() or not author.strip():
                st.error("도서 번호, 책 제목, 작가명은 필수 항목입니다.")
            elif book_id in df['book_id'].values:
                st.error("이미 존재하는 도서 번호(ISBN)입니다.")
            else:
                insert_book(book_id.strip(), title.strip(), author.strip(), r_aladin, r_kyobo, r_yes, r_interpark, is_borrowed, cover_url.strip())
                st.success(f"'{title}' 도서가 성공적으로 등록되었습니다!")
                st.rerun()


# --- 3) 도서 목록 수정 화면 ---
def view_edit_book(df):
    st.subheader("✏️ 도서 정보 수정")
    if df.empty:
        st.info("수정할 도서가 존재하지 않습니다.")
        return

    book_options = {f"{row['title']} ({row['book_id']})": row['book_id'] for _, row in df.iterrows()}
    selected_label = st.selectbox("수정할 도서를 선택하세요", list(book_options.keys()))
    selected_id = book_options[selected_label]
    
    book_data = df[df['book_id'] == selected_id].iloc[0]

    with st.form("edit_book_form"):
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("ISBN (수정 불가)", value=book_data['book_id'], disabled=True)
            title = st.text_input("책 제목", value=book_data['title'])
            author = st.text_input("작가명", value=book_data['author'])
            is_borrowed = st.selectbox("대출 상태", options=[0, 1], index=int(book_data['is_borrowed']), format_func=lambda x: "대출 가능" if x == 0 else "대출 중")

        with col2:
            r_aladin = st.number_input("알라딘 평점", 0.0, 5.0, float(book_data['rating_aladin']), 0.1)
            r_kyobo = st.number_input("교보문고 평점", 0.0, 5.0, float(book_data['rating_kyobo']), 0.1)
            r_yes = st.number_input("YES24 평점", 0.0, 5.0, float(book_data['rating_yes24']), 0.1)
            r_interpark = st.number_input("인터파크 평점", 0.0, 5.0, float(book_data['rating_interpark']), 0.1)

        cover_url = st.text_input("표지 이미지 URL", value=book_data['cover_url'])

        if cover_url:
            st.caption("📷 현재 표지 미리보기")
            render_book_cover(cover_url, width=100)

        submitted = st.form_submit_button("정보 수정 완료", use_container_width=True)

        if submitted:
            update_book(selected_id, title.strip(), author.strip(), r_aladin, r_kyobo, r_yes, r_interpark, is_borrowed, cover_url.strip())
            st.success("도서 정보가 성공적으로 수정되었습니다.")
            st.rerun()


# --- 4) 도서 목록 삭제 화면 ---
def view_delete_book(df):
    st.subheader("🗑️ 도서 삭제")
    if df.empty:
        st.info("삭제할 도서가 없습니다.")
        return

    book_options = {f"{row['title']} - {row['author']} (ISBN: {row['book_id']})": row['book_id'] for _, row in df.iterrows()}
    selected_label = st.selectbox("삭제 대상 도서를 선택하세요", list(book_options.keys()))
    selected_id = book_options[selected_label]
    
    target_book = df[df['book_id'] == selected_id].iloc[0]

    st.warning(f"⚠️ 선택한 도서: **{target_book['title']}** ({target_book['author']})")
    
    col_cover, col_btn = st.columns([1, 4])
    with col_cover:
        render_book_cover(target_book['cover_url'], width=100)
    with col_btn:
        st.write(f"- ISBN: {target_book['book_id']}")
        st.write(f"- 통합 평점: ⭐ {target_book['avg_rating']}")
        if st.button("❌ 정말 삭제하시겠습니까?", type="primary"):
            delete_book(selected_id)
            st.success("도서가 성공적으로 삭제되었습니다.")
            st.rerun()


# ==========================================
# 4. 메인 애플리케이션 흐름 (Main Controller)
# ==========================================

def main():
    st.set_page_config(page_title="통합 도서 관리 시스템", layout="wide")
    
    # 상단 타이틀 영역 고정
    st.markdown("""
        <style>
            .title-header {
                position: sticky;
                top: 0;
                background-color: white;
                z-index: 1000;
                padding-top: 10px;
                padding-bottom: 5px;
            }
        </style>
        <div class="title-header">
            <h1 style="margin:0;">📚 통합 도서 관리 및 평점 분석 시스템</h1>
        </div>
    """, unsafe_allow_html=True)

    # DB 초기화 및 데이터 로드
    init_db()
    df_books = load_all_books()

    # 사이드바 관리 메뉴
    st.sidebar.header("📌 관리 메뉴")
    menu = st.sidebar.radio(
        "기능을 선택하세요",
        ["1) 도서 목록 검색", "2) 도서 목록 추가", "3) 도서 목록 수정", "4) 도서 목록 삭제"]
    )

    # 선택된 메뉴 실행
    if menu == "1) 도서 목록 검색":
        view_search_books(df_books)
    elif menu == "2) 도서 목록 추가":
        view_add_book(df_books)
    elif menu == "3) 도서 목록 수정":
        view_edit_book(df_books)
    elif menu == "4) 도서 목록 삭제":
        view_delete_book(df_books)

if __name__ == "__main__":
    main()