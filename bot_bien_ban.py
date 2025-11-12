# app_web_bien_ban.py - Trợ Lý Viết Biên Bản (Phiên bản TEXT ONLY)

import streamlit as st
from google import genai
import sys
import os

# ----------------------------------------------------
# 1. THIẾT LẬP API KEY VÀ CLIENT
# ----------------------------------------------------
# Đọc Key từ st.secrets (Cần thiết lập trong Streamlit Cloud)
try:
    API_KEY = st.secrets.GEMINI_API_KEY
except AttributeError:
    st.error("LỖI CẤU HÌNH: Không tìm thấy GEMINI_API_KEY trong Streamlit Secrets.")
    st.stop() 

# Khởi tạo Client
client = genai.Client(api_key=API_KEY)


# ----------------------------------------------------
# 2. PROMPT CHUYÊN GIA
# ----------------------------------------------------
system_instruction = """
Chatbot này là 1 chuyên gia trong lĩnh vực tạo báo cáo buổi họp của công ty bảo hiểm phi nhân thọ VBI Hồ Chí MInh với hơn 10 năm kinh nghiệm. Chatbot hỗ trợ soạn thảo báo cáo từ các ghi chú hoặc nội dung dán. Báo cáo được trình bày rõ ràng, chính xác có cấu trúc chuẩn gồm: thời gian họp, địa điểm họp, thành phần tham dự, nội dung chính của buổi họp, các quyết định, yêu cầu, hành động tiếp theo và người phụ trách thực hiện. Chatbot giữ văn phong trang trọng, ngắn gọn và chính xác. Nếu thông tin chưa đầy đủ, chưa rõ, Chatbot sẽ chủ động hỏi lại để làm rõ trước khi soạn báo cáo.

Nhiệm vụ 1: Phân tích và tổ chức thông tin đầu vào
- Xác định và phân loại thông tin chính từ nội dung thô.
- Nhận diện các yếu tố cốt lõi: thời gian, địa điểm, đối tượng.
- Phân chia nội dung thành: thảo luận, vấn đề nổi bật, ý kiến đóng góp, quyết định.
- Các thông tin được cung cấp có thể rời rạc nhưng phải tập hợp lại thành cùng đoạn văn bản nếu có cùng nội dung, cùng chủ đề.

Nhiệm vụ 2: Soạn thảo báo cáo họp theo định dạng chuẩn
- Gồm: Tiêu đề, thời gian, địa điểm, người tham dự, nội dung, kết luận, hành động tiếp theo.
- Sử dụng ngôn ngữ trang trọng, mạch lạc, hành chính, rõ ràng.

Quy tắc hoạt động:
1. Chỉ sử dụng thông tin đã được xác minh từ người dùng, không suy diễn, bịa đặt.
2. Luôn hỏi lại nếu thông tin chưa rõ ràng hoặc thiếu.
3. Văn phong hành chính, trang trọng, ngắn gọn.
4. Đảm bảo tính logic, mạch lạc trong toàn bộ văn bản.
"""

# ----------------------------------------------------
# 3. GIAO DIỆN STREAMLIT VÀ GỌI API
# ----------------------------------------------------

st.title("🤖 Trợ Lý Biên Bản (VBI HCM - Gemini)")
st.caption("Công cụ chỉ xử lý Văn bản. Vui lòng dán nội dung đã được phiên âm.")

# Bổ sung câu hướng dẫn của bạn
st.info("⚠️ Nếu bạn có file MP3, hãy dùng Google **NotebookLM** để chuyển đổi sang văn bản rồi dán vào đây. Xin lỗi vì sự bất tiện này.")

# --- Hộp dán văn bản ---
meeting_notes = st.text_area(
    "Dán Toàn Bộ Nội Dung Cuộc Họp Thô vào ô dưới đây:", 
    height=300, 
    placeholder="Dán nội dung, ghi chú, hoặc các yêu cầu về báo cáo của bạn..."
)


# --- LOGIC XỬ LÝ CHÍNH ---
if st.button("Soạn Thảo Báo Cáo"):
    
    if not meeting_notes.strip():
        st.warning("Vui lòng dán nội dung cuộc họp trước khi nhấn nút.")
        st.stop()
    
    # Khối loading
    with st.spinner("Đang xử lý nội dung..."):
        
        try:
            # Xây dựng nội dung cuối cùng cho mô hình
            full_prompt = system_instruction + "\n\nNỘI DUNG CUỘC HỌP CẦN TÓM TẮT:\n---\n" + meeting_notes + "\n---"
            
            # Gọi API
            response = client.models.generate_content(
                model='gemini-2.5-flash', # Dùng Flash cho Text (Nhanh và hiệu quả)
                contents=full_prompt,
                config={"temperature": 0.1}
            )
            
            # Hiển thị kết quả
            st.subheader("✅ Báo Cáo Buổi Họp Hoàn Chỉnh")
            st.markdown(response.text)
            
        except Exception as e:
            st.error(f"Lỗi Kết Nối hoặc Xác Thực: {e}")
            st.error("Vui lòng kiểm tra lại API Key hoặc thử lại sau (Lỗi quá tải server 503).")
