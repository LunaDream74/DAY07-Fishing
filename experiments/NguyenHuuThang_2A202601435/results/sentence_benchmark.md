# Kết quả thí nghiệm SentenceChunker — Nguyễn Hữu Thắng

## Cấu hình cố định

- Corpus: `data/hust_services` (10 tài liệu)
- Strategy: `SentenceChunker(max_sentences_per_chunk=2)`
- Embedder: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- Số chunk đã nạp: **32**
- Queries: `scripts.benchmark.BENCHMARK_QUERIES` (5 query chung)
- Metadata overrides: không có; giữ nguyên metadata của corpus

## Baseline (đã bỏ YAML front matter)

`ChunkingStrategyComparator.compare(body, chunk_size=200)`

| Tài liệu | Strategy | Số chunk | Độ dài trung bình |
|---|---|---:|---:|
| `hust-course-registration-20261` | `fixed_size` | 7 | 183.4 |
| `hust-course-registration-20261` | `by_sentences` | 3 | 326.3 |
| `hust-course-registration-20261` | `recursive` | 9 | 107.8 |
| `hust-student-administrative-procedures` | `fixed_size` | 6 | 185.2 |
| `hust-student-administrative-procedures` | `by_sentences` | 3 | 285.7 |
| `hust-student-administrative-procedures` | `recursive` | 8 | 106.1 |
| `hust-tran-dai-nghia-scholarship` | `fixed_size` | 4 | 197.2 |
| `hust-tran-dai-nghia-scholarship` | `by_sentences` | 1 | 637.0 |
| `hust-tran-dai-nghia-scholarship` | `recursive` | 4 | 158.5 |

## Kết quả retrieval

- Điểm: **6.0/10.0**
- Hit@1: **60.0%**
- Hit@3: **60.0%**
- Filter accuracy: **100.0%**

### Query 1

- Câu hỏi: Thời hạn và các đợt đăng ký học phần kỳ 1 năm học 2026-2027 diễn ra khi nào?
- Target: `hust-course-registration-20261`
- Filter: `None`
- Target rank: `1`; điểm: `2.0/2.0`

| Rank | Score | doc_id | Preview |
|---:|---:|---|---|
| 1 | 0.7204 | `hust-course-registration-20261` | ## Các đợt đăng ký - Đăng ký chính thức: từ 16:00 ngày 22/07/2026 đến 14:00 ngày 03/08/2026. - Đăng ký điều chỉnh: từ 16:00 ngày 03/08/2026 đến 14:00 ngày 15/08/2026. |
| 2 | 0.7166 | `hust-course-registration-20261` | - Đăng ký thêm: từ 16:00 ngày 15/08/2026 đến 16:00 ngày 22/08/2026. Hệ thống bảo trì định kỳ từ 00:00 đến 02:00 mỗi ngày; sinh viên không truy cập trang đăng ký trong thời gian ... |
| 3 | 0.6118 | `hust-student-administrative-procedures` | - Biên lai học phí: sinh viên đăng ký vào sáng thứ Hai, Ba hoặc Tư và nhận biên lai vào thứ Sáu. |

Câu trả lời của agent trích xuất (offline, dùng top-3 làm grounding):

> [1] ## Các đợt đăng ký - Đăng ký chính thức: từ 16:00 ngày 22/07/2026 đến 14:00 ngày 03/08/2026. - Đăng ký điều chỉnh: từ 16:00 ngày 03/08/2026 đến 14:00 ngày 15/08/2026. [2] - Đăng ký thêm: từ 16:00 ngày 15/08/2026 đến 16:00 ngày 22/08/2026. Hệ thống bảo trì định kỳ từ 00:00 đến 02:00 mỗi ngày; sinh viên không truy cập trang đăng ký trong thời gian này. [3] - Biên lai học phí: sinh viên đăng ký vào sáng thứ Hai, Ba hoặc Tư và nhận biên lai vào thứ Sáu.

### Query 2

- Câu hỏi: Điều kiện và đối tượng được xét trao Học bổng Trần Đại Nghĩa là gì?
- Target: `hust-tran-dai-nghia-scholarship`
- Filter: `None`
- Target rank: `N/A`; điểm: `0.0/2.0`

