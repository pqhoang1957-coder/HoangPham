# app_web_bien_ban.py - Trợ Lý Viết Biên Bản (Hỗ trợ Text và Ghi Âm)

import streamlit as st
from google import genai
import sys
import os

# ----------------------------------------------------
# 1. THIẾT LẬP API KEY VÀ CLIENT
# ----------------------------------------------------
# Đọc Key từ st.secrets
try:
    # Đã sửa lỗi canh lề
    API_KEY = st.secrets.GEMINI_API_KEY
except AttributeError:
    # Đã sửa lỗi canh lề
    st.error("LỖI CẤU HÌNH: Không tìm thấy GEMINI_API_KEY trong Streamlit Secrets.")
    st.stop() 

# Khởi tạo Client
client = genai.Client(api_key=API_KEY)


# ----------------------------------------------------
# 2. PROMPT CHUYÊN GIA
# ----------------------------------------------------
system_instruction = """
Chatbot này là 1 chuyên gia trong lĩnh vực tạo báo cáo buổi họp của công ty bảo hiểm phi nhân thọ VBI Hồ Chí MInh với hơn 10 năm kinh nghiệm. Chatbot hỗ trợ soạn thảo báo cáo từ các ghi chú, nội dung dán hoặc từ **file ghi âm được phiên âm**. Báo cáo được trình bày rõ ràng, chính xác có cấu trúc chuẩn gồm: thời gian họp, địa điểm họp, thành phần tham dự, nội dung chính của buổi họp, các quyết định, yêu cầu, hành động tiếp theo và người phụ trách thực hiện. Chatbot giữ văn phong trang trọng, ngắn gọn và chính xác. Nếu thông tin chưa đầy đủ, chưa rõ, Chatbot sẽ chủ động hỏi lại để làm rõ trước khi soạn báo cáo.

Nhiệm vụ 1: Phân tích và tổ chức thông tin đầu vào
- Xác định và phân loại thông tin chính từ nội dung thô hoặc **file ghi âm**.
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
st.caption("Xử lý Biên Bản từ Văn bản hoặc File Ghi Âm (MP3/WAV/FLAC).")

# --- 1. Hộp tải file Ghi Âm --- (Bỏ dấu '---' để tránh lỗi cú pháp)
# [1] CHÚ THÍCH PHẢI DÙNG DẤU '#'
st.markdown("### Tùy chọn 1: Tải file ghi âm") 
uploaded_file = st.file_uploader(
    "Tải lên file ghi âm cuộc họp (.mp3, .wav, .flac)",
    type=["mp3", "wav", "flac"]
)

st.markdown("---") # Đường kẻ ngang để phân chia giao diện

# --- 2. Hộp dán văn bản --- (Bỏ dấu '---')
# [2] CHÚ THÍCH PHẢI DÙNG DẤU '#'
st.markdown("### Tùy chọn 2: Dán văn bản")
meeting_notes = st.text_area(
    "HOẶC Dán Nội Dung Cuộc Họp Thô vào ô dưới đây:",
    height=200,
    placeholder="Chỉ dùng khi không tải file ghi âm."
)

# --- 3. LOGIC XỬ LÝ CHÍNH ---
if st.button("Soạn Thảo Báo Cáo"):
    
    if uploaded_file is None and not meeting_notes.strip():
        # Lỗi nếu không có input nào
        st.warning("Vui lòng tải lên file ghi âm HOẶC dán nội dung cuộc họp.")
        st.stop()
    
    # Khối logic chính
    with st.spinner("Đang xử lý nội dung..."):
        
        file = None
        
        try:
            # --- ƯU TIÊN 1: Xử lý File Ghi Âm ---
            if uploaded_file is not None:
                st.info("Phát hiện file ghi âm. Đang ưu tiên phiên âm và tóm tắt file...")
                
                # Đã sửa lỗi cú pháp 'mime_type' và 'display_name'
                file = client.files.upload(file=uploaded_file) 
                
               
                # Nội dung sẽ bao gồm Prompt + File
                full_prompt_contents = [
                    system_instruction, 
                    file, 
                    "Bây giờ, hãy tạo báo cáo họp/biên bản dựa trên nội dung được **phiên âm** từ file ghi âm này."
                ]
                model_to_use = 'gemini-2.5-pro' # Dùng Pro cho Audio
                
            # --- ƯU TIÊN 2: Xử lý Văn bản Dán ---
            elif meeting_notes.strip(): # Mức thụt lề đã đúng
                st.info("Phát hiện văn bản dán. Đang xử lý nội dung thô...")
                # Nội dung chỉ là chuỗi văn bản
                full_prompt_contents = system_instruction + "\n\nNỘI DUNG CUỘC HỌP CẦN TÓM TẮT:\n---\n" + meeting_notes + "\n---"
                model_to_use = 'gemini-2.5-flash' # Dùng Flash cho Văn bản
            
            # --- Gọi API ---
            # Khối này đã cùng mức thụt lề với if/elif
            response = client.models.generate_content(
                model=model_to_use,
                contents=full_prompt_contents,
                config={"temperature": 0.1}
            )
            
            st.subheader("✅ Báo Cáo Buổi Họp Hoàn Chỉnh")
            st.markdown(response.text)
            
        except Exception as e:
            st.error(f"Lỗi Kết Nối hoặc Xác Thực: {e}")
            st.error("Vui lòng kiểm tra file audio có bị hỏng hay không, hoặc thử lại sau (Lỗi quá tải server 503).")
            
        finally:
            # Xóa file khỏi máy chủ nếu file đã được tải lên
            if file is not None:
                client.files.delete(name=file.name)
                st.success("Đã dọn dẹp file tạm trên máy chủ Gemini.")









