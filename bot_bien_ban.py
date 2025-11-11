# bot_bien_ban.py - Code Viết Biên Bản Hoàn Chỉnh (Dùng cho đóng gói .exe)

# ----------------------------------------------------
# 1. THIẾT LẬP API KEY (ĐỌC TỪ SECRETS CỦA STREAMLIT)
# ----------------------------------------------------
import streamlit as st
from google import genai
import sys
import os

# Cố gắng đọc Key từ Streamlit Secrets
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except KeyError:
    st.error("LỖI CẤU HÌNH: Không tìm thấy GEMINI_API_KEY trong Streamlit Secrets.")
    st.info("Vui lòng thiết lập GEMINI_API_KEY trong phần 'Settings' > 'Secrets' của Streamlit Cloud.")
    st.stop() # Dừng ứng dụng nếu không có Key

# Khởi tạo Client
client = genai.Client(api_key=API_KEY)


# ----------------------------------------------------
# 2. PROMPT VÀ NHẬN DỮ LIỆU ĐẦU VÀO
# ----------------------------------------------------

print("--- Công cụ Viết Biên Bản Cuộc Họp (Gemini) ---")

# Lệnh input() phải nằm ngoài khối try/except chính để đảm bảo hiển thị
print("\nVui lòng dán toàn bộ nội dung cuộc họp thô vào đây (Trên MỘT DÒNG và nhấn ENTER):")
try:
    meeting_notes = input("Nội dung: ") 
    if not meeting_notes.strip():
        print("Không có dữ liệu đầu vào. Chương trình sẽ thoát.")
        input("\nNhấn ENTER để đóng cửa sổ...")
        sys.exit(1)

except Exception as e:
    # Nếu có lỗi khi nhập liệu, dừng lại
    print(f"Lỗi nhập liệu: {e}")
    input("\nNhấn ENTER để đóng cửa sổ...")
    sys.exit(1)


# Prompt yêu cầu biên bản (Giữ nguyên)
system_prompt = f"""
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

NỘI DUNG CUỘC HỌP CẦN TÓM TẮT:
---
{meeting_notes}
---
"""

# ----------------------------------------------------
# 3. GỌI API VÀ IN KẾT QUẢ
# ----------------------------------------------------

print("\nĐang gửi nội dung cuộc họp đến Gemini để tạo biên bản...")

# Khối TRY/EXCEPT chính cho cuộc gọi API
try:
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=system_prompt,
        config={
            "temperature": 0.1
        }
    )

    # In kết quả biên bản (Nếu thành công)
    print("\n=============================================")
    print("✅ BIÊN BẢN CUỘC HỌP HOÀN CHỈNH:")
    print("=============================================")
    print(response.text)
    print("=============================================")

except Exception as e:
    # Xử lý lỗi API (Nếu thất bại)
    print("\nLỖI KẾT NỐI API HOẶC XÁC THỰC:")
    print(f"Lỗi chi tiết: {e}")
    print("Vui lòng kiểm tra lại API Key và kết nối mạng của bạn.")
    
# -----------------------------------------------------------------------
# LỆNH TẠM DỪNG CUỐI CÙNG (Đảm bảo chạy, dù có lỗi hay thành công)
# -----------------------------------------------------------------------
input("\nNhấn ENTER để đóng cửa sổ...")
