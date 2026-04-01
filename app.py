import streamlit as st
from PIL import Image
import google.generativeai as genai
import os
from dotenv import load_dotenv

# ======================
# PAGE CONFIG
# ======================
st.set_page_config(
    layout="wide",
    page_title="MediLens AI",
    page_icon="🩺"
)

# ======================
# SESSION STATE
# ======================
if "page" not in st.session_state:
    st.session_state.page = "home"

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None

if "messages" not in st.session_state:
    st.session_state.messages = []

# ======================
# LOAD API
# ======================
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        api_key = None

if api_key:
    genai.configure(api_key=api_key)

# ======================
# LANGUAGE & TEXTS DICT
# ======================
# Language Selector at the very top right
col_empty, col_lang = st.columns([8, 1.5])
with col_lang:
    lang_choice = st.selectbox("", ["English", "العربية"], label_visibility="collapsed")
    lang = "ar" if lang_choice == "العربية" else "en"

texts = {
    "nav_home": {"en": "Home", "ar": "الرئيسية"},
    "nav_about": {"en": "About", "ar": "عن التطبيق"},
    "nav_features": {"en": "Features", "ar": "المميزات"},
    "tagline": {"en": "Smart Medical Report Reader", "ar": "القارئ الذكي للتقارير الطبية"},
    "hero_badge": {"en": "AI-powered • Patient-friendly • Medical clarity", "ar": "مدعوم بالذكاء الاصطناعي • صديق للمريض • وضوح طبي"},
    "hero_title": {"en": "Understand your medical reports without confusion.", "ar": "افهم تقاريرك الطبية بدون حيرة أو تعقيد."},
    "hero_sub": {
        "en": "Many patients struggle to understand laboratory reports because of technical terms. MediLens AI helps by extracting important values, explaining them clearly, and answering follow-up questions.",
        "ar": "يعاني الكثير من المرضى من صعوبة فهم التقارير المخبرية بسبب المصطلحات المعقدة. تطبيقنا يساعدك في استخراج القيم المهمة، وشرحها بوضوح، والإجابة على استفساراتك الطبية."
    },
    "pill_1": {"en": "Easy to use", "ar": "سهل الاستخدام"},
    "pill_2": {"en": "Built for patients and professionals", "ar": "مصمم للمرضى والمختصين"},
    "pill_3": {"en": "AI summary + smart chat", "ar": "ملخص ذكي + محادثة تفاعلية"},
    "pill_4": {"en": "Faster understanding", "ar": "فهم أسرع للنتائج"},
    "sec_why_title": {"en": "Why this service matters", "ar": "لماذا هذه الخدمة مهمة؟"},
    "sec_why_sub": {"en": "Medical reports often contain complex values difficult to understand quickly.", "ar": "التقارير الطبية غالباً ما تحتوي على قيم ومصطلحات يصعب على غير المختص فهمها بسرعة."},
    "card1_title": {"en": "The Problem", "ar": "المشكلة"},
    "card1_text": {"en": "Lab reports full of abbreviations create stress and confusion.", "ar": "التقارير المليئة بالاختصارات الطبية والأرقام تسبب القلق والحيرة للمرضى."},
    "card2_title": {"en": "The Service", "ar": "الخدمة"},
    "card2_text": {"en": "Our AI reads images, extracts values, and provides a smart chat assistant.", "ar": "يقرأ الذكاء الاصطناعي صور التحاليل، ويشرحها، ويوفر مستشاراً للإجابة على الأسئلة."},
    "card3_title": {"en": "Why It Helps", "ar": "الفائدة"},
    "card3_text": {"en": "Saves time, reduces confusion, and makes medical info accessible.", "ar": "توفير الوقت، وتقليل القلق، وجعل المعلومات الطبية في متناول الجميع بسهولة."},
    "about_title": {"en": "About Us", "ar": "عن التطبيق"},
    "about_text": {
        "en": "MediLens AI is designed as a smart medical support tool that bridges the gap between complex medical reports and everyday understanding.<br><br>This platform is intended for informational support only and does not replace professional medical consultation.",
        "ar": "تم تصميم MediLens AI ليكون أداة دعم طبي ذكية تسد الفجوة بين التقارير المعقدة والفهم اليومي المبسط. <br><br>هذه المنصة مخصصة للاسترشاد والدعم المعلوماتي فقط، ولا تغني أبداً عن الاستشارة الطبية المتخصصة."
    },
    "cta_title": {"en": "Ready to try the smart reader?", "ar": "جاهز لتجربة القارئ الذكي؟"},
    "cta_text": {"en": "Move to the analysis page and upload your report in seconds.", "ar": "انتقل لصفحة التحليل وارفع تقريرك الطبي في ثوانٍ معدودة."},
    "btn_open": {"en": "🚀 Open the App", "ar": "🚀 افتح التطبيق الآن"},
    "btn_back": {"en": "⬅ Back Home", "ar": "⬅ العودة للرئيسية"},
    "app_title": {"en": "Upload your report", "ar": "ارفع تقريرك الطبي"},
    "app_sub": {"en": "Upload a medical report image to extract key values and get an AI explanation.", "ar": "قم برفع صورة التقرير لاستخراج القيم الأساسية والحصول على شرح ذكي مبسط."},
    "upload_lbl": {"en": "Upload medical report", "ar": "ارفع صورة التقرير الطبي (JPG, PNG)"},
    "preview_title": {"en": "Preview", "ar": "معاينة الصورة"},
    "options_title": {"en": "Analysis Options", "ar": "خيارات التحليل"},
    "options_sub": {"en": "Choose the explanation style.", "ar": "اختر أسلوب الشرح المناسب لك."},
    "mode_lbl": {"en": "Explanation mode", "ar": "نمط الشرح:"},
    "modes": {"en": ["Simple explanation", "Scientific explanation"], "ar": ["شرح مبسط (للمريض)", "شرح علمي (للمختص)"]},
    "analyze_btn": {"en": "Analyze Report", "ar": "بدء تحليل التقرير"},
    "spinner": {"en": "Analyzing report...", "ar": "جاري تحليل التقرير وفهم البيانات..."},
    "error_not_med": {"en": "The uploaded image is not recognized as a medical report.", "ar": "⛔ الصورة المرفقة لا تبدو كتقرير طبي. يرجى التحقق."},
    "result_title": {"en": "Analysis Results", "ar": "نتائج التحليل"},
    "chat_title": {"en": "Smart Medical Chat", "ar": "المحادثة الطبية الذكية"},
    "chat_sub": {"en": "Ask questions related to the uploaded report.", "ar": "اسأل أي سؤال يتعلق بالتقرير المرفق."},
    "chat_hint": {"en": "Ask about your report...", "ar": "اكتب سؤالك هنا..."},
    "chat_spin": {"en": "Thinking...", "ar": "جاري التفكير..."}
}

