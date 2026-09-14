import sqlite3
import pandas as pd
import streamlit as st

# ---------------------------------------------------------
# 1. DB 연동 및 테이블 초기화
# ---------------------------------------------------------
DB_NAME = "books.db"


def get_connection():
    """SQLite DB 연결 객체 반환"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # 컬럼명으로 접근 가능하도록 설정
    return conn


def init_db():
    """도서 테이블 생성 (없는 경우)"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                category TEXT,
                published_year INTEGER,
                status TEXT DEFAULT '대출 가능'
            )
        """
        )
        conn.commit()


# 앱 시작 시 DB 테이블 자동 생성
init_db()

# ---------------------------------------------------------
# 2. DB CRUD 함수 정의
# ---------------------------------------------------------


def add_book(title, author, category, published_year):
    """신규 도서 추가"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO books (title, author, category, published_year, status)
            VALUES (?, ?, ?, ?, '대출 가능')
        """,
            (title, author, category, published_year),
        )
        conn.commit()


def get_all_books():
    """전체 도서 목록 조회"""
    with get_connection() as conn:
        df = pd.read_sql_query("SELECT * FROM books ORDER BY id DESC", conn)
    return df


def search_books(keyword):
    """제목 또는 저자로 도서 검색"""
    with get_connection() as conn:
        query = "SELECT * FROM books WHERE title LIKE ? OR author LIKE ? ORDER BY id DESC"
        df = pd.read_sql_query(query, conn, params=(f"%{keyword}%", f"%{keyword}%"))
    return df


def update_book_status(book_id, new_status):
    """대출 상태 변경 (대출 가능 / 대출 중)"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE books SET status = ? WHERE id = ?", (new_status, book_id)
        )
        conn.commit()


def delete_book(book_id):
    """도서 삭제"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM books WHERE id = ?", (book_id,))
        conn.commit()


# ---------------------------------------------------------
# 3. Streamlit UI 구성
# ---------------------------------------------------------
st.set_page_config(
    page_title="도서 관리 시스템", page_icon="📚", layout="wide"
)

st.title("📚 SQLite 기반 도서 관리 시스템")
st.markdown("---")

# 사이드바 메뉴
menu = ["도서 목록 / 검색", "도서 등록", "상태 변경 / 삭제"]
choice = st.sidebar.selectbox("메뉴 선택", menu)

# ---------------------------------------------------------
# 메뉴 1: 도서 목록 및 검색
# ---------------------------------------------------------
if choice == "도서 목록 / 검색":
    st.subheader("📖 전체 도서 목록 및 검색")

    # 검색 창
    search_term = st.text_input("도서 제목 또는 저자명 검색")

    if search_term:
        df = search_books(search_term)
        st.write(f"🔍 **'{search_term}'** 검색 결과 ({len(df)}건)")
    else:
        df = get_all_books()

    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("등록된 도서가 없습니다.")

# ---------------------------------------------------------
# 메뉴 2: 신규 도서 등록
# ---------------------------------------------------------
elif choice == "도서 등록":
    st.subheader("➕ 신규 도서 등록")

    with st.form("add_book_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            title = st.text_input("도서 제목 *")
            author = st.text_input("저자 *")

        with col2:
            category = st.selectbox(
                "카테고리", ["소설", "인문", "과학/기술", "자기계발", "기타"]
            )
            published_year = st.number_input(
                "출판 연도", min_value=1900, max_value=2026, value=2024
            )

        submit = st.form_submit_button("도서 등록하기")

        if submit:
            if title.strip() == "" or author.strip() == "":
                st.error("도서 제목과 저자는 필수 입력 항목입니다.")
            else:
                add_book(title, author, category, published_year)
                st.success(f"'{title}' 도서가 성공적으로 등록되었습니다!")

# ---------------------------------------------------------
# 메뉴 3: 도서 상태 변경 및 삭제
# ---------------------------------------------------------
elif choice == "상태 변경 / 삭제":
    st.subheader("⚙️ 도서 정보 관리")

    df = get_all_books()

    if not df.empty:
        # 도서 선택
        book_options = {
            f"[{row['id']}] {row['title']} ({row['author']}) - {row['status']}": row[
                "id"
            ]
            for _, row in df.iterrows()
        }
        selected_book_label = st.selectbox(
            "관리할 도서를 선택하세요", list(book_options.keys())
        )
        selected_id = book_options[selected_book_label]

        col1, col2 = st.columns(2)

        # 상태 변경 구역
        with col1:
            st.markdown("### 🔄 대출 상태 변경")
            current_status = df[df["id"] == selected_id]["status"].values[0]
            new_status = st.radio(
                "상태 선택",
                ["대출 가능", "대출 중"],
                index=0 if current_status == "대출 가능" else 1,
            )

            if st.button("상태 업데이트"):
                update_book_status(selected_id, new_status)
                st.success("대출 상태가 변경되었습니다.")
                st.rerun()

        # 삭제 구역
        with col2:
            st.markdown("### 🗑️ 도서 삭제")
            st.warning("삭제된 데이터는 복구할 수 없습니다.")
            if st.button("도서 삭제하기", type="primary"):
                delete_book(selected_id)
                st.success("도서가 삭제되었습니다.")
                st.rerun()
    else:
        st.info("등록된 도서가 없습니다.")