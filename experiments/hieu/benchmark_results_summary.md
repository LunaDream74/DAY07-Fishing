# 📊 Báo Cáo Tổng Hợp Kết Quả Thử Nghiệm: FixedSizeChunker & Bộ Benchmark Nhóm

---

## 📌 1. Thông Tin Thử Nghiệm (Experiment Metadata)

- **Người thực hiện**: Nguyễn Hữu Hiếu
- **Thư mục thí nghiệm**: `experiments/hieu/`
- **Chiến lược chia nhỏ (Chunking Strategy)**: `FixedSizeChunker`
  - `chunk_size`: **400 ký tự**
  - `overlap`: **50 ký tự**
- **Tập dữ liệu dùng chung (Shared Corpus)**: `data/hust_services/` (10 tài liệu dịch vụ HUST)
- **Tổng số Chunks sinh ra**: **22 chunks**
- **Embedder Model**: `sentence-transformers/all-MiniLM-L6-v2` (Local Transformer Embedder)

---

## 🎯 2. Bộ 5 Câu Hỏi Đánh Giá Benchmark (Group Benchmark Queries)

Bộ câu hỏi được thiết kế chuẩn theo quy định K3 Variant:

| # | Query (Câu Hỏi) | Target Document ID | Metadata Filter | Mục Tiêu Đánh Giá |
|---|---|---|---|---|
| 1 | *"Thời hạn và các đợt đăng ký học phần kỳ 1 năm học 2026-2027 diễn ra khi nào?"* | `hust-course-registration-20261` | `None` | Kiểm tra khả năng định vị thông tin lịch đăng ký môn học |
| 2 | *"Điều kiện và đối tượng được xét trao Học bổng Trần Đại Nghĩa là gì?"* | `hust-tran-dai-nghia-scholarship` | `None` | Kiểm tra khả năng truy xuất chính sách học bổng đặc thù |
| 3 | *"Thông báo đăng ký bổ sung học phần môn Toán kỳ 2025.2 yêu cầu sinh viên thực hiện như thế nào?"* | `hust-math-course-supplementary-registration` | `None` | Kiểm tra định vị thông tin môn học cụ thể |
| 4 | *"Quy trình xin ký xác nhận các thủ tục hành chính cho sinh viên tại trường như thế nào?"* | `hust-student-administrative-procedures` | `None` | Kiểm tra tổng hợp quy trình dịch vụ hành chính |
| 5 | *"Các mức học phí và quy định đóng học phí áp dụng cho sinh viên là gì?"* | `hust-tuition-information` | `{"audience": "student"}` | **Bắt buộc K3**: Kiểm tra khả năng lọc theo siêu dữ liệu |

---

## 📈 3. Kết Quả Thực Thi Chi Tiết (Detailed Benchmark Results)

### Tóm Tắt Chỉ Số (Aggregate Metrics)
- **Tổng điểm (Total Score)**: **5.0 / 10.0 Điểm**
- **Hit Rate @ 1 (Top-1 Accuracy)**: **40.0%** (2/5 câu hỏi đạt Top-1 chính xác)
- **Hit Rate @ 3 (Top-3 Accuracy)**: **60.0%** (3/5 câu hỏi thuộc Top-3)
- **Độ chính xác Lọc Metadata (Filter Accuracy)**: **100.0%**

### Bảng Chi Tiết Từng Câu Hỏi
| # | Câu Hỏi (Query) | Target Doc ID | Rank | Similarity Score | Điểm (Score) | Trạng Thái |
|---|---|---|---|---|---|---|
| 1 | Thời hạn và các đợt đăng ký học phần kỳ 1 năm học 2026-2027 diễn ra khi nào? | `hust-course-registration-20261` | N/A | 0.7212 | 0.0/2.0 | 🔴 FAILED (Không vào Top-3) |
| 2 | Điều kiện và đối tượng được xét trao Học bổng Trần Đại Nghĩa là gì? | `hust-tran-dai-nghia-scholarship` | #2 | 0.7003 | 1.0/2.0 | 🟡 ACCEPTABLE (Rank #2) |
| 3 | Thông báo đăng ký bổ sung học phần môn Toán kỳ 2025.2 yêu cầu sinh viên thực hiện như thế nào? | `hust-math-course-supplementary-registration` | #1 | 0.8241 | 2.0/2.0 | 🟢 PASSED (Top-1 Match) |
| 4 | Quy trình xin ký xác nhận các thủ tục hành chính cho sinh viên tại trường như thế nào? | `hust-student-administrative-procedures` | #1 | 0.7269 | 2.0/2.0 | 🟢 PASSED (Top-1 Match) |
| 5 | Các mức học phí và quy định đóng học phí áp dụng cho sinh viên là gì? | `hust-tuition-information` | N/A | 0.6945 | 0.0/2.0 | 🔴 FAILED (Không vào Top-3) |

---

## 🔍 4. Trích Đoạn Chunks Truy Xuất Top-1 (Top-1 Retrieved Contexts)

