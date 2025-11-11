# app_web_bien_ban.py - Code Viết Biên Bản Hoàn Chỉnh (Phiên bản Streamlit Web)

import streamlit as st
from google import genai
import sys
import os

# ----------------------------------------------------
# 1. THIẾT LẬP API KEY (ĐỌC TỪ SECRETS CỦA STREAMLIT)
# ----------------------------------------------------
# Đọc Key từ st.secrets (Đây là cách duy nhất hoạt động trên Streamlit Cloud)
try:
    API_KEY = st.secrets.GEMINI_API_KEY
except AttributeError:
    # Nếu không tìm thấy, báo lỗi và dừng ứng dụng
    st.error("LỖI CẤU HÌNH: Không tìm thấy GEMINI_API_KEY.")
    st.info("Vui lòng thiết lập Key trong phần 'Secrets' của Streamlit Cloud theo cấu trúc: GEMINI_API_KEY = 'KEY_CỦA_BẠN'")
    st.stop() 

# Khởi tạo Client
client = genai.Client(api_key=API_KEY)


# ----------------------------------------------------
# 2. PROMPT CHUYÊN GIA (ĐÃ TÍCH HỢP)
# ----------------------------------------------------

# Giữ nguyên Prompt chi tiết của bạn trong biến system_instruction
system_instruction = """
Chatbot này là 1 chuyên gia trong lĩnh vực tạo báo cáo buổi họp của công ty bảo hiểm phi nhân thọ VBI Hồ Chí MInh với hơn 10 năm kinh nghiệm. Chatbot hỗ trợ soạn thảo báo cáo từ các ghi chú hoặc từ nội dung do người dùng cung cấp. Báo cáo được trình bày rõ ràng, chính xác có cấu trúc chuẩn gồm: thời gian họp, địa điểm họp, thành phần tham dự, nội dung chính của buổi họp, các quyết định, yêu cầu, hành động tiếp theo và người phụ trách thực hiện. Chatbot có thể viết biên bản bằng tiếng Việt hoặc tiếng Anh tuỳ theo yêu cầu. Chatbot giữ văn phong trang trọng, ngắn gọn và chính xác. Nếu thông tin chưa đầy đủ, chưa rõ, Chatbot sẽ chủ động hỏi lại để làm rõ trước khi soạn báo cáo.
Chatbot cũng hỗ trợ người dùng chuyển báo cáo sang các định dạng trình bày khác nhau, ví dụ: email tóm tắt, văn bản hành chính.

Nhiệm vụ 1: Phân tích và tổ chức thông tin đầu vào
- Xác định và phân loại thông tin chính từ nội dung thô.
- Nhận diện các yếu tố cốt lõi: thời gian, địa điểm, đối tượng.
- Phân chia nội dung thành: thảo luận, vấn đề nổi bật, ý kiến đóng góp, quyết định.
- Các thông tin được cung cấp có thể rời rạc nhưng phại tập hợp lại thành cùng đoạn văn bản nếu có cùng nội dung, cùng chủ đề.

Nhiệm vụ 2: Soạn thảo báo cáo họp theo định dạng chuẩn
- Gồm: Tiêu đề, thời gian, địa điểm, người tham dự, nội dung, kết luận, hành động tiếp theo.
- Sử dụng ngôn ngữ trang trọng, mạch lạc, hành chính, rõ ràng.
- Đảm bảo ngữ pháp, chính tả và định dạng thống nhất.

Nhiệm vụ 3: Tùy chỉnh định dạng báo cáo theo yêu cầu
- Chuyển báo cáo thành email, văn bản chính thức hoặc bản để trình bày.
- Điều chỉnh văn phong theo đối tượng người nhận.
- Tùy biến độ chi tiết theo yêu cầu.
- Không đề cập các định dạng tệp như word, excel, powerpoint.

Nhiệm vụ 4: Rà soát và tối ưu báo cáo
- Kiểm tra lỗi chính tả, ngữ pháp và logic tổng thể.
- Gợi ý cải thiện nội dung chưa rõ ràng.
- Đảm bảo thông tin không bị trùng lặp, mâu thuẫn.

Quy tắc hoạt động:
1. Chỉ sử dụng thông tin đã được xác minh từ người dùng, không tự suy luận, không bịa số liệu.
2. Luôn hỏi lại nếu thông tin chưa rõ ràng hoặc thiếu, cần thiết yêu cầu gửi biểu số liệu để phân tích. Các từ viết tắt chưa rõ phải hỏi và ghi nhớ cho lần sau
3. Văn phong hành chính, trang trọng, ngắn gọn.
4. Tôn trọng yêu cầu về gửi định dạng của người dùng.
5. Không xuất nội dung dưới dạng tệp hoặc mẫu định sẵn.
6. Đảm bảo tính logic, mạch lạc trong toàn bộ văn bản.
7. Giữ tính riêng tư và bảo mật nội dung cuộc họp.
"""

# ----------------------------------------------------
# 3. GIAO DIỆN STREAMLIT VÀ GỌI API
# ----------------------------------------------------

st.title("🤖 Trợ Lý Biên Bản Chuyên Nghiệp (VBI - Gemini)")
st.caption("Chuyên gia 10 năm kinh nghiệm trong lĩnh vực bảo hiểm phi nhân thọ.")

# Tạo hộp văn bản đầu vào trên web
meeting_notes = st.text_area(
    "Dán Toàn Bộ Nội Dung Cuộc Họp Thô vào ô dưới đây:", 
    height=300, 
    placeholder="Dán nội dung, ghi chú, hoặc các yêu cầu về báo cáo của bạn..."
)

# Nút kích hoạt Bot
if st.button("Soạn Thảo Báo Cáo"):
    if not meeting_notes:
        st.warning("Vui lòng dán nội dung cuộc họp trước khi nhấn nút.")
    else:
        # Khung loading
        with st.spinner("Đang gửi nội dung đến Gemini để xử lý..."):
            
            # Xây dựng nội dung cuối cùng cho mô hình
            full_prompt = system_instruction + "\n\nNỘI DUNG CUỘC HỌP CẦN TÓM TẮT:\n---\n" + meeting_notes + "\n---"
            
            try:
                # Gọi API
                response = client.models.generate_content(
                    model='gemini-2.5-pro', # Dùng Pro cho tác vụ phức tạp
                    contents=full_prompt,
                    config={
                        "temperature": 0.1
                    }
                )
                
                # Hiển thị kết quả trên giao diện web
                st.subheader("✅ Báo Cáo Buổi Họp Hoàn Chỉnh")
                st.markdown(response.text) # Hiển thị kết quả dưới dạng Markdown
                
            except Exception as e:
                st.error(f"Lỗi Kết Nối hoặc Xác Thực: {e}")
