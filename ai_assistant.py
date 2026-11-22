import streamlit as st
import streamlit.components.v1 as components
import base64
import os
import re
import json
import requests

# ==========================================
# KONFIGURASI API KEY GROQ
# ==========================================
def get_groq_api_key():
    return st.secrets.get("GROQ_API_KEY", "").strip()

@st.cache_data(ttl=3600)
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

# Cache data katalog wisata selama 5 menit agar AI tidak query MySQL tiap kali chat
@st.cache_data(ttl=300)
def ambil_konteks_wisata(_koneksi_db):
    try:
        conn = _koneksi_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT kategori, jenis_alam, nama, harga, kota_pulau, provinsi, jadwal, deskripsi_singkat, fasilitas FROM katalog")
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        if not data:
            return "Belum ada paket wisata yang terdaftar di katalog Go Adventure."
        teks = "DAFTAR PRODUK RESMI GO ADVENTURE SAAT INI:\n"
        for d in data:
            fas = (d.get("fasilitas") or "").replace("\n", ", ")
            teks += (
                f"- [{d['kategori']} - {d['jenis_alam']}] {d['nama']} | "
                f"Lokasi: {d['kota_pulau']}, {d['provinsi']} | "
                f"Harga: Rp {d['harga']:,}/orang | Jadwal: {d['jadwal']} | "
                f"Info: {d['deskripsi_singkat']} | Fasilitas: {fas}\n"
            )
        return teks
    except Exception:
        return "Data katalog sedang tidak dapat diakses."

def stream_groq_ai(riwayat_chat, koneksi_db):
    key = get_groq_api_key()
    if not key or "MASUKKAN_API_KEY" in key:
        yield "⚠️ API Key Groq belum diatur di Streamlit Secrets (`GROQ_API_KEY`)."
        return

    data_katalog = ambil_konteks_wisata(koneksi_db)
    sistem_prompt = (
        "Kamu adalah asisten AI ramah untuk platform wisata alam 'Go Adventure'. "
        "Jawablah setiap pertanyaan dalam Bahasa Indonesia dengan SINGKAT, PADAT, dan JELAS. Jangan bertele-tele dan jangan membuat tabel terlalu panjang.\n\n"
        f"{data_katalog}\n\n"
        "ATURAN WAJIB:\n"
        "1. DILARANG memakai tag HTML seperti <br>.\n"
        "2. Jika pengunjung menanyakan tempat wisata/destinasi yang TIDAK ADA di 'DAFTAR PRODUK RESMI GO ADVENTURE SAAT INI', tetap berikan penjelasan informatif singkat tentang tempat tersebut, lalu tutup di baris akhir dengan kalimat minta maaf karena Go Adventure belum mempunyai layanan tersebut.\n"  
        "3. Jika produk MEMANG ADA di daftar resmi di atas, sebutkan nama, lokasi, dan harganya.\n"
        "4. Info Go Adventure: Open Trip ≥5 orang diskon Rp 100.000. Tiket Mandiri berlaku 30 hari. Bayar via QRIS. CS WA: +6283105717926."
    )

    messages_payload = [{"role": "system", "content": sistem_prompt}]
    for msg in riwayat_chat[-6:]:
        messages_payload.append({"role": msg["role"], "content": msg["content"]})

    try:
        # Langsung panggil model cepat dengan mode stream=True (tanpa request GET /models lagi)
        with requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.1-8b-instant",
                "messages": messages_payload,
                "temperature": 0.6,
                "max_tokens": 800,
                "stream": True
            },
            stream=True,
            timeout=12
        ) as response:
            if response.status_code != 200:
                err_text = response.text
                if response.status_code == 401:
                    yield "⚠️ Error Groq (401): API Key tidak valid atau kedaluwarsa. Harap perbarui `GROQ_API_KEY` di Streamlit Secrets."
                else:
                    yield f"⚠️ Error Groq ({response.status_code}): {err_text}"
                return

            for line in response.iter_lines():
                if line:
                    decoded = line.decode("utf-8")
                    if decoded.startswith("data: "):
                        data_str = decoded[6:].strip()
                        if data_str == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data_str)
                            delta = chunk["choices"][0].get("delta", {})
                            konten = delta.get("content", "")
                            if konten:
                                konten = re.sub(r"<br\s*/?>", "\n", konten, flags=re.IGNORECASE)
                                yield konten
                        except json.JSONDecodeError:
                            continue
    except requests.exceptions.Timeout:
        yield "⚠️ Koneksi ke server AI melebihi batas waktu (timeout). Silakan coba kirim ulang."
    except Exception as e:
        yield f"⚠️ Gagal terhubung ke server AI: {e}"

