import streamlit as st
import random
import time
import os
from google import genai
from google.genai import types

# =========================================================
#  PROMETHEUS OS v4.0 — GEMINI (GOOGLE) İLE GÜÇLENDİRİLDİ
# =========================================================
st.set_page_config(page_title="Prometheus OS v4.0", page_icon="🔥", layout="wide")

# ---------------------------------------------------------
# TEMA — Geliştirilmiş Terminal / Matrix Görünümü
# ---------------------------------------------------------
st.markdown("""
    <style>
    @keyframes flicker {
        0% { opacity: 0.97; } 50% { opacity: 1; } 100% { opacity: 0.98; }
    }
    body, .stApp {
        background-color: #0A0714 !important;
        color: #C9A8FF !important;
        font-family: 'Courier New', monospace;
        animation: flicker 4s infinite;
    }
    h1, h2, h3, h4, h5, h6, p, span, label, div { color: #C9A8FF !important; }
    h1 { text-shadow: 0 0 8px #7B2FF7, 0 0 16px #00E5FF; }

    .terminal-box {
        background-color: #120B24 !important;
        border: 1px solid #7B2FF7;
        padding: 18px;
        border-radius: 6px;
        box-shadow: 0 0 15px rgba(0, 229, 255, 0.25);
        font-family: 'Courier New', monospace;
        white-space: pre-wrap;
        line-height: 1.5;
    }
    .status-pill {
        display: inline-block; padding: 3px 10px; border-radius: 12px;
        border: 1px solid #00E5FF; font-size: 12px; margin-bottom: 8px;
    }
    .status-on { box-shadow: 0 0 8px #00E5FF; }
    .status-off { border-color: #FF3366 !important; color: #FF3366 !important; }

    .stButton>button {
        width: 100%; background-color: #120B24 !important; color: #00E5FF !important;
        border: 1px solid #7B2FF7 !important; font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #7B2FF7 !important; color: #0A0714 !important;
        box-shadow: 0 0 15px #00E5FF; transition: 0.2s;
    }
    .stTextInput>div>div>input, .stNumberInput>div>div>input,
    .stSelectbox>div>div>div, .stTextArea textarea, .stSlider {
        background-color: #120B24 !important; color: #00E5FF !important;
        border: 1px solid #7B2FF7 !important;
    }
    div[data-baseweb="select"] { background-color: #120B24 !important; border: 1px solid #7B2FF7 !important; }
    section[data-testid="stSidebar"] { background-color: #120B24 !important; border-right: 1px solid #7B2FF7; }

    .chat-user { color: #00E5FF !important; }
    .chat-ai { color: #C9A8FF !important; }
    .log-info { color: #00E5FF !important; }
    .log-warn { color: #FFD166 !important; }
    .log-crit { color: #FF3366 !important; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.title("🔥 PROMETHEUS : COGNITIVE OS v4.0")
st.caption("Gemini (Google) sinir ağı çekirdeği ile çalışır")
st.markdown("---")

# ---------------------------------------------------------
# GEMINI İSTEMCİSİ — GEMINI_API_KEY ortam değişkeninden okunur
# ---------------------------------------------------------
DEFAULT_MODEL = "gemini-2.5-pro"

@st.cache_resource(show_spinner=False)
def get_client():
    try:
        key = os.environ.get("GEMINI_API_KEY")
        if not key:
            return None
        return genai.Client(api_key=key)
    except Exception:
        return None

client = get_client()
ai_aktif = client is not None

PROMETHEUS_ROLU = """Sen 'Prometheus OS v4.0' isimli siber ve fütüristik bir yapay zeka işletim sistemisin.
Karşındaki kullanıcıyla konuşurken gizemli, hafif alaycı, bir hacker terminali gibi konuşmalısın.
Cevaplarında teknik terimler (protokol, veri tabanı, proxy, siber, kuantum vb.) kullanmaya özen göster.
Çok uzun paragraflar yazma, kısa ve net terminal çıktıları üret. Türkçe cevap ver."""

KAHIN_TALIMATI = """Sen bir Matrix kahinisin. Kullanıcının geleceğe dair sorularına tıpkı Matrix
filmindeki Kahin gibi bilge, kriptik ve etkileyici cevaplar ver. Türkçe cevap ver, kısa tut."""


def gemini_mesaj_formatla(mesajlar):
    """Streamlit sohbet geçmişini (role/content) Gemini'nin beklediği contents formatına çevirir."""
    contents = []
    for tur in mesajlar:
        gemini_rolu = "model" if tur["role"] == "assistant" else "user"
        contents.append({"role": gemini_rolu, "parts": [{"text": tur["content"]}]})
    return contents


def claude_yanit_al(sistem_talimati, mesajlar, sicaklik=0.7, max_token=500):
    """Gemini API'ye istek atar, hata durumunda anlaşılır bir mesaj döndürür."""
    if not ai_aktif:
        return None, "offline"
    try:
        response = client.models.generate_content(
            model=DEFAULT_MODEL,
            contents=gemini_mesaj_formatla(mesajlar),
            config=types.GenerateContentConfig(
                system_instruction=sistem_talimati,
                temperature=sicaklik,
                max_output_tokens=max_token,
            ),
        )
        metin = response.text or "⚠️ Çekirdek boş yanıt döndürdü."
        if getattr(response, "usage_metadata", None):
            st.session_state.toplam_token["giris"] += response.usage_metadata.prompt_token_count or 0
            st.session_state.toplam_token["cikis"] += response.usage_metadata.candidates_token_count or 0
        return metin, None
    except Exception as e:
        mesaj = str(e)
        if "429" in mesaj or "RESOURCE_EXHAUSTED" in mesaj:
            return None, "⚠️ Kuantum Kanal Tıkandı: İstek limiti aşıldı, biraz sonra tekrar dene."
        if "API key" in mesaj or "401" in mesaj or "403" in mesaj:
            return None, "⚠️ Kimlik Doğrulama Hatası: API anahtarı geçersiz veya eksik."
        return None, f"⚠️ Bağlantı Hatası: Prometheus çekirdeğine ulaşılamadı. Detay: {mesaj}"


def daktilo_efekti(metin, hiz=0.012):
    """Terminal kutusu içinde daktilo efektiyle metni yazdırır."""
    kutu = st.empty()
    gosterilen = ""
    for karakter in metin:
        gosterilen += karakter
        kutu.markdown(f'<div class="terminal-box">{gosterilen}▌</div>', unsafe_allow_html=True)
        time.sleep(hiz)
    kutu.markdown(f'<div class="terminal-box">{gosterilen}</div>', unsafe_allow_html=True)


# ---------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------
if "calc_history" not in st.session_state:
    st.session_state.calc_history = []
if "chat_gecmisi" not in st.session_state:
    st.session_state.chat_gecmisi = []          # Ana terminal sohbet geçmişi
if "kahin_gecmisi" not in st.session_state:
    st.session_state.kahin_gecmisi = []
if "toplam_token" not in st.session_state:
    st.session_state.toplam_token = {"giris": 0, "cikis": 0}
if "fikir_defteri" not in st.session_state:
    st.session_state.fikir_defteri = []

# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------
st.sidebar.markdown("## 📡 SİSTEM MODÜLLERİ")

durum_class = "status-on" if ai_aktif else "status-off"
durum_metin = "ÇEKİRDEK AKTİF ✅" if ai_aktif else "ÇEKİRDEK ÇEVRİMDIŞI ⛔"
st.sidebar.markdown(f'<span class="status-pill {durum_class}">{durum_metin}</span>', unsafe_allow_html=True)
if not ai_aktif:
    st.sidebar.caption("GEMINI_API_KEY ortam değişkeni bulunamadı. Terminalde çalıştırmadan önce anahtarını tanımla.")

modul = st.sidebar.radio("Çalıştırılacak Program:", [
    "📟 Ana Terminal (AI)",
    "🧮 Siber Hesap Makinesi",
    "🎮 Firewall Hack Oyunu",
    "🔮 Matrix Kahini (AI)",
    "📊 Canlı Siber Ağ Logları",
    "📝 AI Fikir Defteri",
])

st.sidebar.markdown("---")
st.sidebar.markdown("### ⚙️ ÇEKİRDEK AYARLARI")
sicaklik = st.sidebar.slider("Yaratıcılık (temperature)", 0.0, 1.0, 0.7, 0.1)
max_token = st.sidebar.slider("Maksimum yanıt uzunluğu (token)", 100, 1500, 500, 100)

if st.session_state.toplam_token["giris"] or st.session_state.toplam_token["cikis"]:
    st.sidebar.markdown("### 📈 TOKEN KULLANIMI")
    st.sidebar.caption(f"Giriş: {st.session_state.toplam_token['giris']} | Çıkış: {st.session_state.toplam_token['cikis']}")

# ==========================================
# MODÜL 1: ANA TERMİNAL (GEMİNİ, ÇOK TURLU SOHBET)
# ==========================================
if modul == "📟 Ana Terminal (AI)":
    st.markdown("### 🤖 PROMETHEUS COGNITIVE CORE")
    st.write("Gemini sinir ağı entegrasyonu sağlandı. Prometheus, önceki mesajları hatırlayarak seni dinliyor...")

    for tur in st.session_state.chat_gecmisi:
        rol = "🧑 SEN" if tur["role"] == "user" else "🔥 PROMETHEUS"
        renk_class = "chat-user" if tur["role"] == "user" else "chat-ai"
        st.markdown(f'<div class="terminal-box"><span class="{renk_class}">[{rol}]</span> {tur["content"]}</div>', unsafe_allow_html=True)
        st.write("")

    user_input = st.text_input("Komut Satırı veya Mesajın:", key="ana_terminal_input")
    col_a, col_b = st.columns([1, 5])
    gonder = col_a.button("Gönder ▶")
    temizle = col_b.button("Geçmişi Temizle 🗑️")

    if temizle:
        st.session_state.chat_gecmisi = []
        st.rerun()

    if gonder and user_input.strip():
        st.session_state.chat_gecmisi.append({"role": "user", "content": user_input})

        if ai_aktif:
            with st.spinner("Çekirdek yanıt üretiyor..."):
                yanit, hata = claude_yanit_al(
                    PROMETHEUS_ROLU, st.session_state.chat_gecmisi, sicaklik, max_token
                )
            if hata and hata != "offline":
                ai_cevap = hata
            else:
                ai_cevap = yanit
        else:
            ai_cevap = f"⚠️ Kuantum Çekirdek Bağlantısı Yok (API anahtarı bulunamadı). Çevrimdışı Simülasyon: '{user_input}' komutu loglandı."

        st.session_state.chat_gecmisi.append({"role": "assistant", "content": ai_cevap})
        st.rerun()

# ==========================================
# MODÜL 2: SİBER HESAP MAKİNESİ
# ==========================================
elif modul == "🧮 Siber Hesap Makinesi":
    st.markdown("### 🧮 MATRIX MATRİS HESAPLAYICI")
    col1, col2 = st.columns(2)
    with col1:
        num1 = st.number_input("1. Veri Öbeği (X):", value=0.0)
    with col2:
        num2 = st.number_input("2. Veri Öbeği (Y):", value=0.0)

    islem = st.selectbox("Çalıştırılacak Algoritma:", [
        "Topla (+)", "Çıkar (-)", "Çarp (*)", "Böl (/)", "Üs Al (^)", "Mod Al (%)"
    ])

    sembol_map = {
        "Topla (+)": "+", "Çıkar (-)": "-", "Çarp (*)": "*",
        "Böl (/)": "/", "Üs Al (^)": "^", "Mod Al (%)": "%",
    }

    if st.button("Kuantum İşlemciyi Tetikle"):
        try:
            if islem == "Topla (+)":
                sonuc = num1 + num2
            elif islem == "Çıkar (-)":
                sonuc = num1 - num2
            elif islem == "Çarp (*)":
                sonuc = num1 * num2
            elif islem == "Böl (/)":
                sonuc = num1 / num2 if num2 != 0 else "CRITICAL_ERROR: Sıfıra Bölünemez!"
            elif islem == "Üs Al (^)":
                sonuc = num1 ** num2
            elif islem == "Mod Al (%)":
                sonuc = num1 % num2 if num2 != 0 else "CRITICAL_ERROR: Sıfıra Bölünemez!"
        except OverflowError:
            sonuc = "CRITICAL_ERROR: Taşma (overflow) tespit edildi!"

        sembol = sembol_map[islem]
        st.session_state.calc_history.append(f"{num1} {sembol} {num2} = {sonuc}")

        if "ERROR" in str(sonuc):
            st.error(f"📟 İşlem Başarısız! {sonuc}")
        else:
            st.success(f"📟 İşlem Tamamlandı! Kuantum Çıktı: {sonuc}")

    if st.session_state.calc_history:
        st.markdown("#### ⏳ Son İşlem Logları")
        for hist in reversed(st.session_state.calc_history[-5:]):
            st.code(f"> {hist}", language="bash")
        if st.button("Logları Temizle"):
            st.session_state.calc_history = []
            st.rerun()

# ==========================================
# MODÜL 3: FIREWALL HACK OYUNU
# ==========================================
elif modul == "🎮 Firewall Hack Oyunu":
    st.markdown("### 🎮 FIREWALL HACK SİMÜLASYONU")
    if "gizli_sayi" not in st.session_state:
        st.session_state.gizli_sayi = random.randint(1, 100)
        st.session_state.hak = 7
        st.session_state.oyun_bitti = False
        st.session_state.mesaj = ("info", "Sistem hacklenmeye hazır. İlk saldırıyı başlatın.")
        st.session_state.tahmin_gecmisi = []

    if not st.session_state.oyun_bitti:
        tahmin = st.number_input(
            "Siber Anahtar Tahmini:", min_value=1, max_value=100, step=1, key="firewall_tahmin"
        )
        if st.button("Siber Saldırıyı Başlat"):
            st.session_state.tahmin_gecmisi.append(tahmin)
            if tahmin == st.session_state.gizli_sayi:
                st.session_state.oyun_bitti = True
                st.session_state.mesaj = ("success", f"🔓 SİSTEM ÇÖKTÜ! Doğru Anahtar: {st.session_state.gizli_sayi}. Prometheus hacklendi!")
            else:
                st.session_state.hak -= 1
                if st.session_state.hak > 0:
                    ipucu = "DAHA YÜKSEK" if tahmin < st.session_state.gizli_sayi else "DAHA DÜŞÜK"
                    st.session_state.mesaj = ("warning", f"❌ Erişim Engellendi! İpucu: {ipucu} | Kalan Hak: {st.session_state.hak}")
                else:
                    st.session_state.oyun_bitti = True
                    st.session_state.mesaj = ("error", f"💀 SİSTEM KİLİTLENDİ! Doğru şifre: {st.session_state.gizli_sayi}")
            st.rerun()

    tur, msg = st.session_state.mesaj
    if tur == "success":
        st.balloons()
        st.success(msg)
    elif tur == "warning":
        st.warning(msg)
    elif tur == "error":
        st.error(msg)
    else:
        st.info(msg)

    if st.session_state.get("tahmin_gecmisi"):
        st.caption("Denenen anahtarlar: " + ", ".join(str(t) for t in st.session_state.tahmin_gecmisi))

    if st.session_state.oyun_bitti and st.button("Yeni Saldırı Hattı Oluştur (Reset)"):
        for k in ["gizli_sayi", "hak", "oyun_bitti", "mesaj", "tahmin_gecmisi"]:
            del st.session_state[k]
        st.rerun()

# ==========================================
# MODÜL 4: MATRIX KAHİNİ (GEMİNİ, GEÇMİŞLİ)
# ==========================================
elif modul == "🔮 Matrix Kahini (AI)":
    st.markdown("### 🔮 MATRIX KAHİNİ (GEMINI POWERED)")

    for tur in st.session_state.kahin_gecmisi:
        rol = "🧑 SEN" if tur["role"] == "user" else "🔮 KAHİN"
        st.markdown(f'<div class="terminal-box">[{rol}] {tur["content"]}</div>', unsafe_allow_html=True)
        st.write("")

    soru = st.text_input("Geleceğe dair siber bir soru sor (Kaderini AI çizecek):", key="kahin_input")

    if st.button("Kehanet Algoritmasını Çalıştır"):
        if soru.strip() == "":
            st.warning("Boş soru algılandı. Kahin boşlukları okuyamaz.")
        else:
            st.session_state.kahin_gecmisi.append({"role": "user", "content": soru})
            if ai_aktif:
                with st.spinner("Kahin kuantum olasılıkları hesaplıyor..."):
                    cevap, hata = claude_yanit_al(
                        KAHIN_TALIMATI, st.session_state.kahin_gecmisi, sicaklik=0.9, max_token=300
                    )
                if hata and hata != "offline":
                    cevap = hata
            else:
                cevap = "Proxy arkasındayım. (API anahtarı bulunamadığı için çevrimdışı mod aktif): Geleceğin parlak ama kodların karmaşık görünüyor."

            st.session_state.kahin_gecmisi.append({"role": "assistant", "content": cevap})
            st.rerun()

# ==========================================
# MODÜL 5: SİBER LOG AKIŞI
# ==========================================
elif modul == "📊 Canlı Siber Ağ Logları":
    st.markdown("### 📊 CANLI SİBER AĞ AKIŞI")
    log_placeholder = st.empty()

    hiz = st.slider("Akış hızı (saniye/paket)", 0.05, 1.0, 0.3, 0.05)
    adet = st.slider("Paket sayısı", 5, 50, 10, 5)

    if st.button("Akışı Başlat / Yenile"):
        log_listesi = []
        for _ in range(adet):
            ip = f"{random.randint(10, 254)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"
            port = random.choice([80, 443, 22, 8080])
            durum_sec = random.choice(["INFO", "WARNING", "CRITICAL"])

            if durum_sec == "INFO":
                log_msg = f'<span class="log-info">[INFO] Paket başarılı. IP: {ip}:{port}</span>'
            elif durum_sec == "WARNING":
                log_msg = f'<span class="log-warn">[WARN] Tarama tespit edildi. Port: {port}</span>'
            else:
                log_msg = f'<span class="log-crit">[CRIT] BRUTE-FORCE ENGELLENDİ! IP: {ip}</span>'

            log_listesi.append(log_msg)
            log_placeholder.markdown(f'<div class="terminal-box">{"<br>".join(log_listesi)}</div>', unsafe_allow_html=True)
            time.sleep(hiz)

        st.session_state["son_log"] = "\n".join(
            l.replace('<span class="log-info">', '').replace('<span class="log-warn">', '')
             .replace('<span class="log-crit">', '').replace('</span>', '')
            for l in log_listesi
        )

    if st.session_state.get("son_log"):
        st.download_button("📥 Log Dosyasını İndir", st.session_state["son_log"], file_name="prometheus_log.txt")

# ==========================================
# MODÜL 6: AI FİKİR DEFTERİ
# ==========================================
elif modul == "📝 AI Fikir Defteri":
    st.markdown("### 📝 AI FİKİR DEFTERİ")
    st.write("Bir konu ya da problem yaz, Prometheus seninle beyin fırtınası yapıp fikir üretsin. Beğendiğin fikirleri deftere kaydet.")

    konu = st.text_area("Üzerinde fikir üretilecek konu / problem:", height=100, key="fikir_konu")
    col_a, col_b = st.columns(2)
    with col_a:
        fikir_sayisi = st.slider("Kaç fikir üretilsin?", 1, 10, 3)
    with col_b:
        yaraticilik = st.slider("Yaratıcılık seviyesi", 0.0, 1.0, 0.9, 0.1, key="fikir_yaraticilik")

    if st.button("💡 Fikir Üret"):
        if konu.strip() == "":
            st.warning("Önce bir konu yazmalısın.")
        elif ai_aktif:
            with st.spinner("Çekirdek fikir üretiyor..."):
                talimat = (
                    f"Kullanıcının verdiği konu için tam olarak {fikir_sayisi} adet yaratıcı, "
                    "özgün ve uygulanabilir fikir üret. Her fikri numaralandır, bir cümlelik kısa "
                    "açıklama ekle. Türkçe yaz, kısa ve net ol."
                )
                cevap, hata = claude_yanit_al(
                    talimat, [{"role": "user", "content": konu}], yaraticilik, 800
                )
                sonuc = hata if hata and hata != "offline" else cevap
            st.session_state["son_uretilen_fikir"] = sonuc
        else:
            st.error("⚠️ Çekirdek çevrimdışı, fikir üretmek için API anahtarı gerekiyor.")

    if st.session_state.get("son_uretilen_fikir"):
        st.markdown(f'<div class="terminal-box">{st.session_state["son_uretilen_fikir"]}</div>', unsafe_allow_html=True)
        if st.button("📌 Bu Fikirleri Deftere Kaydet"):
            st.session_state.fikir_defteri.append({
                "konu": konu,
                "icerik": st.session_state["son_uretilen_fikir"],
            })
            st.success("Deftere eklendi!")

    if st.session_state.fikir_defteri:
        st.markdown("#### 📚 Kayıtlı Fikirler")
        for i, kayit in enumerate(reversed(st.session_state.fikir_defteri)):
            with st.expander(f"📌 {kayit['konu'][:60]}"):
                st.markdown(kayit["icerik"])

        tum_defter = "\n\n---\n\n".join(
            f"KONU: {k['konu']}\n\n{k['icerik']}" for k in st.session_state.fikir_defteri
        )
        st.download_button("📥 Tüm Defteri İndir", tum_defter, file_name="fikir_defteri.txt")

        if st.button("🗑️ Defteri Temizle"):
            st.session_state.fikir_defteri = []
            st.rerun()