1. **Câu hỏi #1**: Target `hust-course-registration-20261`
   - *Top-1 Doc ID*: `hust-tuition-information` (Similarity: 0.7212)
   - *Snippet*: `"# Thông tin học phí HUST Trang học phí của HUST liên kết đến thông tin học phí năm học 2025–2026..."`
2. **Câu hỏi #2**: Target `hust-tran-dai-nghia-scholarship` (Rank #2)
   - *Top-1 Doc ID*: `hust-international-student-exchange` (Similarity: 0.7003)
   - *Snippet*: `"ài tháng, nhằm học tập và giao lưu văn hóa. Trao đổi hè thường dưới một tháng..."`
3. **Câu hỏi #3**: Target `hust-math-course-supplementary-registration` (Rank #1)
   - *Top-1 Doc ID*: `hust-math-course-supplementary-registration` (Similarity: 0.8241)
   - *Snippet*: `"# Đăng ký bổ sung học phần môn Toán kỳ 2025.2 Để đăng ký học vào lớp đã đầy, sinh viên thực hiện trên hệ thống QLDT tại qldt.hust.edu.vn và điền biểu mẫu 'Đơn xin đăng ký vào lớp đầy'..."`
4. **Câu hỏi #4**: Target `hust-student-administrative-procedures` (Rank #1)
   - *Top-1 Doc ID*: `hust-student-administrative-procedures` (Similarity: 0.7269)
   - *Snippet*: `"đãi và biên lai học phí được nhận cả ngày thứ Sáu. Giấy chứng nhận sinh viên tạm thời được trả vào buổi chiều từ 15:30. ## Một số quy trình - Giấy vay vốn: sinh viên tự in biểu mẫu, nộp cho lớp trưởng..."`
5. **Câu hỏi #5**: Target `hust-tuition-information` (Filter `audience: student`)
   - *Top-1 Doc ID*: `hust-tran-dai-nghia-scholarship` (Similarity: 0.6945)
   - *Snippet*: `"bật; sinh viên các khóa khác đang học đúng tiến độ, tích lũy đủ tín chỉ, có CPA từ 2,0 và điểm rèn luyện tích lũy từ 65..."`

---

## 💡 5. Phân Tích Lỗi & Đánh Giá Chiến Lược (Failure Analysis & Discussion)

### Ưu Điểm
- **Đơn giản & Tốc độ cao**: Thuật toán chỉ dựa vào phép cắt chuỗi ký tự cố định, độ phức tạp tính toán $O(N)$.
- **Khống chế kích thước tối đa**: Đảm bảo 100% các chunks không vượt quá `chunk_size = 400` ký tự.

### Nhược Điểm & Nguyên Nhân Lỗi (Failure Causes)
1. **Cắt dở từ và câu (Word & Sentence Mutilation)**:
   - Thuật toán cắt theo số ký tự tuyệt đối mà không nhận biết ranh giới từ (khoảng trắng) hay ranh giới câu (dấu chấm). Nhiều từ bị ngắt đôi (ví dụ: `"đãi và biên lai"`, `"ài tháng"`).
2. **Mất liên kết ngữ nghĩa (Semantic Disruption)**:
   - Ở câu hỏi #1 và #5, việc cắt cố định 400 ký tự khiến thông tin quan trọng bị đẩy sang chunk tiếp theo, dẫn tới điểm tương tự Cosine với tài liệu mục tiêu bị thấp hơn so với các chunk nhiễu khác.
3. **So sánh với các chiến lược khác trong nhóm**:
   - `SentenceChunker`: Giữ trọn ranh giới câu, giảm thiểu việc mất ngữ cảnh giữa câu.
   - `RecursiveChunker`: Ưu việt nhất vì phân chia đệ quy theo tiêu đề và đoạn văn bản (`\n\n`, `\n`), giữ trọn vẹn ngữ nghĩa của từng mục quy định.

---

## 🛠️ 6. Các Tệp Liên Quan (Related Files)

- [config.py](file:///d:/tai%20lieu%20hoc%20tap/VinAI/Day07/Lap/DAY07-Fishing/experiments/hieu/config.py): Cấu hình `FixedSizeChunker`.
- [metadata_overrides.json](file:///d:/tai%20lieu%20hoc%20tap/VinAI/Day07/Lap/DAY07-Fishing/experiments/hieu/metadata_overrides.json): Metadata mở rộng cá nhân.
- [run_experiment.py](file:///d:/tai%20lieu%20hoc%20tap/VinAI/Day07/Lap/DAY07-Fishing/experiments/hieu/run_experiment.py): Script thực thi benchmark.
- [LOG_v1.0_20260803_fixed_size_benchmark.md](file:///d:/tai%20lieu%20hoc%20tap/VinAI/Day07/Lap/DAY07-Fishing/my_workspace/logs/LOG_v1.0_20260803_fixed_size_benchmark.md): Log ghi nhận trong `my_workspace/`.