# ======================
# DYNAMIC CSS (RTL/LTR)
# ======================
font_family = "'Tajawal', sans-serif" if lang == 'ar' else "'Inter', sans-serif"
direction = "rtl" if lang == 'ar' else "ltr"
text_align = "right" if lang == 'ar' else "left"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800&display=swap');

html, body, [class*="css"] {{
    font-family: {font_family} !important;
}}

.stApp {{
    background:
        radial-gradient(circle at top left, rgba(37,99,235,0.15), transparent 25%),
        radial-gradient(circle at top right, rgba(245,158,11,0.10), transparent 20%),
        linear-gradient(180deg, #081120 0%, #0B1324 100%);
    color: #F8FAFC;
    direction: {direction};
    text-align: {text_align};
}}

.block-container {{
    padding-top: 3.5rem; 
    padding-bottom: 3rem;
    max-width: 1280px;

}}

header[data-testid="stHeader"] {{ background: transparent; }}
section[data-testid="stSidebar"] {{ display: none; }}

/* Navbar */
.navbar {{
    width: 100%; height: 84px; display: flex; justify-content: space-between; align-items: center;
    padding: 0 10px; border-bottom: 1px solid rgba(255,255,255,0.08); background: rgba(8,17,32,0.45); backdrop-filter: blur(8px);
}}
.brand-wrap {{ display: flex; align-items: center; gap: 14px; }}
.brand-logo {{
    width: 44px; height: 44px; border-radius: 14px;
    background: linear-gradient(135deg, #2563EB 0%, #38BDF8 60%, #F59E0B 100%);
    display: flex; align-items: center; justify-content: center; font-size: 24px; box-shadow: 0 10px 24px rgba(37,99,235,0.25);
}}
.brand-text {{ display: flex; flex-direction: column; }}
.brand-name {{ font-size: 1.3rem; font-weight: 800; color: #FFFFFF; line-height: 1.1; }}
.brand-tag {{ font-size: 0.86rem; color: #94A3B8; }}
.nav-links {{ display: flex; gap: 24px; align-items: center; color: #CBD5E1; font-weight: 500; font-size: 0.98rem; }}

/* Hero */
.hero {{ padding: 70px 0 50px 0; }}
.hero-box {{
    background: linear-gradient(135deg, rgba(255,255,255,0.04), rgba(255,255,255,0.02));
    border: 1px solid rgba(255,255,255,0.08); border-radius: 32px; padding: 60px 42px; box-shadow: 0 20px 60px rgba(0,0,0,0.20);
}}
.badge {{
    display: inline-block; background: rgba(56,189,248,0.12); color: #7DD3FC; border: 1px solid rgba(125,211,252,0.25);
    padding: 8px 14px; border-radius: 999px; font-size: 0.9rem; font-weight: 600; margin-bottom: 18px;
}}
.hero-title {{ font-size: 3.8rem; line-height: 1.15; font-weight: 800; margin-bottom: 18px; color: #F8FAFC; }}
.hero-subtitle {{ font-size: 1.18rem; line-height: 1.9; color: #CBD5E1; max-width: 760px; margin-bottom: 28px; }}
.hero-points {{ display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 28px; }}
.point-pill {{
    background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.08); color: #E2E8F0;
    border-radius: 999px; padding: 10px 14px; font-size: 0.94rem; font-weight: 600;
}}

.section-title {{ font-size: 2.2rem; font-weight: 800; color: #FFFFFF; margin: 50px 0 18px 0; }}
.section-sub {{ color: #94A3B8; font-size: 1.05rem; margin-bottom: 26px; line-height: 1.8; }}

/* Cards */
.info-card {{
    background: linear-gradient(180deg, #F8FAFC 0%, #EFF6FF 100%); border: 1px solid #DBEAFE;
    border-radius: 26px; padding: 26px; min-height: 230px; box-shadow: 0 16px 30px rgba(0,0,0,0.10);
}}
.info-icon {{
    width: 54px; height: 54px; border-radius: 16px; background: linear-gradient(135deg, #2563EB, #38BDF8);
    display: flex; align-items: center; justify-content: center; color: white; font-size: 24px; margin-bottom: 18px;
}}
.info-title {{ color: #0F172A; font-size: 1.22rem; font-weight: 800; margin-bottom: 10px; }}
.info-text {{ color: #334155; line-height: 1.9; font-size: 1rem; }}

/* About & CTA */
.about-box {{
    background: linear-gradient(135deg, rgba(37,99,235,0.18), rgba(14,165,233,0.10)); border: 1px solid rgba(125,211,252,0.20);
    border-radius: 30px; padding: 34px; color: #E2E8F0; line-height: 2; font-size: 1.05rem;
}}
.cta-box {{
    margin-top: 40px; background: linear-gradient(135deg, #1D4ED8 0%, #0EA5E9 100%); border-radius: 30px;
    padding: 34px; text-align: center; color: white; box-shadow: 0 20px 45px rgba(29,78,216,0.28);
}}
.cta-title {{ font-size: 2rem; font-weight: 800; margin-bottom: 10px; }}
.cta-text {{ font-size: 1.05rem; opacity: 0.95; margin-bottom: 22px; }}

/* Buttons */
.stButton > button {{
    background: linear-gradient(135deg, #F59E0B, #FBBF24) !important; color: #111827 !important;
    border: none !important; border-radius: 16px !important; font-weight: 800 !important;
    padding: 0.9rem 1.4rem !important; box-shadow: 0 10px 24px rgba(245,158,11,0.25);
}}
.stButton > button:hover {{ background: linear-gradient(135deg, #E69008, #F59E0B) !important; color: #111827 !important; }}

/* App page */
.app-shell {{ padding-top: 28px; }}
.app-card {{
    background: linear-gradient(180deg, #FFFFFF 0%, #F8FAFC 100%); border: 1px solid #E2E8F0;
    border-radius: 26px; padding: 28px; box-shadow: 0 18px 40px rgba(0,0,0,0.12); margin-bottom: 22px; direction: {direction};
}}
.app-title {{ color: #0F172A; font-size: 1.55rem; font-weight: 800; margin-bottom: 10px; }}
.app-sub {{ color: #475569; line-height: 1.8; margin-bottom: 16px; }}
[data-testid="stFileUploadDropzone"] {{
    background: linear-gradient(180deg, #FFFFFF 0%, #F8FAFC 100%); border: 2px dashed #60A5FA; border-radius: 18px; padding: 30px;
}}
[data-testid="stFileUploadDropzone"]:hover {{ background: #EFF6FF; border-color: #2563EB; }}
.stRadio label, .stMarkdown, p, span {{ color: inherit !important; }}
.result-box {{ background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 20px; padding: 20px; color: #0F172A; text-align: {text_align}; }}

@media (max-width: 900px) {{
    .hero-title {{ font-size: 2.5rem; }}
    .section-title {{ font-size: 1.7rem; }}
}}
</style>
""", unsafe_allow_html=True)

# ======================
# HOME PAGE
# ======================
if st.session_state.page == "home":
    st.markdown(f"""
    <div class="navbar" dir="{direction}">
        <div class="brand-wrap">
            <div class="brand-logo">🩺</div>
            <div class="brand-text">
                <div class="brand-name">MediLens AI</div>
                <div class="brand-tag">{texts["tagline"][lang]}</div>
            </div>
        </div>
        <div class="nav-links">
            <span>{texts["nav_home"][lang]}</span>
            <span>{texts["nav_about"][lang]}</span>
            <span>{texts["nav_features"][lang]}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="hero" dir="{direction}">
        <div class="hero-box">
            <div class="badge">{texts["hero_badge"][lang]}</div>
            <div class="hero-title">{texts["hero_title"][lang]}</div>
            <div class="hero-subtitle">{texts["hero_sub"][lang]}</div>
            <div class="hero-points">
                <div class="point-pill">{texts["pill_1"][lang]}</div>
                <div class="point-pill">{texts["pill_2"][lang]}</div>
                <div class="point-pill">{texts["pill_3"][lang]}</div>
                <div class="point-pill">{texts["pill_4"][lang]}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f'<div class="section-title" dir="{direction}">{texts["sec_why_title"][lang]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-sub" dir="{direction}">{texts["sec_why_sub"][lang]}</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div class="info-card" dir="{direction}">
            <div class="info-icon">📄</div>
            <div class="info-title">{texts["card1_title"][lang]}</div>
            <div class="info-text">{texts["card1_text"][lang]}</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="info-card" dir="{direction}">
            <div class="info-icon">🧠</div>
            <div class="info-title">{texts["card2_title"][lang]}</div>
            <div class="info-text">{texts["card2_text"][lang]}</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="info-card" dir="{direction}">
            <div class="info-icon">⚡</div>
            <div class="info-title">{texts["card3_title"][lang]}</div>
            <div class="info-text">{texts["card3_text"][lang]}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f'<div class="section-title" dir="{direction}">{texts["about_title"][lang]}</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="about-box" dir="{direction}">
        {texts["about_text"][lang]}
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="cta-box" dir="{direction}">
        <div class="cta-title">{texts["cta_title"][lang]}</div>
        <div class="cta-text">{texts["cta_text"][lang]}</div>
    </div>
    """, unsafe_allow_html=True)

    col_btn1, col_btn2, col_btn3 = st.columns([2,1,2])
    with col_btn2:
        st.write("") # Spacer
        if st.button(texts["btn_open"][lang], use_container_width=True):
            st.session_state.page = "app"
            st.rerun()

# ======================
# APP PAGE
# ======================
elif st.session_state.page == "app":
    st.markdown('<div class="app-shell">', unsafe_allow_html=True)

    top1, top2 = st.columns([5,1])
    with top1:
        st.markdown(f"""
        <div class="brand-wrap" style="margin-bottom:20px;" dir="{direction}">
            <div class="brand-logo">🩺</div>
            <div class="brand-text">
                <div class="brand-name">MediLens AI</div>
                <div class="brand-tag">{texts["tagline"][lang]}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with top2:
        if st.button(texts["btn_back"][lang], use_container_width=True):
            st.session_state.page = "home"
            st.rerun()

    st.markdown(f"""
    <div class="app-card">
        <div class="app-title">{texts["app_title"][lang]}</div>
        <div class="app-sub">{texts["app_sub"][lang]}</div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(texts["upload_lbl"][lang], type=["jpg", "jpeg", "png"])
    st.markdown("</div>", unsafe_allow_html=True)

    if uploaded_file is not None and api_key:
        image = Image.open(uploaded_file)

        left, right = st.columns([1, 1.1])

        with left:
            st.markdown(f"""
            <div class="app-card">
                <div class="app-title">{texts["preview_title"][lang]}</div>
            """, unsafe_allow_html=True)
            st.image(image, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with right:
            st.markdown(f"""
            <div class="app-card">
                <div class="app-title">{texts["options_title"][lang]}</div>
                <div class="app-sub">{texts["options_sub"][lang]}</div>
            """, unsafe_allow_html=True)

            mode_options = texts["modes"][lang]
            mode = st.radio(
                texts["mode_lbl"][lang],
                mode_options,
                horizontal=True
            )

            if st.button(texts["analyze_btn"][lang], use_container_width=True):
                with st.spinner(texts["spinner"][lang]):
                    try:
                        model = genai.GenerativeModel('models/gemini-flash-latest')
                        
                        # Dynamic Prompt based on Language & Mode
                        p_lang = "Arabic" if lang == "ar" else "English"
                        style = "simple patient-friendly language" if mode == mode_options[0] else "professional medical language"
                        
                        prompt = f"""
                        You are a strict medical AI assistant.
                        1. Check whether the uploaded image is a medical report or lab result.
                        2. If NOT, respond ONLY with exactly: ERROR_NOT_MEDICAL
                        3. If YES, explain it in {p_lang} using {style}.
                        4. Extract the top 5 important values in a Markdown table.
                        5. Add a short disclaimer that this tool is for informational purposes only.
                        """
                        
                        res = model.generate_content([prompt, image])
                        st.session_state.analysis_result = res.text
                    except Exception as e:
                        st.error(str(e))

            st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.analysis_result:
        st.markdown(f"""
        <div class="app-card">
            <div class="app-title">{texts["result_title"][lang]}</div>
            <div class="result-box" dir="{direction}">
        """, unsafe_allow_html=True)

        if "ERROR_NOT_MEDICAL" in st.session_state.analysis_result:
            st.error(texts["error_not_med"][lang])
        else:
            st.markdown(st.session_state.analysis_result)

        st.markdown("</div></div>", unsafe_allow_html=True)

    if st.session_state.analysis_result and "ERROR_NOT_MEDICAL" not in st.session_state.analysis_result:
        st.markdown(f"""
        <div class="app-card">
            <div class="app-title">{texts["chat_title"][lang]}</div>
            <div class="app-sub">{texts["chat_sub"][lang]}</div>
        """, unsafe_allow_html=True)

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if q := st.chat_input(texts["chat_hint"][lang]):
            st.session_state.messages.append({"role": "user", "content": q})

            with st.chat_message("user"):
                st.markdown(q)

            with st.chat_message("assistant"):
                with st.spinner(texts["chat_spin"][lang]):
                    try:
                        chat_model = genai.GenerativeModel('models/gemini-flash-latest')
                        p_lang = "Arabic" if lang == "ar" else "English"
                        
                        # Strict Medical Context Prompt
                        full_prompt = f"""
                        You are a strict medical AI assistant.
                        Rule: ONLY answer questions related to the uploaded medical report or general health context. 
                        If the user asks about travel, coding, or anything outside health, apologize and state you are a medical bot.

                        Context (Report Analysis):
                        {st.session_state.analysis_result}

                        User question:
                        {q}

                        Reply briefly and clearly in {p_lang}.
                        """
                        ans = chat_model.generate_content([full_prompt])
                        st.markdown(ans.text)
                        st.session_state.messages.append({"role": "assistant", "content": ans.text})
                    except Exception as e:
                        st.error(str(e))

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

else:
    if not api_key:
        st.error("Gemini API key is missing. Please add it to your environment variables or Streamlit secrets.")
