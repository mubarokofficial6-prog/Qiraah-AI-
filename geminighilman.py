import streamlit as st
import time

# ==============================================================================
# 1. VERIFIKASI INSTALASI LIBRARY PENDUKUNG (Anti Undefined Pustaka)
# ==============================================================================
try:
    from google import genai
    from google.genai import types
    LIBRARY_AMAN = True
except ImportError:
    LIBRARY_AMAN = False

# ==============================================================================
# 2. SETTING HALAMAN & STYLE DESAIN MODERN ELEGAN (HIJAU MADRASAH & EMAS)
# ==============================================================================
st.set_page_config(
    page_title="Qira'ah AI - Maharah Qira'ah VII",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style yang disesuaikan agar elegan, bersih, dan ramah anak kelas VII MTs
st.markdown("""
    <style>
    .stApp { background-color: #f7faf7; }
    .main-title { color: #1e4d2b; font-family: 'Poppins', sans-serif; font-weight: 700; text-align: center; margin-top: -20px; margin-bottom: 5px; }
    .subtitle { color: #555555; text-align: center; margin-bottom: 35px; font-size: 1.1rem; }
    div.stButton > button:first-child { background-color: #1e4d2b; color: white; border-radius: 8px; border: 1px solid #c5a059; font-weight: bold; }
    div.stButton > button:first-child:hover { background-color: #163a20; color: #c5a059; }
    .stTextInput>div>div>input { border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

if not LIBRARY_AMAN:
    st.error("❌ Komponen Sistem Belum Lengkap!")
    st.info("Buka Terminal/CMD Anda terlebih dahulu, lalu ketik perintah berikut:\n\n`pip install google-genai streamlit` \n\nSetelah selesai instalasi, silakan jalankan kembali aplikasinya.")
    st.stop()

# ==============================================================================
# 3. MANAJEMEN MEMORI SESI (PREVENTING UNDEFINED STATE ERRORS)
# ==============================================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "current_persona" not in st.session_state:
    st.session_state.current_persona = ""
if "current_materi" not in st.session_state:
    st.session_state.current_materi = ""
if "active_model" not in st.session_state:
    st.session_state.active_model = "gemini-2.5-flash"

# ==============================================================================
# 4. GERBANG MASUK (HALAMAN LOGIN DENGAN BYPASS VALIDASI ANTI CRASH)
# ==============================================================================
if not st.session_state.logged_in:
    st.markdown("<h1 class='main-title'>📖 QIRA'AH AI 📖</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Aplikasi Pembelajaran Mandiri Interaktif • Khusus Maharah Qira'ah Kelas VII Madrasah Tsanawiyah / Aliyah</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.8, 1])
    with col2:
        st.write("### 🔑 Validasi Akses Siswa")
        username = st.text_input("Nama Lengkap Siswa", placeholder="Masukkan nama Anda...")
        api_key = st.text_input("Google AI Studio API Key", type="password", placeholder="Masukkan kunci AIzaSy...")
        
        st.markdown("---")
        if st.button("Masuk Ke Ruang Belajar 🚀", use_container_width=True):
            if username.strip() and api_key.strip():
                # Menggunakan teknik bypass cerdas Anda agar tidak macet di gerbang depan
                st.session_state.username = username
                st.session_state.api_key = api_key
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.warning("⚠️ Harap lengkapi Nama Anda dan API Key terlebih dahulu!")
    st.stop()

# ==============================================================================
# 5. INTEGRASI API GOOGLE & PANEL SIDEBAR (PILIHAN TOPIK KELAS VII & PERSONA GURU)
# ==============================================================================
client = genai.Client(api_key=st.session_state.api_key)

with st.sidebar:
    st.markdown("<h2 style='color: white; font-weight: bold;'>📖 Qira'ah AI</h2>", unsafe_allow_html=True)
    st.write(f"Siswa aktif: **{st.session_state.username}**")
    
    # Fitur ganti model manual jika salah satu model utama down/sibuk
    st.session_state.active_model = st.selectbox(
        "⚙️ Model Engine AI (Ganti jika error 503):",
        ["gemini-2.5-flash", "gemini-1.5-flash"],
        index=0
    )
    st.markdown("---")
    
    ustadz_pilihan = st.radio("🎙️ Pilih Guru Pendamping:", ["Ustadz Ahmad", "Ustadzah Fatimah"])
    materi_pilihan = st.selectbox(
        "📚 Pilih Materi Qira'ah (Kelas VII):",
        [
            "العُنْوَانُ (Al-Unwan / Alamat)",
            "المَرَافِقُ المَدْرَسِيَّةُ (Al-Marafiq Al-Madrasiyyah / Fasilitas Sekolah)",
            "البَيْتُ (Al-Bait / Rumah)"
        ]
    )
    
    st.markdown("---")
    if st.button("🚪 Keluar Sesi", use_container_width=True):
        st.session_state.clear()
        st.rerun()

if st.session_state.current_persona != ustadz_pilihan or st.session_state.current_materi != materi_pilihan:
    st.session_state.current_persona = ustadz_pilihan
    st.session_state.current_materi = materi_pilihan
    st.session_state.chat_history = [] 

# Prompt Instruksi yang difokuskan penuh pada melatih Maharah Qira'ah (Membaca & Memahami)
instruksi_sistem = f"""
Anda adalah {ustadz_pilihan}, seorang pendidik bahasa Arab yang ramah, interaktif, dan sabar untuk anak kelas VII MTs/MA.
Fokus materi Anda saat ini adalah mengajarkan Keterampilan Membaca dan Memahami Teks (Maharah Qira'ah) dengan topik khusus: {materi_pilihan}.

Aturan Berkomunikasi:
1. Awali kelas menggunakan salam Islami dan sapa siswa bernama {st.session_state.username}.
2. Berikan potongan teks qira'ah (bacaan) pendek yang sesuai untuk tingkat pemula (kelas VII) berharakat lengkap dan jelas.
3. Bimbing siswa untuk membaca teks tersebut, menerjemahkannya, atau berikan pertanyaan pemahaman (soal cerita pendek) berdasarkan teks.
4. Gunakan bahasa Indonesia untuk instruksi pengajaran agar mudah dipahami siswa, namun teks qira'ah wajib menggunakan bahasa Arab.
5. Berikan apresiasi atau pujian Islami seperti ممتاز (Mumtaz!) atau بَارَكَ اللهُ فِيْك (Barakallahufiik) jika jawaban siswa benar.
"""

# ==============================================================================
# 6. PANEL CHAT UTAMA & RIWAYAT PERCAKAPAN (CONVERSATION HISTORY)
# ==============================================================================
st.markdown(f"## 🏛️ Ruang Qira'ah: {materi_pilihan}")
st.write(f"Guru Pendamping: **{ustadz_pilihan}**")

# Menampilkan Riwayat Percakapan yang tersimpan
for chat in st.session_state.chat_history:
    with st.chat_message(chat["role"]):
        st.markdown(chat["content"])

# Pengondisian Pesan Pembuka Otomatis (Greeting Persona)
if len(st.session_state.chat_history) == 0:
    if ustadz_pilihan == "Ustadz Ahmad":
        salam_pembuka = f"Assalamu'alaikum wr. wb. Selamat datang di kelas bahasa Arab, Ananda **{st.session_state.username}**. Bersama Ustadz Ahmad di sini, mari kita latih kelancaran membaca dan memahami teks (*Maharah Qira'ah*) tentang **{materi_pilihan}**. Silakan ketik 'Siap Ustadz' jika Ananda sudah siap membaca teks hari ini."
    else:
        salam_pembuka = f"Assalamu'alaikum wr. wb. Halo anakku yang shalih/shalihah, **{st.session_state.username}**! Senang sekali bisa berjumpa dengan Ustadzah Fatimah di aplikasi Qira'ah AI. Kita akan belajar memahami teks bahasa Arab dengan cara yang seru untuk materi **{materi_pilihan}**. Sapa Ustadzah sekarang untuk mendapatkan teks bacaan pertamamu ya!"
        
    st.session_state.chat_history.append({"role": "assistant", "content": salam_pembuka})
    st.rerun()

# Menangani Masukan Chat dari Pengguna
if pesan_user := st.chat_input("Ketik tanggapan Anda atau jawaban latihan Qira'ah di sini..."):
    with st.chat_message("user"):
        st.markdown(pesan_user)
    st.session_state.chat_history.append({"role": "user", "content": pesan_user})

    # Fitur Perintah Keluar manual melalui input chat
    if pesan_user.lower() in ['exit', 'quit', 'keluar']:
        st.session_state.clear()
        st.rerun()

    # Menyusun Payload Konten History
    payload_konten = []
    for msg in st.session_state.chat_history:
        peran_api = "user" if msg["role"] == "user" else "model"
        payload_konten.append(
            types.Content(role=peran_api, parts=[types.Part.from_text(text=msg["content"])])
        )

    # LOOP RETRY OTOMATIS TAHAN ERROR JIKA SERVER GOOGLE 503 ATAU HIGH DEMAND
    respons_api = None
    max_retries = 3
    
    with st.spinner(f"{ustadz_pilihan} sedang memeriksa jawaban Anda..."):
        for i in range(max_retries):
            try:
                respons_api = client.models.generate_content(
                    model=st.session_state.active_model,
                    contents=payload_konten,
                    config=types.GenerateContentConfig(
                        system_instruction=instruksi_sistem,
                        temperature=0.5,
                    )
                )
                break  # Berhasil terkoneksi! keluar dari loop retry
            except Exception as e:
                # Jika terkena rate limit/high demand/503, tunggu sebentar lalu coba lagi
                if ("503" in str(e) or "demand" in str(e).lower()) and i < max_retries - 1:
                    time.sleep(2)
                    continue
                else:
                    respons_api = e

    # Evaluasi Hasil Akhir Respon API
    if respons_api and not isinstance(respons_api, Exception):
        teks_balasan = respons_api.text
        with st.chat_message("assistant"):
            st.markdown(teks_balasan)
        st.session_state.chat_history.append({"role": "assistant", "content": teks_balasan})
    else:
        # Tampilan pesan error mitigasi yang aman sesuai dengan format file contoh Anda
        st.error("⚠️ Server Google AI Studio saat ini sedang sangat sibuk (High Demand).")
        st.info("💡 **Solusi Mudah:** Silakan lihat ke bilah kiri (Sidebar), ubah pilihan **Model Engine AI** Anda menjadi `gemini-1.5-flash`, lalu kirim ulang pesan Anda dengan menekan enter.")