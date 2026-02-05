import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
from dotenv import load_dotenv

# 1. إعداد المفتاح
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# 2. إعداد الصفحة
st.set_page_config(page_title="مفسر التحاليل الطبية", layout="wide", page_icon="🩺")

# --- تهيئة الذاكرة (للحفاظ على التحليل والشات) ---
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- القائمة الجانبية (Sidebar) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3063/3063176.png", width=100)
    st.title("عن التطبيق")
    st.info("""
    هذا التطبيق يستخدم الذكاء الاصطناعي لقراءة التحاليل وشرحها، مع إمكانية الدردشة حول النتائج.
    """)
    
    # زر لإعادة ضبط كل شيء
    if st.button("🗑️ تحليل جديد"):
        st.session_state.analysis_result = None
        st.session_state.messages = []
        st.rerun()
        
    st.write("---")
    st.write("👩‍💻 **تطوير:** هيفاء")
    st.error("⚠️ **تنبيه:** النتائج للاسترشاد فقط.")

# --- الواجهة الرئيسية ---
st.title("🔬 مفسر التقارير الطبية الذكي")
st.markdown("---")

# رفع الملف
uploaded_file = st.file_uploader("قم برفع صورة التحليل هنا (JPG, PNG)...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    
    # تقسيم الشاشة (الصورة يمين - والخيارات يسار)
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.image(image, caption="الصورة المرفقة", use_container_width=True)
    
    with col2:
        # إذا لم يكن هناك تحليل محفوظ، اعرض زر التحليل
        if st.session_state.analysis_result is None:
            st.write("### ⚙️ خيارات التحليل:")
            mode = st.radio("كيف تريد شرح النتائج؟", ["شرح مبسط (عامي وسهل)", "شرح علمي (مفصل)"])
            
            if st.button("تحليل النتائج الآن ⚡", type="primary"):
                model = genai.GenerativeModel('models/gemini-flash-latest')
                
                with st.spinner('جاري قراءة الأرقام وفهم الرموز الطبية...'):
                    try:
                        style_instruction = "استخدم لغة بسيطة جداً ومطمئنة." if mode == "شرح مبسط (عامي وسهل)" else "استخدم مصطلحات طبية دقيقة."
                        
                        prompt = f"""
                        أنت خبير طبي. {style_instruction}
                        من الصورة المرفقة:
                        1. أنشئ جدولاً بالنتائج (الاسم | القيمة | الحالة ✅/⚠️).
                        2. اكتب ملخصاً سريعاً لأهم الملاحظات.
                        """
                        
                        response = model.generate_content([prompt, image])
                        
                        # حفظ النتيجة في الذاكرة لكي لا تختفي
                        st.session_state.analysis_result = response.text
                        st.rerun() # تحديث الصفحة لإظهار النتيجة
                        
                    except Exception as e:
                        st.error(f"حدث خطأ: {e}")

        # إذا كانت النتيجة موجودة، اعرضها
        else:
            st.success("✅ تم التحليل بنجاح!")
            st.markdown("### 📋 تقرير النتائج:")
            st.markdown(st.session_state.analysis_result)

    # --- قسم الدردشة (يظهر فقط بعد التحليل) ---
    if st.session_state.analysis_result is not None:
        st.markdown("---")
        st.subheader("💬 دكتور، عندي استفسار...")
        
        # عرض المحادثة السابقة
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # خانة السؤال
        if user_question := st.chat_input("اكتب سؤالك هنا (مثلاً: ما هو العلاج الغذائي المناسب؟)"):
            
            # عرض سؤال المستخدم
            st.session_state.messages.append({"role": "user", "content": user_question})
            with st.chat_message("user"):
                st.markdown(user_question)

            # جلب الإجابة
            with st.chat_message("assistant"):
                with st.spinner("جاري الكتابة..."):
                    model = genai.GenerativeModel('models/gemini-flash-latest')
                    
                    # نرسل له سياق المحادثة + الصورة
                    chat_prompt = f"""
                    أنت خبير طبي. المستخدم يسأل عن التحليل المرفق في الصورة.
                    سؤال المستخدم: {user_question}
                    أجب باختصار وبطريقة مفيدة.
                    """
                    response = model.generate_content([chat_prompt, image])
                    
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})