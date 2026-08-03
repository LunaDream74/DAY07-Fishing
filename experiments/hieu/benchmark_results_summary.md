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
- **Embedder**: `MockEmbedder` (Deterministic fast embedder)

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
- **Tổng điểm (Total Score)**: **1.0 / 10.0 Điểm**
- **Hit Rate @ 1 (Top-1 Accuracy)**: **0.0%**
- **Hit Rate @ 3 (Top-3 Accuracy)**: **20.0%**
- **Độ chính xác Lọc Metadata (Filter Accuracy)**: **100.0%**

### Bảng Chi Tiết Từng Câu Hỏi
| # | Câu Hỏi (Query) | Target Doc ID | Rank | Similarity Score | Điểm (Score) | Trạng Thái |
|---|---|---|---|---|---|---|
| 1 | Thời hạn và các đợt đăng ký học phần kỳ 1 năm học 2026-2027 diễn ra khi nào? | `hust-course-registration-20261` | N/A | 0.2128 | 0.0/2.0 | 🔴 FAILED (Không vào Top-3) |
| 2 | Điều kiện và đối tượng được xét trao Học bổng Trần Đại Nghĩa là gì? | `hust-tran-dai-nghia-scholarship` | N/A | 0.4152 | 0.0/2.0 | 🔴 FAILED (Không vào Top-3) |
| 3 | Thông báo đăng ký bổ sung học phần môn Toán kỳ 2025.2 yêu cầu sinh viên thực hiện như thế nào? | `hust-math-course-supplementary-registration` | N/A | 0.2073 | 0.0/2.0 | 🔴 FAILED (Không vào Top-3) |
| 4 | Quy trình xin ký xác nhận các thủ tục hành chính cho sinh viên tại trường như thế nào? | `hust-student-administrative-procedures` | #3 | 0.1458 | 1.0/2.0 | 🟡 ACCEPTABLE (Rank #3) |
| 5 | Các mức học phí và quy định đóng học phí áp dụng cho sinh viên là gì? | `hust-tuition-information` | N/A | 0.1516 | 0.0/2.0 | 🔴 FAILED (Không vào Top-3) |

---

## 🔍 4. Trích Đoạn Chunks Truy Xuất Top-1 (Top-1 Retrieved Contexts)

1. **Câu hỏi #1**: Target `hust-course-registration-20261`
   - *Top-1 Doc ID*: `hust-tran-dai-nghia-scholarship`
   - *Snippet*: `"bật; sinh viên các khóa khác đang học đúng tiến độ, tích lũy đủ tín chỉ, có CPA từ 2,0 và điểm rèn luyện tích lũy từ 65; hoặc sinh viên gặp rủi ro, tai nạn, bệnh hiểm nghèo..."`
2. **Câu hỏi #2**: Target `hust-tran-dai-nghia-scholarship`
   - *Top-1 Doc ID*: `hust-international-student-exchange`
   - *Snippet*: `" ứng yêu cầu của đối tác/nước sở tại. Hồ sơ thường gồm đơn đăng ký, CV, bảng điểm, chứng chỉ tiếng Anh, thư nguyện vọng và thư giới thiệu..."`
3. **Câu hỏi #3**: Target `hust-math-course-supplementary-registration`
   - *Top-1 Doc ID*: `hust-course-registration-20261`
   - *Snippet*: `"00 ngày 22/08/2026. Hệ thống bảo trì định kỳ từ 00:00 đến 02:00 mỗi ngày; sinh viên không truy cập trang đăng ký trong thời gian này..."`
4. **Câu hỏi #4**: Target `hust-student-administrative-procedures`
   - *Top-1 Doc ID*: `hust-international-student-exchange`
   - *Snippet*: `" ứng yêu cầu của đối tác/nước sở tại. Hồ sơ thường gồm đơn đăng ký, CV, bảng điểm, chứng chỉ tiếng Anh, thư nguyện vọng và thư giới thiệu..."`
5. **Câu hỏi #5**: Target `hust-tuition-information` (Filter `audience: student`)
   - *Top-1 Doc ID*: `hust-tran-dai-nghia-scholarship`
   - *Snippet*: `"# Học bổng Trần Đại Nghĩa HUST thành lập Học bổng Trần Đại Nghĩa từ năm học 2021–2022 để hỗ trợ sinh viên có hoàn cảnh khó khăn..."`

---

## 💡 5. Phân Tích Lỗi & Đánh Giá Chiến Lược (Failure Analysis & Discussion)

### Ưu Điểm
- **Đơn giản & Tốc độ cao**: Thuật toán chỉ dựa vào phép cắt chuỗi ký tự cố định, độ phức tạp tính toán $O(N)$.
- **Khống chế kích thước tối đa**: Đảm bảo 100% các chunks không vượt quá `chunk_size = 400` ký tự.

### Nhược Điểm & Nguyên Nhân Lỗi (Failure Causes)
1. **Cắt dở từ và câu (Word & Sentence Mutilation)**:
   - Thuật toán cắt theo số ký tự tuyệt đối mà không nhận biết ranh giới từ (khoảng trắng) hay ranh giới câu (dấu chấm). Nhiều từ tiếng Việt bị ngắt đôi (ví dụ: `"ứng yêu cầu"`, `"00 ngày"`).
2. **Mất liên kết ngữ nghĩa (Semantic Disruption)**:
   - Một ý hoàn chỉnh hoặc câu hỏi-đáp bị xé thành 2 chunks riêng biệt. Ngay cả khi có `overlap = 50`, độ chồng chéo này vẫn không đủ bù đắp đoạn bị cắt đứt giữa chừng.
3. **So sánh với các chiến lược khác trong nhóm**:
   - `SentenceChunker`: Tốt hơn `FixedSizeChunker` vì giữ trọn vẹn ranh giới câu.
   - `RecursiveChunker`: Ưu việt nhất vì tách theo thứ tự ưu tiên `["\n\n", "\n", ". ", " "]`, giữ trọn cấu trúc đoạn văn bản.

---

## 🛠️ 6. Các Tệp Liên Quan (Related Files)

- [config.py](file:///d:/tai%20lieu%20hoc%20tap/VinAI/Day07/Lap/DAY07-Fishing/experiments/hieu/config.py): Cấu hình `FixedSizeChunker`.
- [metadata_overrides.json](file:///d:/tai%20lieu%20hoc%20tap/VinAI/Day07/Lap/DAY07-Fishing/experiments/hieu/metadata_overrides.json): Metadata mở rộng cá nhân.
- [run_experiment.py](file:///d:/tai%20lieu%20hoc%20tap/VinAI/Day07/Lap/DAY07-Fishing/experiments/hieu/run_experiment.py): Script thực thi benchmark.
- [LOG_v1.0_20260803_fixed_size_benchmark.md](file:///d:/tai%20lieu%20hoc%20tap/VinAI/Day07/Lap/DAY07-Fishing/my_workspace/logs/LOG_v1.0_20260803_fixed_size_benchmark.md): Log ghi nhận trong `my_workspace/`.