| Rank | Score | doc_id | Preview |
|---:|---:|---|---|
| 1 | 0.7676 | `hust-scholarships` | 3. Học bổng tài trợ dành cho sinh viên có kết quả học tập tốt hoặc có hoàn cảnh khó khăn. |
| 2 | 0.7558 | `hust-scholarships` | 2. Học bổng Trần Đại Nghĩa dành cho sinh viên có hoàn cảnh khó khăn và có nghị lực vươn lên. |
| 3 | 0.7378 | `hust-scholarships` | 5. Học bổng gắn kết quê hương dành cho sinh viên có đồ án hoặc khóa luận tốt nghiệp mang tính ứng dụng, thực tế với đời sống xã hội. |

Câu trả lời của agent trích xuất (offline, dùng top-3 làm grounding):

> [1] 3. Học bổng tài trợ dành cho sinh viên có kết quả học tập tốt hoặc có hoàn cảnh khó khăn. [2] 2. Học bổng Trần Đại Nghĩa dành cho sinh viên có hoàn cảnh khó khăn và có nghị lực vươn lên. [3] 5. Học bổng gắn kết quê hương dành cho sinh viên có đồ án hoặc khóa luận tốt nghiệp mang tính ứng dụng, thực tế với đời sống xã hội.

### Query 3

- Câu hỏi: Thông báo đăng ký bổ sung học phần môn Toán kỳ 2025.2 yêu cầu sinh viên thực hiện như thế nào?
- Target: `hust-math-course-supplementary-registration`
- Filter: `None`
- Target rank: `N/A`; điểm: `0.0/2.0`

| Rank | Score | doc_id | Preview |
|---:|---:|---|---|
| 1 | 0.7157 | `hust-student-administrative-procedures` | # Thủ tục hành chính sinh viên Các giấy tờ được nêu gồm sổ ưu đãi, giấy chứng nhận sinh viên, giấy chứng nhận sinh viên tạm thời, vé tháng xe buýt, giấy giới thiệu, giấy vay vốn... |
| 2 | 0.7141 | `hust-course-registration-20261` | # Kế hoạch đăng ký lớp kỳ 2026.1 Thông báo áp dụng cho sinh viên các khóa K70 trở về trước. Sinh viên đăng ký trực tuyến tại `https://qldt.hust.edu.vn/students` bằng tài khoản e... |
| 3 | 0.7011 | `hust-student-administrative-procedures` | - Biên lai học phí: sinh viên đăng ký vào sáng thứ Hai, Ba hoặc Tư và nhận biên lai vào thứ Sáu. |

Câu trả lời của agent trích xuất (offline, dùng top-3 làm grounding):

> [1] # Thủ tục hành chính sinh viên Các giấy tờ được nêu gồm sổ ưu đãi, giấy chứng nhận sinh viên, giấy chứng nhận sinh viên tạm thời, vé tháng xe buýt, giấy giới thiệu, giấy vay vốn ngân hàng và biên lai học phí. ## Lịch nhận và trả Sinh viên năm thứ nhất nộp các giấy tờ vào sáng thứ Hai, Ba, Tư và các buổi chiều từ 15:30. [2] # Kế hoạch đăng ký lớp kỳ 2026.1 Thông báo áp dụng cho sinh viên các khóa K70 trở về trước. Sinh viên đăng ký trực tuyến tại `https://qldt.hust.edu.vn/students` bằng tài khoản email Office 365 do Đại học cấp. [3] - Biên lai học phí: sinh viên đăng ký vào sáng thứ Hai, Ba hoặc Tư và nhận biên lai vào thứ Sáu.

### Query 4

- Câu hỏi: Quy trình xin ký xác nhận các thủ tục hành chính cho sinh viên tại trường như thế nào?
- Target: `hust-student-administrative-procedures`
- Filter: `None`
- Target rank: `1`; điểm: `2.0/2.0`

