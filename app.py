import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, date
from pathlib import Path

# =========================================================
# CONFIG
# =========================================================

st.set_page_config(
    page_title="Hotel Room Management",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded"
)

DB_FILE = Path("hotel.db")


# =========================================================
# DATABASE
# =========================================================

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_number TEXT UNIQUE NOT NULL,
            room_type TEXT NOT NULL,
            floor INTEGER NOT NULL,
            price REAL NOT NULL,
            status TEXT NOT NULL DEFAULT 'Trống',
            guest_name TEXT,
            guest_phone TEXT,
            check_in TEXT,
            check_out TEXT,
            notes TEXT
        )
    """)

    conn.commit()

    # Tạo dữ liệu mẫu nếu database chưa có phòng
    count = cursor.execute("SELECT COUNT(*) FROM rooms").fetchone()[0]

    if count == 0:
        sample_rooms = [
            ("101", "Standard", 1, 800000, "Trống"),
            ("102", "Standard", 1, 800000, "Đã đặt"),
            ("103", "Deluxe", 1, 1200000, "Đang ở"),
            ("104", "Deluxe", 1, 1200000, "Đang dọn"),
            ("201", "Standard", 2, 800000, "Trống"),
            ("202", "Superior", 2, 1000000, "Đang ở"),
            ("203", "Superior", 2, 1000000, "Bảo trì"),
            ("204", "Deluxe", 2, 1200000, "Trống"),
            ("301", "Suite", 3, 2200000, "Đã đặt"),
            ("302", "Suite", 3, 2200000, "Trống"),
            ("303", "Deluxe", 3, 1200000, "Đang ở"),
            ("304", "Standard", 3, 800000, "Trống"),
        ]

        cursor.executemany("""
            INSERT INTO rooms
            (room_number, room_type, floor, price, status)
            VALUES (?, ?, ?, ?, ?)
        """, sample_rooms)

        # Thêm thông tin khách mẫu
        cursor.execute("""
            UPDATE rooms
            SET guest_name = ?,
                guest_phone = ?,
                check_in = ?,
                check_out = ?
            WHERE room_number = ?
        """, (
            "Nguyễn Văn An",
            "0901234567",
            "2026-09-26",
            "2026-09-29",
            "103"
        ))

        cursor.execute("""
            UPDATE rooms
            SET guest_name = ?,
                guest_phone = ?,
                check_in = ?,
                check_out = ?
            WHERE room_number = ?
        """, (
            "Trần Minh Anh",
            "0912345678",
            "2026-09-27",
            "2026-09-30",
            "202"
        ))

        cursor.execute("""
            UPDATE rooms
            SET guest_name = ?,
                guest_phone = ?,
                check_in = ?,
                check_out = ?
            WHERE room_number = ?
        """, (
            "Lê Hoàng Nam",
            "0987654321",
            "2026-09-25",
            "2026-09-28",
            "303"
        ))

        conn.commit()

    conn.close()


# =========================================================
# DATABASE FUNCTIONS
# =========================================================

def get_rooms():
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT * FROM rooms ORDER BY floor, room_number",
        conn
    )
    conn.close()
    return df


def add_room(room_number, room_type, floor, price, status):
    conn = get_connection()

    try:
        conn.execute("""
            INSERT INTO rooms
            (room_number, room_type, floor, price, status)
            VALUES (?, ?, ?, ?, ?)
        """, (
            room_number,
            room_type,
            floor,
            price,
            status
        ))

        conn.commit()
        return True, "Thêm phòng thành công."

    except sqlite3.IntegrityError:
        return False, "Số phòng đã tồn tại."

    finally:
        conn.close()


def update_room(
    room_id,
    room_number,
    room_type,
    floor,
    price,
    status,
    notes
):
    conn = get_connection()

    try:
        conn.execute("""
            UPDATE rooms
            SET room_number = ?,
                room_type = ?,
                floor = ?,
                price = ?,
                status = ?,
                notes = ?
            WHERE id = ?
        """, (
            room_number,
            room_type,
            floor,
            price,
            status,
            notes,
            room_id
        ))

        conn.commit()
        return True, "Cập nhật phòng thành công."

    except sqlite3.IntegrityError:
        return False, "Số phòng đã tồn tại."

    finally:
        conn.close()


def delete_room(room_id):
    conn = get_connection()

    conn.execute(
        "DELETE FROM rooms WHERE id = ?",
        (room_id,)
    )

    conn.commit()
    conn.close()


def update_room_status(room_id, status):
    conn = get_connection()

    conn.execute("""
        UPDATE rooms
        SET status = ?
        WHERE id = ?
    """, (status, room_id))

    conn.commit()
    conn.close()


def check_in(
    room_id,
    guest_name,
    guest_phone,
    check_in_date,
    check_out_date,
    notes
):
    conn = get_connection()

    conn.execute("""
        UPDATE rooms
        SET status = 'Đang ở',
            guest_name = ?,
            guest_phone = ?,
            check_in = ?,
            check_out = ?,
            notes = ?
        WHERE id = ?
    """, (
        guest_name,
        guest_phone,
        check_in_date,
        check_out_date,
        notes,
        room_id
    ))

    conn.commit()
    conn.close()


def check_out(room_id):
    conn = get_connection()

    conn.execute("""
        UPDATE rooms
        SET status = 'Đang dọn',
            guest_name = NULL,
            guest_phone = NULL,
            check_in = NULL,
            check_out = NULL
        WHERE id = ?
    """, (room_id,))

    conn.commit()
    conn.close()


# =========================================================
# HELPER
# =========================================================

def format_money(value):
    return f"{value:,.0f} VNĐ"


def status_icon(status):
    icons = {
        "Trống": "🟢",
        "Đã đặt": "🔵",
        "Đang ở": "🟠",
        "Đang dọn": "🧹",
        "Bảo trì": "🔴"
    }

    return icons.get(status, "⚪")


def status_color(status):
    colors = {
        "Trống": "#16a34a",
        "Đã đặt": "#2563eb",
        "Đang ở": "#f59e0b",
        "Đang dọn": "#8b5cf6",
        "Bảo trì": "#dc2626"
    }

    return colors.get(status, "#6b7280")


# =========================================================
# INITIALIZE
# =========================================================

init_database()

rooms = get_rooms()


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

.main-title {
    font-size: 32px;
    font-weight: 700;
    margin-bottom: 5px;
}

.subtitle {
    color: #6b7280;
    margin-bottom: 25px;
}

.metric-card {
    padding: 20px;
    border-radius: 14px;
    background: white;
    border: 1px solid #e5e7eb;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

.room-card {
    padding: 18px;
    border-radius: 14px;
    border: 1px solid #e5e7eb;
    background: white;
    margin-bottom: 10px;
}

.room-number {
    font-size: 22px;
    font-weight: 700;
}

.guest-name {
    color: #374151;
    margin-top: 8px;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("🏨 Hotel PMS")

st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "MENU",
    [
        "📊 Tổng quan",
        "🛏️ Quản lý phòng",
        "👤 Check-in",
        "🚪 Check-out",
        "➕ Thêm phòng"
    ]
)

st.sidebar.markdown("---")

st.sidebar.info(
    "Hotel Room Management\n\n"
    "Quản lý phòng khách sạn bằng Streamlit + SQLite."
)


# =========================================================
# DASHBOARD
# =========================================================

if menu == "📊 Tổng quan":

    st.markdown(
        '<div class="main-title">🏨 Tổng quan khách sạn</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">Theo dõi tình trạng phòng theo thời gian thực</div>',
        unsafe_allow_html=True
    )

    total = len(rooms)
    empty = len(rooms[rooms["status"] == "Trống"])
    booked = len(rooms[rooms["status"] == "Đã đặt"])
    occupied = len(rooms[rooms["status"] == "Đang ở"])
    cleaning = len(rooms[rooms["status"] == "Đang dọn"])
    maintenance = len(rooms[rooms["status"] == "Bảo trì"])

    occupancy_rate = 0

    if total > 0:
        occupancy_rate = occupied / total * 100

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "🏨 Tổng phòng",
            total
        )

    with col2:
        st.metric(
            "🟢 Phòng trống",
            empty
        )

    with col3:
        st.metric(
            "🟠 Đang ở",
            occupied
        )

    with col4:
        st.metric(
            "📈 Công suất",
            f"{occupancy_rate:.1f}%"
        )

    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("🔵 Đã đặt", booked)

    with col2:
        st.metric("🧹 Đang dọn", cleaning)

    with col3:
        st.metric("🔴 Bảo trì", maintenance)

    st.markdown("### 📋 Tình trạng phòng")

    status_data = pd.DataFrame({
        "Trạng thái": [
            "🟢 Trống",
            "🔵 Đã đặt",
            "🟠 Đang ở",
            "🧹 Đang dọn",
            "🔴 Bảo trì"
        ],
        "Số phòng": [
            empty,
            booked,
            occupied,
            cleaning,
            maintenance
        ]
    })

    st.dataframe(
        status_data,
        use_container_width=True,
        hide_index=True
    )

    st.markdown("### 👥 Khách đang lưu trú")

    occupied_rooms = rooms[
        rooms["status"] == "Đang ở"
    ].copy()

    if len(occupied_rooms) == 0:
        st.info("Hiện không có khách đang lưu trú.")

    else:

        display_df = occupied_rooms[
            [
                "room_number",
                "room_type",
                "guest_name",
                "guest_phone",
                "check_in",
                "check_out"
            ]
        ].copy()

        display_df.columns = [
            "Phòng",
            "Loại phòng",
            "Tên khách",
            "Số điện thoại",
            "Check-in",
            "Check-out"
        ]

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )


# =========================================================
# ROOM MANAGEMENT
# =========================================================

elif menu == "🛏️ Quản lý phòng":

    st.markdown(
        '<div class="main-title">🛏️ Quản lý phòng</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">Theo dõi và cập nhật tình trạng từng phòng</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        search = st.text_input(
            "🔎 Tìm phòng",
            placeholder="Nhập số phòng..."
        )

    with col2:
        filter_status = st.selectbox(
            "📌 Trạng thái",
            [
                "Tất cả",
                "Trống",
                "Đã đặt",
                "Đang ở",
                "Đang dọn",
                "Bảo trì"
            ]
        )

    with col3:
        filter_type = st.selectbox(
            "🛏️ Loại phòng",
            ["Tất cả"] + sorted(
                rooms["room_type"].unique().tolist()
            )
        )

    filtered = rooms.copy()

    if search:
        filtered = filtered[
            filtered["room_number"]
            .astype(str)
            .str.contains(search, case=False)
        ]

    if filter_status != "Tất cả":
        filtered = filtered[
            filtered["status"] == filter_status
        ]

    if filter_type != "Tất cả":
        filtered = filtered[
            filtered["room_type"] == filter_type
        ]

    st.markdown(
        f"**Hiển thị {len(filtered)} phòng**"
    )

    for _, room in filtered.iterrows():

        status = room["status"]

        with st.container(border=True):

            col1, col2, col3, col4, col5 = st.columns(
                [1, 2, 2, 2, 1.2]
            )

            with col1:
                st.markdown(
                    f"### 🚪 {room['room_number']}"
                )

            with col2:
                st.write(
                    f"**Loại:** {room['room_type']}"
                )
                st.write(
                    f"Tầng {room['floor']}"
                )

            with col3:
                st.write(
                    f"**Giá:** {format_money(room['price'])}"
                )

                st.markdown(
                    f"**{status_icon(status)} {status}**"
                )

            with col4:

                if room["guest_name"]:
                    st.write(
                        f"👤 {room['guest_name']}"
                    )

                    if room["check_out"]:
                        st.caption(
                            f"Check-out: {room['check_out']}"
                        )

                else:
                    st.caption("Chưa có khách")

            with col5:

                new_status = st.selectbox(
                    "Trạng thái",
                    [
                        "Trống",
                        "Đã đặt",
                        "Đang ở",
                        "Đang dọn",
                        "Bảo trì"
                    ],
                    index=[
                        "Trống",
                        "Đã đặt",
                        "Đang ở",
                        "Đang dọn",
                        "Bảo trì"
                    ].index(status),
                    key=f"status_{room['id']}",
                    label_visibility="collapsed"
                )

                if new_status != status:

                    if st.button(
                        "Cập nhật",
                        key=f"update_{room['id']}"
                    ):

                        update_room_status(
                            room["id"],
                            new_status
                        )

                        st.success("Đã cập nhật.")

                        st.rerun()

            with st.expander("✏️ Chỉnh sửa thông tin phòng"):

                with st.form(
                    f"edit_room_{room['id']}"
                ):

                    c1, c2 = st.columns(2)

                    with c1:

                        room_number = st.text_input(
                            "Số phòng",
                            value=room["room_number"]
                        )

                        room_type = st.selectbox(
                            "Loại phòng",
                            [
                                "Standard",
                                "Superior",
                                "Deluxe",
                                "Suite"
                            ],
                            index=[
                                "Standard",
                                "Superior",
                                "Deluxe",
                                "Suite"
                            ].index(room["room_type"])
                            if room["room_type"] in [
                                "Standard",
                                "Superior",
                                "Deluxe",
                                "Suite"
                            ]
                            else 0
                        )

                    with c2:

                        floor = st.number_input(
                            "Tầng",
                            min_value=1,
                            max_value=100,
                            value=int(room["floor"])
                        )

                        price = st.number_input(
                            "Giá phòng / đêm",
                            min_value=0,
                            value=float(room["price"]),
                            step=100000.0
                        )

                    notes = st.text_area(
                        "Ghi chú",
                        value=room["notes"] or ""
                    )

                    submitted = st.form_submit_button(
                        "💾 Lưu thay đổi",
                        use_container_width=True
                    )

                    if submitted:

                        success, message = update_room(
                            room["id"],
                            room_number,
                            room_type,
                            floor,
                            price,
                            status,
                            notes
                        )

                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)

                if st.button(
                    "🗑️ Xóa phòng",
                    key=f"delete_{room['id']}"
                ):

                    delete_room(room["id"])

                    st.success("Đã xóa phòng.")

                    st.rerun()


# =========================================================
# CHECK IN
# =========================================================

elif menu == "👤 Check-in":

    st.markdown(
        '<div class="main-title">👤 Check-in khách</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">Đăng ký khách nhận phòng</div>',
        unsafe_allow_html=True
    )

    available_rooms = rooms[
        rooms["status"].isin(
            ["Trống", "Đã đặt"]
        )
    ]

    if len(available_rooms) == 0:

        st.warning(
            "Không có phòng phù hợp để check-in."
        )

    else:

        room_options = {
            f"{row['room_number']} - "
            f"{row['room_type']} - "
            f"{format_money(row['price'])}": row["id"]
            for _, row in available_rooms.iterrows()
        }

        with st.form("checkin_form"):

            selected_room = st.selectbox(
                "🚪 Chọn phòng",
                list(room_options.keys())
            )

            col1, col2 = st.columns(2)

            with col1:

                guest_name = st.text_input(
                    "👤 Họ và tên khách *"
                )

                guest_phone = st.text_input(
                    "📱 Số điện thoại"
                )

                check_in_date = st.date_input(
                    "📅 Ngày check-in",
                    value=date.today()
                )

            with col2:

                check_out_date = st.date_input(
                    "📅 Ngày check-out",
                    value=date.today()
                )

                notes = st.text_area(
                    "📝 Ghi chú"
                )

            submit = st.form_submit_button(
                "✅ Xác nhận Check-in",
                use_container_width=True
            )

            if submit:

                if not guest_name.strip():

                    st.error(
                        "Vui lòng nhập tên khách."
                    )

                elif check_out_date < check_in_date:

                    st.error(
                        "Ngày check-out không hợp lệ."
                    )

                else:

                    room_id = room_options[selected_room]

                    check_in(
                        room_id,
                        guest_name,
                        guest_phone,
                        check_in_date.isoformat(),
                        check_out_date.isoformat(),
                        notes
                    )

                    st.success(
                        f"Check-in thành công cho {guest_name}."
                    )

                    st.rerun()


# =========================================================
# CHECK OUT
# =========================================================

elif menu == "🚪 Check-out":

    st.markdown(
        '<div class="main-title">🚪 Check-out</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">Xử lý khách trả phòng</div>',
        unsafe_allow_html=True
    )

    occupied_rooms = rooms[
        rooms["status"] == "Đang ở"
    ]

    if len(occupied_rooms) == 0:

        st.info(
            "Hiện không có khách cần check-out."
        )

    else:

        for _, room in occupied_rooms.iterrows():

            with st.container(border=True):

                col1, col2, col3, col4 = st.columns(
                    [1, 2, 2, 1]
                )

                with col1:
                    st.markdown(
                        f"### 🚪 {room['room_number']}"
                    )

                with col2:
                    st.write(
                        f"👤 **{room['guest_name']}**"
                    )
                    st.write(
                        f"📱 {room['guest_phone'] or '—'}"
                    )

                with col3:
                    st.write(
                        f"Check-in: {room['check_in']}"
                    )
                    st.write(
                        f"Check-out: {room['check_out']}"
                    )

                with col4:

                    if st.button(
                        "Check-out",
                        key=f"checkout_{room['id']}"
                    ):

                        check_out(room["id"])

                        st.success(
                            f"Phòng {room['room_number']} "
                            "đã chuyển sang trạng thái Đang dọn."
                        )

                        st.rerun()


# =========================================================
# ADD ROOM
# =========================================================

elif menu == "➕ Thêm phòng":

    st.markdown(
        '<div class="main-title">➕ Thêm phòng mới</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">Tạo phòng mới trong hệ thống</div>',
        unsafe_allow_html=True
    )

    with st.form("add_room_form"):

        col1, col2 = st.columns(2)

        with col1:

            room_number = st.text_input(
                "🚪 Số phòng *",
                placeholder="Ví dụ: 405"
            )

            room_type = st.selectbox(
                "🛏️ Loại phòng",
                [
                    "Standard",
                    "Superior",
                    "Deluxe",
                    "Suite"
                ]
            )

            floor = st.number_input(
                "🏢 Tầng",
                min_value=1,
                max_value=100,
                value=1
            )

        with col2:

            price = st.number_input(
                "💰 Giá phòng / đêm",
                min_value=0,
                value=800000.0,
                step=100000.0
            )

            status = st.selectbox(
                "📌 Trạng thái ban đầu",
                [
                    "Trống",
                    "Đã đặt",
                    "Đang dọn",
                    "Bảo trì"
                ]
            )

        submit = st.form_submit_button(
            "➕ Thêm phòng",
            use_container_width=True
        )

        if submit:

            if not room_number.strip():

                st.error(
                    "Vui lòng nhập số phòng."
                )

            else:

                success, message = add_room(
                    room_number.strip(),
                    room_type,
                    floor,
                    price,
                    status
                )

                if success:

                    st.success(message)

                    st.rerun()

                else:

                    st.error(message)


# =========================================================
# FOOTER
# =========================================================

st.sidebar.markdown("---")

st.sidebar.caption(
    f"© {datetime.now().year} Hotel PMS"
)
