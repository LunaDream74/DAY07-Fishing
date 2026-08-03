---
title: "Benchmark: Minh RecursiveChunker"
date: "2026-08-03"
author: "Tran Nguyen Anh Minh"
strategy: "RecursiveChunker"
chunk_size: 450
separators: ["\n\n", "\n", ". ", " ", ""]
embedding_backend: "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
total_score: 8.0
hit_rate_at_1: 0.6
hit_rate_at_3: 1.0
filter_accuracy: 1.0
---

# Báo Cáo Đánh Giá Benchmark Retrieval - RecursiveChunker (size=450)

## 1. Tóm Tắt Chỉ Số (Aggregate Metrics)
- **Tổng điểm (Total Score)**: **8.0 / 10.0**
- **Hit Rate @ 1 (Top-1 Accuracy)**: 60.0%
- **Hit Rate @ 3 (Top-3 Accuracy)**: 100.0%
- **Độ chính xác Lọc Metadata (Filter Accuracy)**: 100.0%

## 2. Kết Quả Chi Tiết Cho 5 Câu Hỏi
| # | Câu Hỏi (Query) | Target Doc ID | Rank | Similarity | Điểm (Score) | Trạng Thái |
|---|---|---|---|---|---|---|
| 1 | Thời hạn và các đợt đăng ký học phần kỳ 1 năm học 2026-2027 diễn ra khi nào? | `hust-course-registration-20261` | #1 | 0.7217 | 2.0/2.0 | PASSED (Top-1, Score: 0.7217) |
| 2 | Điều kiện và đối tượng được xét trao Học bổng Trần Đại Nghĩa là gì? | `hust-tran-dai-nghia-scholarship` | #3 | 0.7550 | 1.0/2.0 | ACCEPTABLE (Rank #3, Score: 0.7550) |
| 3 | Thông báo đăng ký bổ sung học phần môn Toán kỳ 2025.2 yêu cầu sinh viên thực hiện như thế nào? | `hust-math-course-supplementary-registration` | #2 | 0.7139 | 1.0/2.0 | ACCEPTABLE (Rank #2, Score: 0.7139) |
| 4 | Quy trình xin ký xác nhận các thủ tục hành chính cho sinh viên tại trường như thế nào? | `hust-student-administrative-procedures` | #1 | 0.7113 | 2.0/2.0 | PASSED (Top-1, Score: 0.7113) |
| 5 | Các mức học phí và quy định đóng học phí áp dụng cho sinh viên là gì? | `hust-tuition-information` | #1 | 0.7336 | 2.0/2.0 | PASSED (Top-1, Score: 0.7336) |

## 3. Chi Tiết Chunks Đã Truy Xuất (Top-1 Context Snippets)
### Câu hỏi #1: *"Thời hạn và các đợt đăng ký học phần kỳ 1 năm học 2026-2027 diễn ra khi nào?"*
- **Target Document**: `hust-course-registration-20261` | **Filter**: `Pass`
- **Top-1 Doc ID**: `hust-course-registration-20261`
- **Nội dung trích đoạn**: *"- Đăng ký chính thức: từ 16:00 ngày 22/07/2026 đến 14:00 ngày 03/08/2026. - Đăng ký điều chỉnh: từ 16:00 ngày 03/08/2026 đến 14:00 ngày 15/08/2026. - Đăng ký thêm: từ 16:00 ngày 15/08/2026 đến 16:00 n..."*

### Câu hỏi #2: *"Điều kiện và đối tượng được xét trao Học bổng Trần Đại Nghĩa là gì?"*
- **Target Document**: `hust-tran-dai-nghia-scholarship` | **Filter**: `Pass`
- **Top-1 Doc ID**: `hust-scholarships`
- **Nội dung trích đoạn**: *"1. Học bổng Khuyến khích học tập dành cho sinh viên có kết quả học tập và rèn luyện tốt. 2. Học bổng Trần Đại Nghĩa dành cho sinh viên có hoàn cảnh khó khăn và có nghị lực vươn lên. 3. Học bổng tài tr..."*

### Câu hỏi #3: *"Thông báo đăng ký bổ sung học phần môn Toán kỳ 2025.2 yêu cầu sinh viên thực hiện như thế nào?"*
- **Target Document**: `hust-math-course-supplementary-registration` | **Filter**: `Pass`
- **Top-1 Doc ID**: `hust-course-registration-20261`
- **Nội dung trích đoạn**: *"# Kế hoạch đăng ký lớp kỳ 2026.1  Thông báo áp dụng cho sinh viên các khóa K70 trở về trước. Sinh viên đăng ký trực tuyến tại `https://qldt.hust.edu.vn/students` bằng tài khoản email Office 365 do Đại..."*

### Câu hỏi #4: *"Quy trình xin ký xác nhận các thủ tục hành chính cho sinh viên tại trường như thế nào?"*
- **Target Document**: `hust-student-administrative-procedures` | **Filter**: `Pass`
- **Top-1 Doc ID**: `hust-student-administrative-procedures`
- **Nội dung trích đoạn**: *"# Thủ tục hành chính sinh viên  Các giấy tờ được nêu gồm sổ ưu đãi, giấy chứng nhận sinh viên, giấy chứng nhận sinh viên tạm thời, vé tháng xe buýt, giấy giới thiệu, giấy vay vốn ngân hàng và biên lai..."*

### Câu hỏi #5: *"Các mức học phí và quy định đóng học phí áp dụng cho sinh viên là gì?"*
- **Target Document**: `hust-tuition-information` | **Filter**: `Pass`
- **Top-1 Doc ID**: `hust-tuition-information`
- **Nội dung trích đoạn**: *"# Thông tin học phí HUST  Trang học phí của HUST liên kết đến thông tin học phí năm học 2025–2026, thông tin năm học 2024–2025 và mức học phí theo từng chương trình đào tạo. Sinh viên cần xem đúng tài..."*


## Configuration notes

- Metadata overrides are applied in memory from `metadata_overrides.json`; shared HUST source files remain unchanged.
- The benchmark's required `audience=student` filter is used for query 5.
- Results produced with `MockEmbedder` are structural-only and must not be compared as semantic-retrieval quality. Use the local multilingual backend for the final group comparison.