def tampilkan_chatbot_mengambang(koneksi_db):
    if "chat_open" not in st.session_state:
        st.session_state.chat_open = False
    if "chat_expanded" not in st.session_state:
        st.session_state.chat_expanded = False
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [
            {
                "role": "assistant",
                "content": "Halo! 👋 Saya Asisten AI **Go Adventure**. Tanya apa saja seputar wisata alam, rekomendasi destinasi, atau paket trip kami!"
            }
        ]

    logo_b64 = get_base64_image("img/ai_logo.png")
    bg_style = (
        f'background-image: url("data:image/png;base64,{logo_b64}") !important; background-size: cover !important; background-position: center !important;'
        if logo_b64 else
        'background: linear-gradient(135deg, #43A047, #1B5E20) !important;'
    )

    # Render tombol logo di pojok kiri bawah
    st.markdown('<div id="marker-tombol-ai"></div>', unsafe_allow_html=True)
    if st.button("AI", key="btn_floating_ai_logo", help="Buka Asisten AI Go Adventure"):
        st.session_state.chat_open = not st.session_state.chat_open
        st.rerun(scope="fragment")

    # Render jendela chat jika tombol diklik
    if st.session_state.chat_open:
        st.markdown('<div id="marker-jendela-ai"></div>', unsafe_allow_html=True)
        with st.container(border=True):
            rasio_hdr = [6.2, 0.7, 0.7] if st.session_state.chat_expanded else [3.4, 1.1, 1.1]
            c_title, c_expand, c_close = st.columns(rasio_hdr)
            with c_title:
                st.markdown("**✨ Go Adventure AI** <br><span style='font-size:11px; color:#2E7D32;'>● Online</span>", unsafe_allow_html=True)
            with c_expand:
                ikon_zoom = "🗗" if st.session_state.chat_expanded else "⛶"
                tip_zoom = "Perkecil jendela" if st.session_state.chat_expanded else "Perbesar hampir full layar"
                if st.button(ikon_zoom, key="btn_expand_ai_win", help=tip_zoom, use_container_width=True):
                    st.session_state.chat_expanded = not st.session_state.chat_expanded
                    st.rerun(scope="fragment")
            with c_close:
                if st.button("✖", key="btn_close_ai_win", help="Tutup chat", use_container_width=True):
                    st.session_state.chat_open = False
                    st.rerun(scope="fragment")

            # Area Chat
            st.markdown('<div id="marker-area-chat"></div>', unsafe_allow_html=True)
            if st.session_state.chat_expanded:
                chat_area = st.container(border=False)
            else:
                chat_area = st.container(height=270, border=False)

            with chat_area:
                for msg in st.session_state.chat_messages:
                    with st.chat_message(msg["role"]):
                        konten_bersih = re.sub(r"<br\s*/?>", "\n", msg["content"], flags=re.IGNORECASE)
                        st.markdown(konten_bersih)

            # Form Input di bagian bawah card
            with st.form(key="form_kirim_pesan_ai", clear_on_submit=True):
                rasio_form = [5.2, 1.0] if st.session_state.chat_expanded else [3.4, 1.3]
                col_in, col_btn = st.columns(rasio_form)
                with col_in:
                    prompt = st.text_input("Pesan", placeholder="Tanya apa saja...", label_visibility="collapsed")
                with col_btn:
                    submit = st.form_submit_button("Kirim", type="primary", use_container_width=True)

            if submit and prompt.strip():
                pesan_user = prompt.strip()
                st.session_state.chat_messages.append({"role": "user", "content": pesan_user})
                with chat_area:
                    with st.chat_message("user"):
                        st.markdown(pesan_user)
                    with st.chat_message("assistant"):
                        jawaban_lengkap = st.write_stream(stream_groq_ai(st.session_state.chat_messages, koneksi_db))
                st.session_state.chat_messages.append({"role": "assistant", "content": jawaban_lengkap})

    is_expanded_js = "true" if st.session_state.chat_expanded else "false"

    components.html(f"""
    <script>
        const doc = window.parent.document;
        const isExpanded = {is_expanded_js};

        const markerBtn = doc.getElementById('marker-tombol-ai');
        if (markerBtn) {{
            const wrapperBtn = markerBtn.closest('[data-testid="stElementContainer"]').nextElementSibling;
            if (wrapperBtn) {{
                wrapperBtn.style.cssText = `
                    position: fixed !important;
                    bottom: 24px !important;
                    left: 24px !important;
                    width: 64px !important;
                    height: 64px !important;
                    z-index: 999999 !important;
                `;
                const btn = wrapperBtn.querySelector('button');
                if (btn) {{
                    btn.style.cssText = `
                        width: 64px !important;
                        height: 64px !important;
                        min-height: 64px !important;
                        border-radius: 18px !important;
                        {bg_style}
                        border: 2px solid #A5D6A7 !important;
                        box-shadow: 0 6px 18px rgba(0,0,0,0.35) !important;
                        color: transparent !important;
                        padding: 0 !important;
                    `;
                }}
            }}
        }}

        const markerWin = doc.getElementById('marker-jendela-ai');
        if (markerWin) {{
            const wrapperWin = markerWin.closest('[data-testid="stElementContainer"]').nextElementSibling;
            if (wrapperWin) {{
                if (isExpanded) {{
                    wrapperWin.style.cssText = `
                        position: fixed !important;
                        top: 20px !important;
                        left: 24px !important;
                        right: 24px !important;
                        bottom: 98px !important;
                        width: calc(100vw - 48px) !important;
                        max-width: none !important;
                        height: calc(100vh - 118px) !important;
                        background-color: #FFFFFF !important;
                        border-radius: 16px !important;
                        z-index: 999998 !important;
                        box-shadow: 0 12px 40px rgba(0,0,0,0.35) !important;
                        display: flex !important;
                        flex-direction: column !important;
                        overflow: hidden !important;
                        box-sizing: border-box !important;
                    `;
                }} else {{
                    wrapperWin.style.cssText = `
                        position: fixed !important;
                        bottom: 100px !important;
                        left: 24px !important;
                        width: 390px !important;
                        max-width: 90vw !important;
                        background-color: #FFFFFF !important;
                        border-radius: 16px !important;
                        z-index: 999998 !important;
                        box-shadow: 0 12px 32px rgba(0,0,0,0.28) !important;
                        overflow: hidden !important;
                    `;
                }}

                const headerBtns = wrapperWin.querySelectorAll('[data-testid="stHorizontalBlock"]:first-of-type button');
                headerBtns.forEach((b) => {{
                    b.style.padding = '4px 0px';
                    b.style.minWidth = '36px';
                    b.style.display = 'flex';
                    b.style.alignItems = 'center';
                    b.style.justifyContent = 'center';
                    b.style.fontSize = '15px';
                }});

                const innerBlock = wrapperWin.querySelector('[data-testid="stVerticalBlock"]');
                if (innerBlock && isExpanded) {{
                    innerBlock.style.cssText = `
                        height: 100% !important;
                        display: flex !important;
                        flex-direction: column !important;
                        justify-content: space-between !important;
                        overflow: hidden !important;
                    `;
                }}
            }}
        }}

        const markerChat = doc.getElementById('marker-area-chat');
        if (markerChat && isExpanded) {{
            const chatBox = markerChat.closest('[data-testid="stElementContainer"]').nextElementSibling;
            if (chatBox) {{
                chatBox.style.cssText = `
                    flex: 1 1 auto !important;
                    overflow-y: auto !important;
                    overflow-x: hidden !important;
                    max-height: calc(100vh - 255px) !important;
                    padding-right: 6px !important;
                `;
            }}
        }}
    </script>
    """, height=0, width=0)
