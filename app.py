import streamlit as st
import streamlit.components.v1 as components
import mysql.connector
import os
import time
import socket
from datetime import date, timedelta
from ai_assistant import tampilkan_chatbot_mengambang

# Konfigurasi Halaman
ikon_web = "img/logo.png" if os.path.exists("img/logo.png") else "🏔️"
st.set_page_config(page_title="Go Adventure - Open Trip & Tiket Wisata", page_icon=ikon_web, layout="wide")
os.makedirs("img", exist_ok=True)

# Kredensial Khusus Admin
ADMIN_USN = "admin"
ADMIN_GMAIL = "admin@goadventure.com"
ADMIN_PASS = "admin123"

# ==========================================
# KUSTOMISASI CSS (SIDEBAR TOP-RIGHT LOGIN, COMPACT & TOMBOL)
# ==========================================
st.markdown("""
<style>
    /* Sembunyikan tombol Deploy bawaan Streamlit */
    .stAppDeployButton, [data-testid="stDeployButton"] {
        display: none !important;
    }

    /* Rapatkan jarak atas halaman utama & tarik konten sidebar ke atas sejajar tombol << */
    .block-container {
        padding-top: 2rem !important;
    }
    section[data-testid="stSidebar"] > div:first-child {
        padding-top: 0.4rem !important;
    }
    section[data-testid="stSidebar"] [data-testid="stSidebarHeader"] {
        padding-bottom: 0 !important;
        margin-bottom: -36px !important;
        position: relative;
        z-index: 10;
        pointer-events: none;
    }
    section[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] {
        pointer-events: auto;
    }
    section[data-testid="stSidebar"] hr {
        margin: 0.45rem 0 !important;
    }

    /* Styling khusus tombol Login / Akun di Sidebar Paling Atas (sejajar logo & <<) */
    section[data-testid="stSidebar"] div[data-testid="stVerticalBlockBorderWrapper"]:has(.sidebar-top-login) div.stButton > button,
    section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"]:has(.sidebar-top-login) div.stButton > button {
        background-color: #FFFFFF !important;
        color: #1B5E20 !important;
        border: 1.5px solid #E8F5E9 !important;
        border-radius: 8px !important;
        padding: 3px 8px !important;
        min-height: 32px !important;
        font-size: 12px !important;
        font-weight: 800 !important;
        text-align: center !important;
        margin-bottom: 0 !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.15);
    }
    section[data-testid="stSidebar"] div[data-testid="stVerticalBlockBorderWrapper"]:has(.sidebar-top-login) div.stButton > button:hover,
    section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"]:has(.sidebar-top-login) div.stButton > button:hover {
        background-color: #E8F5E9 !important;
        color: #1B5E20 !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stVerticalBlockBorderWrapper"]:has(.sidebar-top-login) {
        border: none !important;
        padding: 0 !important;
        margin-bottom: 0 !important;
    }

    /* Styling tombol navigasi menu utama di dalam Sidebar */
    section[data-testid="stSidebar"] div.stButton > button {
        width: 100%;
        border-radius: 10px;
        padding: 10px 14px;
        font-weight: 600;
        text-align: left;
        border: 1px solid #A5D6A7;
        margin-bottom: 2px;
        transition: all 0.2s ease;
    }
    section[data-testid="stSidebar"] div.stButton > button[kind="secondary"] {
        background-color: #FFFFFF;
        color: #1B5E20;
    }
    section[data-testid="stSidebar"] div.stButton > button[kind="secondary"]:hover {
        background-color: #C8E6C9;
        border-color: #2E7D32;
    }
    section[data-testid="stSidebar"] div.stButton > button[kind="primary"] {
        background-color: #2E7D32;
        color: #FFFFFF;
        border: 1px solid #1B5E20;
    }

    /* Kotak input teks berwarna putih agar kontras */
    div[data-testid="stTextInput"] input, div[data-testid="stTextArea"] textarea {
        background-color: #FFFFFF !important;
        color: #1B3B1E !important;
        border: 1px solid #2E7D32 !important;
    }

    /* Tombol Utama Halaman */
    div[data-testid="stAppViewContainer"] div.stButton > button {
        border-radius: 8px;
        padding: 9px 16px;
        font-weight: bold;
    }
    div[data-testid="stAppViewContainer"] div.stButton > button[kind="primary"] {
        background-color: #2E7D32;
        color: white;
        border: none;
    }
    div[data-testid="stAppViewContainer"] div.stButton > button[kind="primary"]:hover {
        background-color: #1B5E20;
        color: white;
    }

    /* Tombol EDIT (Warna Abu-abu) di Kartu Produk Admin */
    div[data-testid="stColumn"]:has(.btn-edit-marker) div.stButton > button {
        background-color: #6C757D !important;
        color: #FFFFFF !important;
        border: none !important;
    }
    div[data-testid="stColumn"]:has(.btn-edit-marker) div.stButton > button:hover {
        background-color: #5A6268 !important;
    }

    /* Tombol HAPUS (Warna Merah) di Kartu Produk Admin */
    div[data-testid="stColumn"]:has(.btn-hapus-marker) div.stButton > button {
        background-color: #DC3545 !important;
        color: #FFFFFF !important;
        border: none !important;
    }
    div[data-testid="stColumn"]:has(.btn-hapus-marker) div.stButton > button:hover {
        background-color: #C82333 !important;
    }

    /* Sticky Bottom Bar ala Shopee */
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.sticky-marker) {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: #FFFFFF;
        border-top: 2px solid #2E7D32 !important;
        border-left: none !important;
        border-right: none !important;
        border-bottom: none !important;
        border-radius: 0 !important;
        padding: 12px 30px !important;
        z-index: 999;
        box-shadow: 0 -4px 12px rgba(0,0,0,0.12);
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# KONEKSI DATABASE & FUNGSI BANTUAN
# ==========================================
def koneksi_db():
    return mysql.connector.connect(
        host="mysql-goadventure-godventure.a.aivencloud.com",
        port=22717,
        user="avnadmin",
        password="AVNS_tP2Gx9VWqkuyR3whVLE",
        database="defaultdb",
        ssl_ca="ca.pem"
    )

def dapatkan_ip_lokal():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "localhost"

def ambil_gambar(path_foto):
    if path_foto and os.path.exists(path_foto):
        return path_foto
    if os.path.exists("img/banner_trip.jpg"):
        return "img/banner_trip.jpg"
    return "https://images.unsplash.com/photo-1501785888041-af3ef285b470?w=800"

# ==========================================
# HANDLER WEBHOOK / SCAN BARCODE QRIS DARI HP
# ==========================================
if "bayar_id" in st.query_params:
    id_transaksi = st.query_params["bayar_id"]
    try:
        conn = koneksi_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE booking SET status = 'Lunas' WHERE id = %s AND status = 'Menunggu Pembayaran'", (id_transaksi,))
        conn.commit()
        cursor.close()
        conn.close()
        
        st.success(f"## ✅ Scan QRIS Berhasil!\nPembayaran untuk Pesanan **#{id_transaksi}** telah diterima otomatis. Silakan kembali ke layar utama!")
        st.balloons()
        st.stop()
    except Exception as e:
        st.error(f"Gagal memproses pembayaran QRIS: {e}")
        st.stop()

# ==========================================
# INISIALISASI SESSION STATE & PEMULIHAN SESI LOGIN OTOMATIS
# ==========================================
if "halaman" not in st.session_state:
    st.session_state.halaman = "Beranda"
if "item_detail_id" not in st.session_state:
    st.session_state.item_detail_id = None
if "edit_item_id" not in st.session_state:
    st.session_state.edit_item_id = None
if "jenis_tambah_baru" not in st.session_state:
    st.session_state.jenis_tambah_baru = "Open Trip"
if "user_login" not in st.session_state:
    st.session_state.user_login = None
if "admin_login" not in st.session_state:
    st.session_state.admin_login = False
if "transaksi_aktif_id" not in st.session_state:
    st.session_state.transaksi_aktif_id = None
if "tampil_lupa_sandi" not in st.session_state:
    st.session_state.tampil_lupa_sandi = False

# Tangani proses hapus sesi dari localStorage jika baru saja klik Logout
if "logout" in st.query_params:
    del st.query_params["logout"]
    components.html("""
    <script>
        localStorage.removeItem('goadv_uid');
        localStorage.removeItem('goadv_role');
    </script>
    """, height=0, width=0)
else:
    # Pulihkan uid atau role dari localStorage browser jika URL dibuka polos
    components.html("""
    <script>
        const doc = window.parent;
        const urlParams = new URLSearchParams(doc.location.search);
        const savedUid = localStorage.getItem('goadv_uid');
        const savedRole = localStorage.getItem('goadv_role');

        if (!urlParams.has('uid') && !urlParams.has('role')) {
            if (savedUid) {
                urlParams.set('uid', savedUid);
                doc.location.search = urlParams.toString();
            } else if (savedRole === 'admin') {
                urlParams.set('role', 'admin');
                doc.location.search = urlParams.toString();
            }
        }
    </script>
    """, height=0, width=0)

if st.session_state.user_login is None and "uid" in st.query_params:
    try:
        conn = koneksi_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE id = %s", (st.query_params["uid"],))
        u_db = cursor.fetchone()
        cursor.close()
        conn.close()
        if u_db:
            st.session_state.user_login = u_db
    except Exception:
        pass

if not st.session_state.admin_login and st.query_params.get("role") == "admin":
    st.session_state.admin_login = True

# ==========================================
# FUNGSI AMBIL DATA KATALOG, RATING & KATEGORI DINAMIS
# ==========================================
def hitung_rating_db(katalog_id):
    try:
        conn = koneksi_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT AVG(skor) as rata, COUNT(*) as jml FROM ulasan WHERE katalog_id = %s", (katalog_id,))
        res = cursor.fetchone()
        cursor.close()
        conn.close()
        if res and res["jml"] and int(res["jml"]) > 0:
            return round(float(res["rata"]), 1), int(res["jml"])
        return 0.0, 0
    except Exception:
        return 0.0, 0

def format_teks_rating(rata_rating, jml_ulasan):
    if jml_ulasan == 0:
        return "Belum ada rating"
    return f"⭐ {rata_rating} ({jml_ulasan} ulasan)"

def ambil_semua_katalog(kategori_filter=None):
    try:
        conn = koneksi_db()
        cursor = conn.cursor(dictionary=True)
        if kategori_filter:
            cursor.execute("SELECT * FROM katalog WHERE kategori = %s ORDER BY id DESC", (kategori_filter,))
        else:
            cursor.execute("SELECT * FROM katalog ORDER BY id DESC")
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return data
    except Exception as e:
        st.error(f"Gagal mengambil data katalog dari MySQL: {e}")
        return []

def ambil_katalog_populer_beranda():
    semua = ambil_semua_katalog()
    for item in semua:
        rata, jml = hitung_rating_db(item["id"])
        item["rata_rating"] = rata
        item["jml_ulasan"] = jml
    semua.sort(key=lambda x: (x["rata_rating"], x["jml_ulasan"]), reverse=True)
    return semua

def ambil_daftar_jenis_alam(kategori_filter=None):
    dasar = ["Semua", "Gunung", "Pantai", "Curug & Camp"]
    try:
        conn = koneksi_db()
        cursor = conn.cursor(dictionary=True)
        if kategori_filter:
            cursor.execute("SELECT DISTINCT jenis_alam FROM katalog WHERE kategori = %s", (kategori_filter,))
        else:
            cursor.execute("SELECT DISTINCT jenis_alam FROM katalog")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        for r in rows:
            val = r["jenis_alam"].strip()
            if val and val not in dasar:
                dasar.append(val)
    except Exception:
        pass
    return dasar

def get_item_aktif():
    if st.session_state.item_detail_id is None:
        return None
    try:
        conn = koneksi_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM katalog WHERE id = %s", (st.session_state.item_detail_id,))
        item = cursor.fetchone()
        cursor.close()
        conn.close()
        return item
    except Exception:
        return None

# ==========================================
# SIDEBAR NAVIGASI (TOMBOL LOGIN DI PALING ATAS KANAN SEBELUM <<)
# ==========================================
with st.sidebar:
    # Baris 1: Logo DVGO diperbesar di kiri & Tombol Login/Akun sejajar <<
    with st.container(border=False):
        st.markdown("<span class='sidebar-top-login'></span>", unsafe_allow_html=True)
        col_logo, col_akun, col_space = st.columns([1.4, 1.3, 0.45])
        
        with col_logo:
            if os.path.exists("img/logo.png"):
                st.image("img/logo.png", width=88)
            else:
                st.markdown("<div style='font-size: 38px; line-height: 1;'>🌲</div>", unsafe_allow_html=True)

        with col_akun:
            if not st.session_state.admin_login and st.session_state.user_login is None:
                if st.button("🔑 Login", key="btn_sidebar_top_login", use_container_width=True):
                    st.session_state.tampil_lupa_sandi = False
                    st.session_state.halaman = "Login"
                    st.rerun()
            elif st.session_state.user_login is not None:
                if st.button("👤 Akun", key="btn_sidebar_top_akun", use_container_width=True):
                    st.session_state.halaman = "Akun Saya"
                    st.rerun()
            elif st.session_state.admin_login:
                if st.button("🛡️ Admin", key="btn_sidebar_top_admin", use_container_width=True):
                    st.session_state.halaman = "Dashboard Admin"
                    st.rerun()

    # Baris 2: Teks GO ADVENTURE dan deskripsi di bawahnya rata tengah (center)
    st.markdown("""
    <div style='text-align: center; margin-top: 4px; margin-bottom: 2px;'>
        <div style='color: #FFFFFF; font-weight: 800; font-size: 18px; letter-spacing: 0.5px; line-height: 1.2;'>GO ADVENTURE</div>
        <p style='color: #E8F5E9; font-size: 12px; margin: 2px 0 0 0; line-height: 1.3;'>Open Trip & Tiket Wisata</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    daftar_menu = [
        ("Beranda", "🏡  Beranda"),
        ("Paket Trip", "🎒  Paket Open Trip"),
        ("Tiket Wisata", "🎟️  Tiket Wisata"),
    ]
    
    if st.session_state.admin_login:
        daftar_menu.append(("Dashboard Admin", "📊  Laporan & Pesanan"))
    
    item_aktif = get_item_aktif()
    for nama_halaman, label_tombol in daftar_menu:
        aktif = (st.session_state.halaman == nama_halaman) or (
            st.session_state.halaman in ["Detail", "Checkout"] and item_aktif and item_aktif["kategori"] == ("Open Trip" if nama_halaman == "Paket Trip" else "Tiket Wisata")
        ) or (
            st.session_state.halaman == "Tambah Produk" and st.session_state.jenis_tambah_baru == ("Open Trip" if nama_halaman == "Paket Trip" else "Tiket Wisata")
        )
        tipe_tombol = "primary" if aktif else "secondary"
        if st.button(label_tombol, key=f"nav_{nama_halaman}", type=tipe_tombol, use_container_width=True):
            st.session_state.halaman = nama_halaman
            st.session_state.item_detail_id = None
            st.session_state.edit_item_id = None
            st.session_state.transaksi_aktif_id = None
            st.rerun()
            
    st.divider()

    # BAGIAN PROFILE DI SIDEBAR (PENGGUNA ATAU ADMIN)
    if st.session_state.admin_login:
        st.markdown("""
        <div style='background-color: rgba(255,255,255,0.15); padding: 10px; border-radius: 10px; text-align: center; margin-bottom: 8px;'>
            <div style='font-size: 28px; line-height: 1.1;'>🛡️</div>
            <div style='color: #FFFFFF; font-weight: 800; font-size: 14px; letter-spacing: 1px; margin-top: 4px;'>ADMIN</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🚪 Logout Admin", key="btn_logout_admin_side", type="secondary", use_container_width=True):
            st.session_state.admin_login = False
            if "role" in st.query_params:
                del st.query_params["role"]
            st.query_params["logout"] = "1"
            st.session_state.halaman = "Beranda"
            st.rerun()

    elif st.session_state.user_login is not None:
        u = st.session_state.user_login
        st.markdown(f"""
        <div style='background-color: rgba(255,255,255,0.15); padding: 10px; border-radius: 10px; text-align: center; margin-bottom: 8px;'>
            <div style='font-size: 28px; line-height: 1.1;'>👤</div>
            <div style='color: #FFFFFF; font-weight: 700; font-size: 14px; margin-top: 4px;'>{u['nama']}</div>
            <div style='color: #E8F5E9; font-size: 11px;'>{u['email']}</div>
        </div>
        """, unsafe_allow_html=True)
        tipe_akun = "primary" if st.session_state.halaman == "Akun Saya" else "secondary"
        if st.button("👤  Profil & Akun Saya", key="nav_akun_saya", type=tipe_akun, use_container_width=True):
            st.session_state.halaman = "Akun Saya"
            st.session_state.item_detail_id = None
            st.rerun()

    st.divider()
    st.markdown("""
    <a href="https://wa.me/+6283105717926?text=Halo%20Admin%20Go%20Adventure%2C%20saya%20ingin%20bertanya%20seputar%20paket%20wisata." target="_blank" style="text-decoration: none;">
        <div style="background-color: #E8F5E9; color: #1B5E20; padding: 12px 14px; border-radius: 10px; border: 1px solid #A5D6A7; font-size: 14px;">
            <div style="font-weight: 800; margin-bottom: 4px;">💬 Hubungi CS (WhatsApp)</div>
            <div style="font-weight: 600;">📞 +6283105717926</div>
            <div style="font-size: 12px; margin-top: 4px; color: #2E7D32;">📍 Bogor, Jawa Barat • <i>Klik untuk chat</i></div>
        </div>
    </a>
    """, unsafe_allow_html=True)

# ==========================================
# NOTIFIKASI PEMBATALAN ADMIN DI PAGE PENGGUNA
# ==========================================
if st.session_state.user_login is not None:
    try:
        conn = koneksi_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, paket_wisata, alasan_batal FROM booking WHERE email = %s AND status = 'Dibatalkan Admin' ORDER BY id DESC",
            (st.session_state.user_login["email"],)
        )
        daftar_batal = cursor.fetchall()
        cursor.close()
        conn.close()
        for b in daftar_batal:
            alasan_teks = b["alasan_batal"] if b["alasan_batal"] else "alasan operasional."
            st.error(f"🚨 **Pemberitahuan Pesanan #{b['id']} ({b['paket_wisata']}):** admin membatalkan pesanan anda karena {alasan_teks}")
    except Exception:
        pass

# ==========================================
# FUNGSI TAMPILAN KARTU KATALOG (EDIT ABU & HAPUS MERAH BAGI ADMIN)
# ==========================================
def render_grid_kartu(items, kunci_unik):
    if not items:
        st.warning("maaf kami belum menyediakan layanan ini")
        return

    for i in range(0, len(items), 2):
        cols = st.columns(2)
        for j in range(2):
            if i + j < len(items):
                item = items[i + j]
                rata_rating, jml_ulasan = hitung_rating_db(item["id"])
                teks_rating = format_teks_rating(rata_rating, jml_ulasan)
                
                with cols[j]:
                    with st.container(border=True):
                        st.image(ambil_gambar(item["foto"]), use_container_width=True)
                        st.caption(f"🏷️ **{item['kategori']}** • **{item['jenis_alam']}**  |  📍 {item['kota_pulau']}, {item['provinsi']}")
                        st.markdown(f"### {item['nama']}")
                        
                        c_harga, c_rating = st.columns(2)
                        with c_harga:
                            st.markdown(f"<h4 style='color: #2E7D32; margin: 0;'>Rp {item['harga']:,}</h4>", unsafe_allow_html=True)
                        with c_rating:
                            st.markdown(f"<p style='text-align: right; margin: 4px 0 0 0; font-weight: bold;'>{teks_rating}</p>", unsafe_allow_html=True)
                        
                        st.write(item["deskripsi_singkat"])
                        
                        if st.button("🔍 Lihat Detail", key=f"btn_{kunci_unik}_{item['id']}", type="primary", use_container_width=True):
                            st.session_state.item_detail_id = item["id"]
                            st.session_state.halaman = "Detail"
                            st.session_state.transaksi_aktif_id = None
                            st.rerun()

                        # Tombol EDIT (Abu-abu) & HAPUS (Merah) di Masing-Masing Card bagi Admin
                        if st.session_state.admin_login:
                            col_ed, col_del = st.columns(2)
                            with col_ed:
                                st.markdown("<span class='btn-edit-marker'></span>", unsafe_allow_html=True)
                                if st.button("✏️ Edit", key=f"edit_card_{kunci_unik}_{item['id']}", use_container_width=True):
                                    if st.session_state.edit_item_id == item["id"]:
                                        st.session_state.edit_item_id = None
                                    else:
                                        st.session_state.edit_item_id = item["id"]
                                    st.rerun()
                            with col_del:
                                st.markdown("<span class='btn-hapus-marker'></span>", unsafe_allow_html=True)
                                if st.button("🗑️ Hapus", key=f"del_card_{kunci_unik}_{item['id']}", use_container_width=True):
                                    try:
                                        conn = koneksi_db()
                                        cursor = conn.cursor()
                                        cursor.execute("DELETE FROM katalog WHERE id = %s", (item["id"],))
                                        cursor.execute("DELETE FROM ulasan WHERE katalog_id = %s", (item["id"],))
                                        conn.commit()
                                        cursor.close()
                                        conn.close()
                                        st.warning(f"Produk '{item['nama']}' berhasil dihapus!")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Gagal menghapus: {e}")

                            if st.session_state.edit_item_id == item["id"]:
                                st.divider()
                                st.markdown(f"**✏️ Edit Produk: {item['nama']}**")
                                e_nama = st.text_input("Nama Destinasi", value=item["nama"], key=f"enm_{kunci_unik}_{item['id']}")
                                e_jenis = st.text_input("Kategori Katalog", value=item["jenis_alam"], key=f"ejn_{kunci_unik}_{item['id']}")
                                e_harga = st.number_input("Harga (Rp)", min_value=5000, step=5000, value=int(item["harga"]), key=f"ehg_{kunci_unik}_{item['id']}")
                                e_prov = st.text_input("Provinsi", value=item["provinsi"], key=f"epr_{kunci_unik}_{item['id']}")
                                e_kota = st.text_input("Kota / Pulau", value=item["kota_pulau"], key=f"ekt_{kunci_unik}_{item['id']}")
                                e_alamat = st.text_area("Alamat Lengkap", value=item["alamat_lengkap"], key=f"eal_{kunci_unik}_{item['id']}", height=70)
                                e_gmaps = st.text_input("Link Google Maps (Opsional)", value=item.get("link_gmaps") or "", placeholder="https://maps.app.goo.gl/...", key=f"egm_{kunci_unik}_{item['id']}")
                                e_jadwal = st.text_input("Jadwal", value=item["jadwal"], key=f"ejd_{kunci_unik}_{item['id']}")
                                e_desks = st.text_input("Deskripsi Singkat", value=item["deskripsi_singkat"], key=f"eds_{kunci_unik}_{item['id']}")
                                e_deskl = st.text_area("Deskripsi Lengkap", value=item["deskripsi_lengkap"], key=f"edl_{kunci_unik}_{item['id']}")
                                e_fas = st.text_area("Fasilitas", value=item["fasilitas"], key=f"efs_{kunci_unik}_{item['id']}")
                                e_foto_baru = st.file_uploader("Ganti Foto (Opsional)", type=["jpg", "jpeg", "png"], key=f"eft_{kunci_unik}_{item['id']}")

                                c_sv, c_bt = st.columns(2)
                                with c_sv:
                                    if st.button("💾 Simpan", key=f"sv_ed_{kunci_unik}_{item['id']}", type="primary", use_container_width=True):
                                        path_foto_fix = item["foto"]
                                        if e_foto_baru is not None:
                                            path_foto_fix = f"img/{int(time.time())}_{e_foto_baru.name}"
                                            with open(path_foto_fix, "wb") as f:
                                                f.write(e_foto_baru.getbuffer())
                                        try:
                                            conn = koneksi_db()
                                            cursor = conn.cursor()
                                            if "link_gmaps" in item:
                                                sql_up = """UPDATE katalog SET jenis_alam=%s, nama=%s, harga=%s, provinsi=%s, 
                                                            kota_pulau=%s, alamat_lengkap=%s, link_gmaps=%s, jadwal=%s, foto=%s, deskripsi_singkat=%s, 
                                                            deskripsi_lengkap=%s, fasilitas=%s WHERE id=%s"""
                                                val_up = (
                                                    e_jenis.strip(), e_nama.strip(), e_harga, e_prov.strip(),
                                                    e_kota.strip(), e_alamat.strip(), e_gmaps.strip(), e_jadwal.strip(), path_foto_fix,
                                                    e_desks.strip(), e_deskl.strip(), e_fas.strip(), item["id"]
                                                )
                                            else:
                                                sql_up = """UPDATE katalog SET jenis_alam=%s, nama=%s, harga=%s, provinsi=%s, 
                                                            kota_pulau=%s, alamat_lengkap=%s, jadwal=%s, foto=%s, deskripsi_singkat=%s, 
                                                            deskripsi_lengkap=%s, fasilitas=%s WHERE id=%s"""
                                                val_up = (
                                                    e_jenis.strip(), e_nama.strip(), e_harga, e_prov.strip(),
                                                    e_kota.strip(), e_alamat.strip(), e_jadwal.strip(), path_foto_fix,
                                                    e_desks.strip(), e_deskl.strip(), e_fas.strip(), item["id"]
                                                )
                                            cursor.execute(sql_up, val_up)
                                            conn.commit()
                                            cursor.close()
                                            conn.close()
                                            st.session_state.edit_item_id = None
                                            st.success("Perubahan disimpan!")
                                            st.rerun()
                                        except Exception as e:
                                            st.error(f"Gagal update: {e}")
                                with c_bt:
                                    if st.button("Batal", key=f"bt_ed_{kunci_unik}_{item['id']}", use_container_width=True):
                                        st.session_state.edit_item_id = None
                                        st.rerun()

def tampilkan_katalog_lengkap(kategori_filter, kunci_unik):
    daftar_kategori_alam = ambil_daftar_jenis_alam(kategori_filter)
    
    col_search, col_kat = st.columns([1.3, 1.7])
    with col_search:
        kata_kunci = st.text_input(
            "🔍 Cari Destinasi, Kota, atau Provinsi:", 
            placeholder="Ketik nama tempat, kota/pulau, atau provinsi...", 
            key=f"search_{kunci_unik}"
        )
    with col_kat:
        pilih_jenis = st.radio(
            "📂 Kategori Katalog:",
            daftar_kategori_alam,
            horizontal=True,
            key=f"kat_{kunci_unik}"
        )

    st.divider()

    items = ambil_semua_katalog(kategori_filter)

    if pilih_jenis != "Semua":
        items = [item for item in items if item["jenis_alam"].lower() == pilih_jenis.lower()]

    if kata_kunci.strip() != "":
        q = kata_kunci.strip().lower()
        items = [
            item for item in items 
            if q in item["nama"].lower() 
            or q in item["kota_pulau"].lower() 
            or q in item["provinsi"].lower()
            or q in item["alamat_lengkap"].lower()
            or q in item["jenis_alam"].lower()
        ]

    render_grid_kartu(items, kunci_unik)

selected = st.session_state.halaman

# ==========================================
# 0. HALAMAN LOGIN (TANPA BOCORAN KREDENSIAL ADMIN)
# ==========================================
if selected == "Login":
    if st.button("⬅️ Kembali"):
        st.session_state.halaman = "Detail" if get_item_aktif() else "Beranda"
        st.rerun()
        
    st.subheader("🔑 Login & Pendaftaran Akun Go Adventure")
    tab_masuk, tab_daftar, tab_admin = st.tabs(["🔓 Masuk Akun Pengguna", "📝 Daftar Akun Baru", "🛡️ Login Admin"])
    
    with tab_masuk:
        with st.container(border=True):
            in_email = st.text_input("Alamat Gmail", placeholder="contoh@gmail.com", key="login_email")
            in_pass = st.text_input("Kata Sandi", type="password", placeholder="Masukkan kata sandi...", key="login_pass")
            if st.button("✅ Masuk ke Akun", type="primary", use_container_width=True):
                if not in_email.strip() or not in_pass.strip():
                    st.error("Gmail dan kata sandi wajib diisi!")
                else:
                    try:
                        conn = koneksi_db()
                        cursor = conn.cursor(dictionary=True)
                        cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (in_email.strip().lower(), in_pass.strip()))
                        user_db = cursor.fetchone()
                        cursor.close()
                        conn.close()
                        
                        if user_db:
                            st.session_state.admin_login = False
                            if "role" in st.query_params:
                                del st.query_params["role"]
                            st.session_state.user_login = user_db
                            st.query_params["uid"] = str(user_db["id"])
                            components.html(f"<script>localStorage.setItem('goadv_uid', '{user_db['id']}');</script>", height=0, width=0)
                            st.session_state.halaman = "Checkout" if get_item_aktif() else "Beranda"
                            st.rerun()
                        else:
                            st.error("Gmail atau Kata Sandi salah!")
                    except Exception as e:
                        st.error(f"Koneksi database gagal: {e}")

        st.write("")
        if st.button("❓ Lupa Sandi? Klik di sini untuk mereset sandi", key="btn_toggle_lupa"):
            st.session_state.tampil_lupa_sandi = not st.session_state.tampil_lupa_sandi

        if st.session_state.tampil_lupa_sandi:
            with st.container(border=True):
                st.markdown("#### 🔄 Reset Kata Sandi")
                st.info("Masukkan **Gmail** atau **Nomor WhatsApp** yang terdaftar pada akunmu terlebih dahulu.")
                f_kontak = st.text_input("Masukkan Gmail atau Nomor WhatsApp Terdaftar:", placeholder="contoh@gmail.com atau 081234567890", key="lupa_kontak")
                f_pass_baru = st.text_input("Kata Sandi Baru (Minimal 6 karakter):", type="password", key="lupa_pass_baru")
                if st.button("Simpan Sandi Baru", key="btn_simpan_lupa", type="primary"):
                    if not f_kontak.strip() or len(f_pass_baru.strip()) < 6:
                        st.error("Harap masukkan Gmail/WA terdaftar dan sandi baru minimal 6 karakter!")
                    else:
                        try:
                            conn = koneksi_db()
                            cursor = conn.cursor(dictionary=True)
                            cursor.execute(
                                "SELECT id FROM users WHERE email = %s OR no_hp = %s",
                                (f_kontak.strip().lower(), f_kontak.strip())
                            )
                            u_found = cursor.fetchone()
                            if u_found:
                                cursor.execute("UPDATE users SET password = %s WHERE id = %s", (f_pass_baru.strip(), u_found["id"]))
                                conn.commit()
                                st.success("✅ Kata sandi berhasil diperbarui! Silakan masuk menggunakan sandi baru di atas.")
                                st.session_state.tampil_lupa_sandi = False
                            else:
                                st.error("Gmail atau Nomor WhatsApp tersebut tidak ditemukan dalam database!")
                            cursor.close()
                            conn.close()
                        except Exception as e:
                            st.error(f"Gagal memproses: {e}")

    with tab_daftar:
        with st.container(border=True):
            d_nama = st.text_input("Nama Lengkap", placeholder="Contoh: Budi Santoso")
            d_email = st.text_input("Alamat Gmail Aktif", placeholder="Contoh: budisantoso@gmail.com")
            d_hp = st.text_input("Nomor HP / WhatsApp Aktif", placeholder="Contoh: 081234567890")
            d_pass = st.text_input("Buat Kata Sandi", type="password", placeholder="Minimal 6 karakter...")
            
            if st.button("🚀 Daftar & Masuk Sekarang", type="primary", use_container_width=True):
                if not d_nama.strip() or not d_email.strip() or not d_hp.strip() or not d_pass.strip():
                    st.error("Semua kolom wajib diisi!")
                elif "@gmail.com" not in d_email.lower():
                    st.error("Gunakan alamat Gmail yang valid (@gmail.com)!")
                elif not d_hp.isdigit() or len(d_hp) < 10:
                    st.error("Nomor HP harus berupa angka minimal 10 digit!")
                elif len(d_pass) < 6:
                    st.error("Kata sandi minimal 6 karakter!")
                else:
                    try:
                        conn = koneksi_db()
                        cursor = conn.cursor(dictionary=True)
                        cursor.execute("SELECT id FROM users WHERE email = %s", (d_email.strip().lower(),))
                        if cursor.fetchone():
                            st.error("Gmail tersebut sudah terdaftar! Silakan masuk melalui tab Masuk Akun Pengguna.")
                        else:
                            cursor.execute(
                                "INSERT INTO users (nama, email, no_hp, password) VALUES (%s, %s, %s, %s)",
                                (d_nama.strip(), d_email.strip().lower(), d_hp.strip(), d_pass.strip())
                            )
                            conn.commit()
                            uid_baru = cursor.lastrowid
                            st.session_state.user_login = {
                                "id": uid_baru,
                                "nama": d_nama.strip(),
                                "email": d_email.strip().lower(),
                                "no_hp": d_hp.strip(),
                                "password": d_pass.strip()
                            }
                            st.query_params["uid"] = str(uid_baru)
                            components.html(f"<script>localStorage.setItem('goadv_uid', '{uid_baru}');</script>", height=0, width=0)
                            st.session_state.halaman = "Checkout" if get_item_aktif() else "Beranda"
                            st.rerun()
                        cursor.close()
                        conn.close()
                    except Exception as e:
                        st.error(f"Gagal mendaftar: {e}")

    with tab_admin:
        st.warning("Area khusus Administrator Go Adventure.")
        with st.container(border=True):
            adm_user = st.text_input("Username Admin", placeholder="Masukkan username admin...")
            adm_gmail = st.text_input("Gmail Khusus Admin", placeholder="Masukkan gmail admin...")
            adm_pass = st.text_input("Password Khusus Admin", type="password", placeholder="Masukkan password khusus admin...")
            
            if st.button("🔓 Masuk sebagai Admin", type="primary", use_container_width=True):
                if adm_user.strip() == ADMIN_USN and adm_gmail.strip().lower() == ADMIN_GMAIL and adm_pass.strip() == ADMIN_PASS:
                    st.session_state.user_login = None
                    if "uid" in st.query_params:
                        del st.query_params["uid"]
                    st.session_state.admin_login = True
                    st.query_params["role"] = "admin"
                    components.html("<script>localStorage.setItem('goadv_role', 'admin');</script>", height=0, width=0)
                    st.session_state.halaman = "Beranda"
                    st.rerun()
                else:
                    st.error("❌ Username, Gmail, atau Password Khusus Admin salah!")

# ==========================================
# 1. MENU BERANDA (PRODUK BERDASARKAN KALKULASI RATING & ULASAN)
# ==========================================
elif selected == "Beranda":
    st.subheader("🌿 Selamat Datang di Go Adventure!")
    st.image(ambil_gambar("img/banner_trip.jpg"), use_container_width=True)
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.info("🎒 **Paket Open Trip (Full Fasilitas + Tour Guide)**\n\nSudah termasuk transportasi, pemandu wisata (*Tour Guide*), makan, homestay, dan dokumentasi.")
    with col_b:
        st.success("🎟️ **Tiket Wisata Mandiri (Tiket Saja)**\n\nCocok untuk kamu yang berangkat sendiri/keluarga dan hanya membutuhkan tiket masuk destinasi.")
    
    st.divider()
    st.subheader("🔥 Rekomendasi Teratas (Berdasarkan Rating & Ulasan Pengunjung)")
    items_populer = ambil_katalog_populer_beranda()
    render_grid_kartu(items_populer, "beranda")

# ==========================================
# 2. MENU PAKET OPEN TRIP (TOMBOL TAMBAH PINDAH KE PAGE BARU)
# ==========================================
elif selected == "Paket Trip":
    col_h1, col_h2 = st.columns([3, 1.2])
    with col_h1:
        st.subheader("🎒 Katalog Paket Open Trip (Termasuk Tour Guide & Fasilitas)")
    with col_h2:
        if st.session_state.admin_login:
            if st.button("➕ Tambah Open Trip Baru", type="primary", use_container_width=True):
                st.session_state.jenis_tambah_baru = "Open Trip"
                st.session_state.halaman = "Tambah Produk"
                st.rerun()
                
    tampilkan_katalog_lengkap("Open Trip", "opentrip")

# ==========================================
# 3. MENU TIKET WISATA (TOMBOL TAMBAH PINDAH KE PAGE BARU)
# ==========================================
elif selected == "Tiket Wisata":
    col_h1, col_h2 = st.columns([3, 1.2])
    with col_h1:
        st.subheader("🎟️ Katalog Tiket Masuk Destinasi (Tanpa Tour Guide)")
    with col_h2:
        if st.session_state.admin_login:
            if st.button("➕ Tambah Tiket Wisata Baru", type="primary", use_container_width=True):
                st.session_state.jenis_tambah_baru = "Tiket Wisata"
                st.session_state.halaman = "Tambah Produk"
                st.rerun()
                
    tampilkan_katalog_lengkap("Tiket Wisata", "tiket")

# ==========================================
# 3B. PAGE BARU: TAMBAH PAKET OPEN TRIP / TIKET WISATA (KHUSUS ADMIN)
# ==========================================
elif selected == "Tambah Produk":
    if not st.session_state.admin_login:
        st.session_state.halaman = "Beranda"
        st.rerun()

    jenis_layanan_tetap = st.session_state.jenis_tambah_baru
    halaman_asal = "Paket Trip" if jenis_layanan_tetap == "Open Trip" else "Tiket Wisata"

    if st.button(f"⬅️ Kembali ke Katalog {jenis_layanan_tetap}"):
        st.session_state.halaman = halaman_asal
        st.rerun()

    st.subheader(f"➕ Tambah {jenis_layanan_tetap} Baru")
    st.write(f"Lengkapi seluruh informasi destinasi di bawah ini untuk mempublikasikan **{jenis_layanan_tetap}** baru:")

    with st.container(border=True):
        col_adm1, col_adm2 = st.columns(2)
        with col_adm1:
            opsi_kat = ["Gunung", "Pantai", "Curug & Camp", "Lainnya"]
            pilih_kat_admin = st.selectbox("Kategori Katalog", opsi_kat)
            if pilih_kat_admin == "Lainnya":
                a_jenis_alam = st.text_input("Tuliskan Nama Kategori Baru:", placeholder="Contoh: Danau & Bukit, Goa, Wisata Sejarah...")
            else:
                a_jenis_alam = pilih_kat_admin
                
            a_nama = st.text_input(f"Nama {jenis_layanan_tetap}", placeholder="Contoh: Open Trip Gunung Prau (2H1M)")
            a_harga = st.number_input("Harga per Orang (Rp)", min_value=5000, step=5000, value=100000)
            a_jadwal = st.text_input("Jadwal / Jam Operasional", placeholder="Contoh: Setiap Sabtu - Minggu")

        with col_adm2:
            a_provinsi = st.text_input("Provinsi", placeholder="Contoh: Jawa Tengah")
            a_kota_pulau = st.text_input("Kota / Kabupaten / Pulau", placeholder="Contoh: Kabupaten Wonosobo / Pulau Pari")
            a_alamat = st.text_area("Alamat Lengkap Destinasi", placeholder="Contoh: Jl. Dieng Km 27, Kejajar, Wonosobo, Jawa Tengah", height=100)
            a_gmaps = st.text_input("Link Google Maps (Opsional)", placeholder="Tempel link dari Google Maps (https://maps.app.goo.gl/...)")
            a_foto = st.file_uploader("Upload Foto Tempat Wisata (JPG/PNG)", type=["jpg", "jpeg", "png"])

        a_desk_singkat = st.text_input("Deskripsi Singkat (Tampil di Kartu Katalog)", placeholder="Ringkasan singkat 1-2 kalimat...")
        a_desk_lengkap = st.text_area("Deskripsi Lengkap Tempat Wisata", placeholder="Penjelasan lengkap mengenai destinasi...")
        a_fasilitas = st.text_area("Fasilitas yang Didapat (Pisahkan tiap poin dengan Enter)", value="✅ Tiket Masuk Wisata\n✅ Asuransi Pengunjung\n✅ Dokumentasi")

        if st.button(f"💾 Simpan & Publikasikan {jenis_layanan_tetap}", type="primary", use_container_width=True):
            if not a_nama.strip() or not a_jenis_alam.strip() or not a_provinsi.strip() or not a_kota_pulau.strip() or not a_alamat.strip() or not a_desk_singkat.strip():
                st.error("Semua kolom (Nama, Kategori, Provinsi, Kota/Pulau, Alamat Lengkap, dan Deskripsi Singkat) wajib diisi!")
            else:
                if a_foto is not None:
                    nama_file_foto = f"img/{int(time.time())}_{a_foto.name}"
                    with open(nama_file_foto, "wb") as f:
                        f.write(a_foto.getbuffer())
                else:
                    nama_file_foto = "img/banner_trip.jpg"

                try:
                    conn = koneksi_db()
                    cursor = conn.cursor(dictionary=True)
                    cursor.execute("SHOW COLUMNS FROM katalog LIKE 'link_gmaps'")
                    punya_kolom_gmaps = cursor.fetchone() is not None
                    cursor.close()

                    cursor = conn.cursor()
                    if punya_kolom_gmaps:
                        sql = """INSERT INTO katalog (kategori, jenis_alam, nama, harga, terjual, provinsi, kota_pulau, alamat_lengkap, link_gmaps, jadwal, foto, deskripsi_singkat, deskripsi_lengkap, fasilitas)
                                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                        val = (
                            jenis_layanan_tetap, a_jenis_alam.strip(), a_nama.strip(), a_harga, "Baru Tersedia",
                            a_provinsi.strip(), a_kota_pulau.strip(), a_alamat.strip(), a_gmaps.strip(), a_jadwal.strip(), nama_file_foto,
                            a_desk_singkat.strip(), a_desk_lengkap.strip(), a_fasilitas.strip()
                        )
                    else:
                        sql = """INSERT INTO katalog (kategori, jenis_alam, nama, harga, terjual, provinsi, kota_pulau, alamat_lengkap, jadwal, foto, deskripsi_singkat, deskripsi_lengkap, fasilitas)
                                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                        val = (
                            jenis_layanan_tetap, a_jenis_alam.strip(), a_nama.strip(), a_harga, "Baru Tersedia",
                            a_provinsi.strip(), a_kota_pulau.strip(), a_alamat.strip(), a_jadwal.strip(), nama_file_foto,
                            a_desk_singkat.strip(), a_desk_lengkap.strip(), a_fasilitas.strip()
                        )
                    cursor.execute(sql, val)
                    conn.commit()
                    cursor.close()
                    conn.close()
                    st.success(f"**{a_nama}** berhasil dipublikasikan!")
                    st.session_state.halaman = halaman_asal
                    st.rerun()
                except Exception as e:
                    st.error(f"Gagal menyimpan ke database: {e}")

# ==========================================
# 4. HALAMAN DETAIL PRODUK (ADMIN TIDAK BISA MEMESAN)
# ==========================================
elif selected == "Detail" and get_item_aktif() is not None:
    item = get_item_aktif()
    rata_rating, jml_ulasan = hitung_rating_db(item["id"])
    teks_rating = format_teks_rating(rata_rating, jml_ulasan)
    
    if st.button("⬅️ Kembali ke Daftar Katalog"):
        st.session_state.halaman = "Paket Trip" if item["kategori"] == "Open Trip" else "Tiket Wisata"
        st.session_state.item_detail_id = None
        st.rerun()
        
    st.divider()
    
    col_img, col_info = st.columns([1.2, 1.5])
    with col_img:
        st.image(ambil_gambar(item["foto"]), use_container_width=True)
    with col_info:
        badge_warna = "#E8F5E9" if item["kategori"] == "Tiket Wisata" else "#E3F2FD"
        badge_teks = "🎟️ Tiket Masuk Mandiri (Berlaku 30 Hari)" if item["kategori"] == "Tiket Wisata" else "🎒 Paket Open Trip (Sesuai Tanggal Reservasi)"
        st.markdown(f"<span style='background-color: {badge_warna}; color: #1B5E20; padding: 5px 12px; border-radius: 20px; font-weight: bold; font-size: 13px;'>{badge_teks} • {item['jenis_alam']}</span>", unsafe_allow_html=True)
        
        st.title(item["nama"])
        st.markdown(f"### {teks_rating}  &nbsp;|&nbsp;  📦 {item['terjual']}")
        st.markdown(f"<h2 style='color: #2E7D32;'>Rp {item['harga']:,} <span style='font-size: 16px; color: gray;'>/ orang</span></h2>", unsafe_allow_html=True)
        
        st.write(f"**🗺️ Wilayah:** {item['kota_pulau']}, Provinsi {item['provinsi']}")
        st.write(f"**📍 Alamat Lengkap:** {item['alamat_lengkap']}")
        
        url_maps = item.get("link_gmaps") if item.get("link_gmaps") and item.get("link_gmaps").strip() else f"https://www.google.com/maps/search/?api=1&query={item['nama'].replace(' ', '+')}+{item['kota_pulau'].replace(' ', '+')}"
        st.link_button("🗺️ Buka Lokasi & Lihat Ulasan di Google Maps", url_maps)
        
        st.write(f"**🕒 Jadwal / Jam Operasional:** {item['jadwal']}")
        
        if item["kategori"] == "Open Trip":
            st.info("🎁 **Promo Rombongan:** Pesan untuk 5 orang atau lebih, otomatis mendapat **Diskon Rp 100.000**!")
        else:
            st.info("📅 **Masa Berlaku Tiket:** Tiket masuk berlaku fleksibel selama **30 hari** sejak tanggal pembelian.")

    st.divider()
    
    col_desk, col_fas = st.columns([1.4, 1.1])
    with col_desk:
        st.subheader("📖 Deskripsi Tempat Wisata")
        st.write(item["deskripsi_lengkap"])
    with col_fas:
        st.subheader("✨ Fasilitas yang Didapat")
        with st.container(border=True):
            for baris in item["fasilitas"].split("\n"):
                if baris.strip():
                    st.write(baris)

    st.divider()

    st.subheader(f"💬 Rating & Ulasan Pelanggan ({teks_rating})")
    try:
        conn = koneksi_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM ulasan WHERE katalog_id = %s ORDER BY id DESC", (item["id"],))
        daftar_ulasan = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if not daftar_ulasan:
            st.caption("Belum ada rating maupun ulasan untuk tempat ini.")
        for ulasan in daftar_ulasan:
            bintang_visual = "⭐" * ulasan["skor"]
            with st.container(border=True):
                st.write(f"**{ulasan['user_nama']}** — {bintang_visual} ({ulasan['skor']}/5)")
                st.write(f'"{ulasan["komen"]}"')
    except Exception as e:
        st.error(f"Gagal memuat ulasan: {e}")

    if not st.session_state.admin_login:
        with st.expander("✍️ Tulis Ulasan & Beri Rating untuk Tempat Ini"):
            u_nama = st.text_input("Nama Kamu", value=st.session_state.user_login["nama"] if st.session_state.user_login else "", key="u_nama")
            pilihan_skor = st.selectbox("Pilih Rating Bintang", [5, 4, 3, 2, 1], format_func=lambda x: f"{'⭐' * x} ({x} Bintang)", key="u_skor")
            u_komen = st.text_area("Tulis pengalamanmu di sini...", key="u_komen")
            if st.button("Kirim Ulasan & Rating", type="primary"):
                if u_nama.strip() and u_komen.strip():
                    try:
                        conn = koneksi_db()
                        cursor = conn.cursor()
                        cursor.execute("INSERT INTO ulasan (katalog_id, user_nama, skor, komen) VALUES (%s, %s, %s, %s)", (item["id"], u_nama.strip(), pilihan_skor, u_komen.strip()))
                        conn.commit()
                        cursor.close()
                        conn.close()
                        st.success("Terima kasih! Rating telah diakumulasi ke database.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Gagal menyimpan ulasan: {e}")
                else:
                    st.warning("Isi nama dan komentar ulasan terlebih dahulu!")

    if not st.session_state.admin_login:
        st.markdown("<div style='height: 95px;'></div>", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown("<span class='sticky-marker'></span>", unsafe_allow_html=True)
            col_bawah_kiri, col_bawah_kanan = st.columns([3, 1.2])
            with col_bawah_kiri:
                st.markdown(f"**{item['nama']}**  <br><span style='font-size: 20px; font-weight: bold; color: #2E7D32;'>Rp {item['harga']:,}</span> <span style='color: gray; font-size: 13px;'>/ orang</span>", unsafe_allow_html=True)
            with col_bawah_kanan:
                if st.button("🛒 Pesan Sekarang", key="btn_sticky_pesan", type="primary", use_container_width=True):
                    if st.session_state.user_login is None:
                        st.session_state.halaman = "Login"
                    else:
                        st.session_state.transaksi_aktif_id = None
                        st.session_state.halaman = "Checkout"
                    st.rerun()
    else:
        st.info("ℹ️ Anda sedang masuk sebagai **Admin**. Fitur pemesanan hanya tersedia untuk akun Pengguna.")

# ==========================================
# 5. HALAMAN CHECKOUT TERPISAH (AUTO-HIDE QRIS SAAT DI-SCAN)
# ==========================================
elif selected == "Checkout" and get_item_aktif() is not None:
    if st.session_state.admin_login:
        st.error("Admin tidak diperbolehkan melakukan pemesanan.")
        st.stop()
    if st.session_state.user_login is None:
        st.session_state.halaman = "Login"
        st.rerun()

    item = get_item_aktif()
    user_aktif = st.session_state.user_login
    
    if st.button("⬅️ Kembali ke Detail Tempat Wisata"):
        st.session_state.transaksi_aktif_id = None
        st.session_state.halaman = "Detail"
        st.rerun()
        
    st.subheader("🧾 Halaman Pemesanan & Pembayaran")
    
    with st.container(border=True):
        c_foto, c_ringkasan = st.columns([1, 2])
        with c_foto:
            st.image(ambil_gambar(item["foto"]), use_container_width=True)
        with c_ringkasan:
            st.markdown(f"### {item['nama']}")
            st.markdown(f"<h3 style='color: #2E7D32; margin: 0;'>Rp {item['harga']:,} <span style='font-size: 14px; color: gray;'>/ orang</span></h3>", unsafe_allow_html=True)
            st.write("")
            st.write(item["deskripsi_singkat"])
            st.caption(f"📍 {item['alamat_lengkap']} ({item['kota_pulau']}, {item['provinsi']})")

    st.divider()

    status_pembayaran = "belum_konfirmasi"
    if st.session_state.transaksi_aktif_id is not None:
        try:
            conn = koneksi_db()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM booking WHERE id = %s", (st.session_state.transaksi_aktif_id,))
            data_transaksi = cursor.fetchone()
            cursor.close()
            conn.close()
            if data_transaksi:
                status_pembayaran = data_transaksi["status"]
        except Exception as e:
            st.error(f"Koneksi database terputus: {e}")

    col_form, col_qris = st.columns([1.3, 1.1])
    tgl_hari_ini = date.today()
    sudah_konfirmasi = (st.session_state.transaksi_aktif_id is not None)
    
    with col_form:
        st.subheader("📝 Data Pemesanan")
        with st.container(border=True):
            nama_pemesan = st.text_input("Nama Lengkap Pemesan", value=user_aktif["nama"], disabled=sudah_konfirmasi)
            c_kontak1, c_kontak2 = st.columns(2)
            with c_kontak1:
                st.text_input("Gmail Konfirmasi", value=user_aktif["email"], disabled=True)
            with c_kontak2:
                st.text_input("No. HP / WhatsApp (Untuk Konfirmasi Tim)", value=user_aktif["no_hp"], disabled=True)
            
            if item["kategori"] == "Tiket Wisata":
                tgl_expired = tgl_hari_ini + timedelta(days=30)
                st.date_input("Tanggal Pembelian", value=tgl_hari_ini, disabled=True)
                st.info(f"⏳ **Masa Berlaku Tiket (30 Hari):** Berlaku mulai **{tgl_hari_ini}** sampai **{tgl_expired}**")
                teks_masa_berlaku = f"30 Hari ({tgl_hari_ini} s.d. {tgl_expired})"
            else:
                tgl_reservasi = st.date_input("Tanggal Reservasi Keberangkatan", min_value=tgl_hari_ini, disabled=sudah_konfirmasi)
                st.info(f"📅 **Jadwal Keberangkatan Open Trip:** Sesuai tanggal reservasi (**{tgl_reservasi}**)")
                teks_masa_berlaku = f"Tgl Berangkat: {tgl_reservasi}"
                
            jumlah_orang = st.number_input("Jumlah Pesanan (Orang / Tiket)", min_value=1, max_value=50, value=1, disabled=sudah_konfirmasi)
            st.selectbox("Metode Pembayaran", ["QRIS"], disabled=sudah_konfirmasi)
            
            subtotal = item["harga"] * jumlah_orang
            diskon = 100000 if (item["kategori"] == "Open Trip" and jumlah_orang >= 5) else 0
            total_bayar = subtotal - diskon
            
            st.divider()
            st.write(f"Subtotal ({jumlah_orang} x Rp {item['harga']:,}): **Rp {subtotal:,}**")
            if diskon > 0:
                st.success(f"🎁 Diskon Rombongan (≥ 5 org): **-Rp {diskon:,}**")
            st.markdown(f"<h3 style='color: #2E7D32;'>Total Pembayaran: Rp {total_bayar:,}</h3>", unsafe_allow_html=True)

            if not sudah_konfirmasi:
                if st.button("🧾 Konfirmasi Pesanan & Munculkan QRIS", type="primary", use_container_width=True):
                    if nama_pemesan.strip() == "":
                        st.error("Nama pemesan wajib diisi!")
                    else:
                        try:
                            conn = koneksi_db()
                            cursor = conn.cursor()
                            jenis_simpan = "Paket Open Trip" if item["kategori"] == "Open Trip" else "Tiket Masuk Mandiri"
                            sql = """INSERT INTO booking (jenis_layanan, nama_pemesan, email, no_hp, paket_wisata, tanggal_pembelian, masa_berlaku, jumlah_peserta, metode_pembayaran, total_bayar, status) 
                                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                            val = (
                                jenis_simpan, nama_pemesan, user_aktif["email"], user_aktif["no_hp"],
                                item["nama"], str(tgl_hari_ini), teks_masa_berlaku, jumlah_orang, "QRIS", total_bayar, "Menunggu Pembayaran"
                            )
                            cursor.execute(sql, val)
                            conn.commit()
                            st.session_state.transaksi_aktif_id = cursor.lastrowid
                            cursor.close()
                            conn.close()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Gagal terhubung ke database XAMPP: {e}")

    with col_qris:
        st.subheader("💳 Status Pembayaran QRIS")
        with st.container(border=True):
            if not sudah_konfirmasi:
                st.info("👈 Silakan tentukan jumlah pesanan di sebelah kiri lalu klik tombol **Konfirmasi Pesanan** untuk memunculkan kode barcode QRIS.")
            
            elif status_pembayaran == "Menunggu Pembayaran":
                id_trx = st.session_state.transaksi_aktif_id
               url_webhook_scan = f"https://https://go-adventure.streamlit.app/?bayar_id={id_trx}"
                url_qr = f"https://api.qrserver.com/v1/create-qr-code/?size=230x230&data={url_webhook_scan}"
                
                st.markdown("<p style='text-align: center; font-weight: bold; color: #1B5E20; margin-bottom: 5px;'>SCAN BARCODE QRIS GO ADVENTURE</p>", unsafe_allow_html=True)
                
                col_q1, col_q2, col_q3 = st.columns([1, 2, 1])
                with col_q2:
                    st.image(url_qr, caption=f"ID Pesanan: #{id_trx} • Rp {total_bayar:,}", use_container_width=True)
                    
                st.info("🔄 **Menunggu pembayaran masuk...** Scan barcode QRIS di atas menggunakan kamera HP (1 Wi-Fi). Barcode akan **otomatis menghilang** begitu pembayaran masuk!")
                st.caption(f"💡 *Simulasi tes di 1 layar laptop: [Klik link ini untuk simulasi hasil scan QRIS](?bayar_id={id_trx})*")
                
                time.sleep(2)
                st.rerun()

            elif status_pembayaran == "Lunas":
                st.balloons()
                st.success("## 🎉 Pembayaran Berhasil!")
                st.write(f"Terima kasih **{nama_pemesan}**! Pembayaran via **QRIS** sebesar **Rp {total_bayar:,}** telah otomatis diterima.")
                st.info(f"📲 Tim & Admin **Go Adventure** akan segera menghubungi nomor WhatsApp **{user_aktif['no_hp']}** dan mengirim detail ke **{user_aktif['email']}** untuk konfirmasi jadwal.")
                st.write(f"**Detail Masa Berlaku:** {teks_masa_berlaku}")
                
                if st.button("👤 Lihat di Riwayat Pesanan Saya", type="primary", use_container_width=True):
                    st.session_state.transaksi_aktif_id = None
                    st.session_state.halaman = "Akun Saya"
                    st.rerun()

# ==========================================
# 6. PAGE AKUN PENGGUNA (DATA DIRI BISA DIGANTI, RIWAYAT PESANAN, LUPA SANDI, LOGOUT)
# ==========================================
elif selected == "Akun Saya":
    if st.session_state.user_login is None:
        st.session_state.halaman = "Login"
        st.rerun()

    u = st.session_state.user_login
    st.subheader(f"👤 Profil & Akun Saya — {u['nama']}")
    
    tab_profil, tab_riwayat, tab_lupa_akun = st.tabs([
        "🪪 Data Diri (Ubah Gmail & No. HP)", 
        "🧾 Riwayat Pesanan Saya", 
        "🔑 Lupa / Ubah Sandi"
    ])
    
    with tab_profil:
        with st.container(border=True):
            st.markdown("#### Edit Informasi Kontak")
            st.caption("Nomor HP dan Gmail ini digunakan tim Go Adventure untuk menghubungi kamu saat konfirmasi keberangkatan.")
            edit_nama = st.text_input("Nama Lengkap", value=u["nama"])
            edit_email = st.text_input("Alamat Gmail", value=u["email"])
            edit_hp = st.text_input("Nomor HP / WhatsApp", value=u["no_hp"])
            
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                if st.button("💾 Simpan Perubahan Profil", type="primary", use_container_width=True):
                    if not edit_nama.strip() or "@gmail.com" not in edit_email.lower() or not edit_hp.isdigit() or len(edit_hp) < 10:
                        st.error("Pastikan Nama terisi, Gmail valid (@gmail.com), dan No. HP minimal 10 digit angka!")
                    else:
                        try:
                            conn = koneksi_db()
                            cursor = conn.cursor()
                            email_lama = u["email"]
                            cursor.execute(
                                "UPDATE users SET nama = %s, email = %s, no_hp = %s WHERE id = %s",
                                (edit_nama.strip(), edit_email.strip().lower(), edit_hp.strip(), u["id"])
                            )
                            cursor.execute(
                                "UPDATE booking SET nama_pemesan = %s, email = %s, no_hp = %s WHERE email = %s",
                                (edit_nama.strip(), edit_email.strip().lower(), edit_hp.strip(), email_lama)
                            )
                            conn.commit()
                            cursor.close()
                            conn.close()
                            
                            st.session_state.user_login["nama"] = edit_nama.strip()
                            st.session_state.user_login["email"] = edit_email.strip().lower()
                            st.session_state.user_login["no_hp"] = edit_hp.strip()
                            st.success("✅ Data diri berhasil diperbarui!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Gagal memperbarui profil: {e}")
            with col_p2:
                if st.button("🚪 Logout dari Akun", type="secondary", use_container_width=True):
                    st.session_state.user_login = None
                    st.session_state.transaksi_aktif_id = None
                    if "uid" in st.query_params:
                        del st.query_params["uid"]
                    st.query_params["logout"] = "1"
                    st.session_state.halaman = "Beranda"
                    st.rerun()

    with tab_riwayat:
        try:
            conn = koneksi_db()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM booking WHERE email = %s ORDER BY id DESC", (u["email"],))
            hasil = cursor.fetchall()
            cursor.close()
            conn.close()
            
            if not hasil:
                st.info("Kamu belum memiliki riwayat pesanan.")
            else:
                for row in hasil:
                    with st.container(border=True):
                        c1, c2, c3 = st.columns([2.2, 1.5, 1])
                        with c1:
                            st.markdown(f"#### #{row['id']} • {row['paket_wisata']}")
                            st.write(f"🏷️ **Layanan:** {row['jenis_layanan']}  |  👥 **Jumlah:** {row['jumlah_peserta']} orang")
                            if row["status"] == "Dibatalkan Admin":
                                alasan = row["alasan_batal"] if row["alasan_batal"] else "alasan operasional."
                                st.error(f"admin membatalkan pesanan anda karena {alasan}")
                        with c2:
                            st.write(f"🗓️ **Tgl Pemesanan:** {row['tanggal_pembelian']}")
                            st.write(f"⏳ **Jadwal / Berlaku:** {row['masa_berlaku']}")
                            st.markdown(f"**💰 Total:** Rp {row['total_bayar']:,} ({row['metode_pembayaran']})")
                        with c3:
                            if row["status"] == "Lunas":
                                st.success(f"Status: **{row['status']}**")
                            elif row["status"] == "Menunggu Pembayaran":
                                st.warning(f"Status: **{row['status']}**")
                            else:
                                st.error(f"Status: **{row['status']}**")
        except Exception as e:
            st.error(f"Gagal memuat riwayat pesanan: {e}")

    with tab_lupa_akun:
        with st.container(border=True):
            st.markdown("#### Reset / Ubah Kata Sandi")
            verif_kontak = st.text_input("Konfirmasi Gmail atau Nomor WhatsApp Terdaftar:", placeholder="Masukkan Gmail atau No. WA...")
            sandi_baru = st.text_input("Kata Sandi Baru (Minimal 6 karakter)", type="password")
            konf_sandi = st.text_input("Ulangi Kata Sandi Baru", type="password")
            if st.button("🔄 Perbarui Kata Sandi", type="primary"):
                if verif_kontak.strip().lower() not in [u["email"].lower(), u["no_hp"]]:
                    st.error("Gmail atau Nomor WhatsApp tidak sesuai dengan akunmu!")
                elif len(sandi_baru) < 6:
                    st.error("Kata sandi minimal 6 karakter!")
                elif sandi_baru != konf_sandi:
                    st.error("Konfirmasi kata sandi tidak cocok!")
                else:
                    try:
                        conn = koneksi_db()
                        cursor = conn.cursor()
                        cursor.execute("UPDATE users SET password = %s WHERE id = %s", (sandi_baru.strip(), u["id"]))
                        conn.commit()
                        cursor.close()
                        conn.close()
                        st.session_state.user_login["password"] = sandi_baru.strip()
                        st.success("✅ Kata sandi berhasil diubah!")
                    except Exception as e:
                        st.error(f"Gagal mengubah sandi: {e}")

# ==========================================
# 7. DASHBOARD ADMIN (BEBAS ERROR PYARROW / SMART APP CONTROL)
# ==========================================
elif selected == "Dashboard Admin":
    if not st.session_state.admin_login:
        st.session_state.halaman = "Login"
        st.rerun()

    st.subheader("📊 Dashboard Administrator — Laporan Keuangan & Kelola Pesanan")
    tab_keuangan, tab_pesanan = st.tabs([
        "💰 Laporan Keuangan Go Adventure", 
        "📋 Kelola Pesanan & Pembatalan"
    ])

    with tab_keuangan:
        try:
            conn = koneksi_db()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM booking ORDER BY id DESC")
            semua_trx = cursor.fetchall()
            cursor.close()
            conn.close()

            trx_lunas = [t for t in semua_trx if t["status"] == "Lunas"]
            trx_batal = [t for t in semua_trx if "Dibatalkan" in t["status"]]
            
            total_pendapatan = sum(t["total_bayar"] for t in trx_lunas)
            pendapatan_trip = sum(t["total_bayar"] for t in trx_lunas if "Open Trip" in t["jenis_layanan"])
            pendapatan_tiket = sum(t["total_bayar"] for t in trx_lunas if "Tiket" in t["jenis_layanan"])

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("💵 Total Pendapatan", f"Rp {total_pendapatan:,}")
            m2.metric("🎒 Pemasukan Open Trip", f"Rp {pendapatan_trip:,}")
            m3.metric("🎟️ Pemasukan Tiket", f"Rp {pendapatan_tiket:,}")
            m4.metric("📊 Lunas / Batal", f"{len(trx_lunas)} Lunas • {len(trx_batal)} Batal")

            st.divider()
            st.markdown("#### 📑 Rincian Pemasukan Transaksi Lunas")
            if not trx_lunas:
                st.info("Belum ada transaksi lunas yang tercatat.")
            else:
                for t in trx_lunas:
                    with st.container(border=True):
                        rk1, rk2, rk3 = st.columns([2, 1.5, 1])
                        with rk1:
                            st.markdown(f"**#{t['id']} • {t['paket_wisata']}**")
                            st.caption(f"👤 Pemesan: {t['nama_pemesan']} ({t['no_hp']})")
                        with rk2:
                            st.write(f"🏷️ {t['jenis_layanan']} • 👥 {t['jumlah_peserta']} org")
                            st.caption(f"🗓️ Tgl Bayar: {t['tanggal_pembelian']} ({t['metode_pembayaran']})")
                        with rk3:
                            st.markdown(f"<h4 style='color: #2E7D32; text-align: right; margin: 0;'>+ Rp {t['total_bayar']:,}</h4>", unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Gagal memuat laporan keuangan: {e}")

    with tab_pesanan:
        st.write("Daftar pesanan pelanggan ditampilkan berbaris ke samping. Klik **Lihat Detail & Pembatalan** pada kartu pesanan untuk melihat rincian lengkap:")
        try:
            conn = koneksi_db()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM booking ORDER BY id DESC")
            semua_pesanan = cursor.fetchall()
            cursor.close()
            conn.close()

            if not semua_pesanan:
                st.info("Belum ada pesanan masuk.")
            else:
                for i in range(0, len(semua_pesanan), 3):
                    cols_p = st.columns(3)
                    for j in range(3):
                        if i + j < len(semua_pesanan):
                            p = semua_pesanan[i + j]
                            with cols_p[j]:
                                with st.container(border=True):
                                    st.markdown(f"#### 👤 {p['nama_pemesan']}")
                                    st.write(f"🎒 **Paket:** {p['paket_wisata']}")
                                    
                                    if p["status"] == "Lunas":
                                        st.success(f"Status: {p['status']}")
                                    elif p["status"] == "Menunggu Pembayaran":
                                        st.warning(f"Status: {p['status']}")
                                    else:
                                        st.error(f"Status: {p['status']}")

                                    with st.expander("🔍 Klik untuk Detail & Pembatalan"):
                                        st.write(f"**ID Pesanan:** #{p['id']}")
                                        st.write(f"**Paket Dipilih:** {p['paket_wisata']} ({p['jenis_layanan']})")
                                        st.write(f"**Jumlah:** {p['jumlah_peserta']} orang (Rp {p['total_bayar']:,})")
                                        st.write(f"**Tanggal Pemesanan:** {p['tanggal_pembelian']}")
                                        st.write(f"**Tanggal Reservasi / Berlaku:** {p['masa_berlaku']}")
                                        st.write(f"**Gmail:** {p['email']}")
                                        st.write(f"**No. Telepon / WA:** {p['no_hp']}")
                                        
                                        st.divider()
                                        if p["status"] in ["Lunas", "Menunggu Pembayaran"]:
                                            alasan_input = st.text_input(
                                                "Alasan Pembatalan:", 
                                                placeholder="Contoh: Kuota penuh / cuaca buruk...", 
                                                key=f"alasan_adm_{p['id']}"
                                            )
                                            if st.button("❌ Batalkan Pesanan", key=f"btn_batal_adm_{p['id']}", type="primary", use_container_width=True):
                                                if alasan_input.strip() == "":
                                                    st.error("Wajib mengisi alasan pembatalan!")
                                                else:
                                                    conn_b = koneksi_db()
                                                    cur_b = conn_b.cursor()
                                                    cur_b.execute(
                                                        "UPDATE booking SET status = 'Dibatalkan Admin', alasan_batal = %s WHERE id = %s",
                                                        (alasan_input.strip(), p["id"])
                                                    )
                                                    conn_b.commit()
                                                    cur_b.close()
                                                    conn_b.close()
                                                    st.warning(f"Pesanan #{p['id']} berhasil dibatalkan.")
                                                    st.rerun()
                                        else:
                                            if p["alasan_batal"]:
                                                st.info(f"**Alasan Pembatalan:** {p['alasan_batal']}")
        except Exception as e:
            st.error(f"Gagal memuat daftar pesanan: {e}")

# Panggil Floating AI Assistant di pojok kiri bawah
tampilkan_chatbot_mengambang(koneksi_db)