| Rank | Score | doc_id | Preview |
|---:|---:|---|---|
| 1 | 0.6870 | `hust-student-administrative-procedures` | # Thủ tục hành chính sinh viên Các giấy tờ được nêu gồm sổ ưu đãi, giấy chứng nhận sinh viên, giấy chứng nhận sinh viên tạm thời, vé tháng xe buýt, giấy giới thiệu, giấy vay vốn... |
| 2 | 0.6336 | `hust-international-student-exchange` | - Có điều kiện tài chính cần thiết, được Trường/Khoa chấp thuận và đáp ứng yêu cầu của đối tác/nước sở tại. Hồ sơ thường gồm đơn đăng ký, CV, bảng điểm, chứng chỉ tiếng Anh, thư... |
| 3 | 0.6095 | `hust-student-administrative-procedures` | ## Một số quy trình - Giấy vay vốn: sinh viên tự in biểu mẫu, nộp cho lớp trưởng; lớp trưởng tổng hợp và nộp theo danh sách lớp. - Giấy chứng nhận sinh viên tạm thời: chỉ dành c... |

Câu trả lời của agent trích xuất (offline, dùng top-3 làm grounding):

> [1] # Thủ tục hành chính sinh viên Các giấy tờ được nêu gồm sổ ưu đãi, giấy chứng nhận sinh viên, giấy chứng nhận sinh viên tạm thời, vé tháng xe buýt, giấy giới thiệu, giấy vay vốn ngân hàng và biên lai học phí. ## Lịch nhận và trả Sinh viên năm thứ nhất nộp các giấy tờ vào sáng thứ Hai, Ba, Tư và các buổi chiều từ 15:30. [2] - Có điều kiện tài chính cần thiết, được Trường/Khoa chấp thuận và đáp ứng yêu cầu của đối tác/nước sở tại. Hồ sơ thường gồm đơn đăng ký, CV, bảng điểm, chứng chỉ tiếng Anh, thư nguyện vọng và thư giới thiệu. [3] ## Một số quy trình - Giấy vay vốn: sinh viên tự in biểu mẫu, nộp cho lớp trưởng; lớp trưởng tổng hợp và nộp theo danh sách lớp. - Giấy chứng nhận sinh viên t

### Query 5

- Câu hỏi: Các mức học phí và quy định đóng học phí áp dụng cho sinh viên là gì?
- Target: `hust-tuition-information`
- Filter: `{'audience': 'student'}`
- Target rank: `1`; điểm: `2.0/2.0`

| Rank | Score | doc_id | Preview |
|---:|---:|---|---|
| 1 | 0.7336 | `hust-tuition-information` | # Thông tin học phí HUST Trang học phí của HUST liên kết đến thông tin học phí năm học 2025–2026, thông tin năm học 2024–2025 và mức học phí theo từng chương trình đào tạo. Sinh... |
| 2 | 0.5829 | `hust-student-administrative-procedures` | # Thủ tục hành chính sinh viên Các giấy tờ được nêu gồm sổ ưu đãi, giấy chứng nhận sinh viên, giấy chứng nhận sinh viên tạm thời, vé tháng xe buýt, giấy giới thiệu, giấy vay vốn... |
| 3 | 0.5370 | `hust-tran-dai-nghia-scholarship` | Học bổng xét theo học kỳ, với hai mức tương ứng 50% và 100% học phí của học kỳ. |

Câu trả lời của agent trích xuất (offline, dùng top-3 làm grounding):

> [1] # Thông tin học phí HUST Trang học phí của HUST liên kết đến thông tin học phí năm học 2025–2026, thông tin năm học 2024–2025 và mức học phí theo từng chương trình đào tạo. Sinh viên cần xem đúng tài liệu của năm học và chương trình đang theo học để tra mức học phí áp dụng. [2] # Thủ tục hành chính sinh viên Các giấy tờ được nêu gồm sổ ưu đãi, giấy chứng nhận sinh viên, giấy chứng nhận sinh viên tạm thời, vé tháng xe buýt, giấy giới thiệu, giấy vay vốn ngân hàng và biên lai học phí. ## Lịch nhận và trả Sinh viên năm thứ nhất nộp các giấy tờ vào sáng thứ Hai, Ba, Tư và các buổi chiều từ 15:30. [3] Học bổng xét theo học kỳ, với hai mức tương ứng 50% và 100% học phí của học kỳ.

