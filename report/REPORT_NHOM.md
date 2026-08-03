# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** Nhóm K3 - Retrieval Quy Định & Dịch Vụ Đại Học  
**Thành viên:**
1. Nguyễn Hữu Hiếu (2A202601429) — FixedSizeChunker
2. Nguyễn Hữu Thắng (2A202601435) — SentenceChunker
3. Trần Nguyễn Anh Minh (2A202601475) — RecursiveChunker  
**Ngày:** 03/08/2026  

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Phạm vi bộ tài liệu (Scope)

**Chủ đề (cố định theo lớp K3):** Dịch vụ / quy định đại học (đăng ký môn, học phí, học bổng, thư viện, ký túc xá…).

**Phạm vi cụ thể nhóm tập trung:**
> Quy định đăng ký học phần, thủ tục hành chính sinh viên, chính sách học bổng (Trần Đại Nghĩa & khuyến khích), thông tin học phí và chương trình trao đổi sinh viên quốc tế tại Đại học Bách khoa Hà Nội (HUST).

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | `hust-course-registration-20261` | https://ctt.hust.edu.vn/DisplayWeb/DisplayKehoach?kehoach=29240 | 08/03/2026 (v2026.1) | 1,535 | `audience: student`, `category: academic`, `department: Dao Tao` |
| 2 | `hust-international-student-exchange` | https://www.hust.edu.vn/vi/trao-doi-sinh-vien/ | 08/03/2026 (not-stated) | 1,458 | `audience: student`, `category: exchange`, `department: Hop tac Quoc te` |
| 3 | `hust-math-course-supplementary-registration` | https://fami.hust.edu.vn/thong-bao-sinh-vien/... | 08/03/2026 (v2025.2) | 959 | `audience: student`, `category: academic`, `department: Vien Toan` |
| 4 | `hust-scholarships` | https://www.hust.edu.vn/vi/sinh-vien/hoc-bong-hoc-phi/... | 08/03/2026 (v2025-06) | 1,189 | `audience: student`, `category: scholarship`, `department: Cong tac Sinh vien` |
| 5 | `hust-student-administrative-procedures` | https://hust.edu.vn/vi/sinh-vien/.../quy-trinh-ky-xac-nhan... | 08/03/2026 (not-stated) | 1,487 | `audience: student`, `category: administrative`, `department: Cong tac Sinh vien` |
| 6 | `hust-student-affairs` | https://www.hust.edu.vn/vi/sinh-vien/cong-tac-sinh-vien/... | 08/03/2026 (not-stated) | 870 | `audience: student`, `category: administrative`, `department: Cong tac Sinh vien` |
| 7 | `hust-student-clubs` | https://www.hust.edu.vn/vi/sinh-vien/hoat-dong-cua-sinh-vien/... | 08/03/2026 (not-stated) | 882 | `audience: student`, `category: activities`, `department: Doan Thanh nien` |
| 8 | `hust-student-exchange-policy` | https://www.hust.edu.vn/vi/sinh-vien/ho-tro-sinh-vien/... | 08/03/2026 (not-stated) | 1,122 | `audience: student`, `category: exchange`, `department: Hop tac Quoc te` |
| 9 | `hust-tran-dai-nghia-scholarship` | https://www.hust.edu.vn/vi/sinh-vien/.../thanh-lap-hoc-bong... | 08/03/2026 (not-stated) | 1,178 | `audience: student`, `category: scholarship`, `department: Cong tac Sinh vien` |
| 10 | `hust-tuition-information` | https://www.hust.edu.vn/vi/sinh-vien/hoc-bong-hoc-phi/... | 08/03/2026 (v2025-2026) | 613 | `audience: student`, `category: finance`, `department: Tai chinh Ke toan` |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `audience` | `str` | `student`, `faculty`, `staff` | Lọc chính xác nhóm đối tượng áp dụng quy định (Bắt buộc K3). |
| `source_url` | `str` | `https://ctt.hust.edu.vn/...` | Đảm bảo tính minh bạch và khả năng truy vết nguồn câu trả lời RAG. |
| `retrieved_at` | `str` | `8/3/2026` | Kiểm soát độ mới (freshness) và ngày lấy dữ liệu. |
| `document_version` | `str` | `2026.1`, `2025-2026` | Phân biệt các đợt áp dụng quy định giữa các học kỳ/năm học. |
| `category` | `str` | `academic`, `scholarship`, `finance` | Phân loại chủ đề tài liệu để lọc trước khi tính similarity. |
| `department` | `str` | `Dao Tao`, `Vien Toan`, `CTSV` | Giới hạn đơn vị quản lý quy định để thu hẹp không gian tìm kiếm. |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 3 tài liệu đại diện:

Đã gọi `parse_front_matter()` và chỉ truyền phần thân tài liệu vào `ChunkingStrategyComparator.compare(body, chunk_size=200)`, số liệu không bao gồm khối YAML:

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------:|-------------------:|-------------------|
| Đăng ký lớp kỳ 2026.1 | FixedSizeChunker (`fixed_size`) | 7 | 183.4 | Trung bình: kích thước đều nhưng có thể cắt giữa câu hoặc danh sách. |
| Đăng ký lớp kỳ 2026.1 | SentenceChunker (`by_sentences`) | 3 | 326.3 | Tốt ở ranh giới câu; một chunk có thể chứa nhiều mục liên tiếp. |
| Đăng ký lớp kỳ 2026.1 | RecursiveChunker (`recursive`) | 9 | 107.8 | Giữ ranh giới Markdown nhưng tạo một số chunk tiêu đề rất ngắn. |
| Thủ tục hành chính sinh viên | FixedSizeChunker (`fixed_size`) | 6 | 185.2 | Trung bình: có nguy cơ tách giấy tờ khỏi bước xử lý tương ứng. |
| Thủ tục hành chính sinh viên | SentenceChunker (`by_sentences`) | 3 | 285.7 | Khá tốt: mỗi quy trình vẫn nguyên câu, nhưng chunk tương đối dài. |
| Thủ tục hành chính sinh viên | RecursiveChunker (`recursive`) | 8 | 106.1 | Giữ đoạn/mục tốt, đổi lại có nhiều mảnh ngắn. |
| Học bổng Trần Đại Nghĩa | FixedSizeChunker (`fixed_size`) | 4 | 197.2 | Trung bình: câu điều kiện dài bị cắt theo ký tự. |
| Học bổng Trần Đại Nghĩa | SentenceChunker (`by_sentences`) | 1 | 637.0 | Giữ trọn câu nhưng gom cả tài liệu, làm giảm độ chi tiết retrieval. |
| Học bổng Trần Đại Nghĩa | RecursiveChunker (`recursive`) | 4 | 158.5 | Cân bằng hơn về kích thước, nhưng có thể tách tiêu đề khỏi nội dung. |

### Chiến lược của từng thành viên

**Thành viên 1 — Nguyễn Hữu Hiếu**
- **Loại chiến lược:** `FixedSizeChunker(chunk_size=400, overlap=50)`
- **Mô tả & lý do chọn cho chủ đề này:** Cửa sổ trượt cố định 400 ký tự giúp khống chế độ dài tối đa của chunk không vượt quá giới hạn token của LLM, tốc độ xử lý nhanh $O(N)$. Tuy nhiên, nhược điểm lớn nhất là không nhận biết ranh giới từ/câu nên dễ làm xé lẻ câu hoặc cắt đôi từ tiếng Việt.
- **Code snippet (built-in):**
```python
chunker = FixedSizeChunker(chunk_size=400, overlap=50)
```

**Thành viên 2 — Nguyễn Hữu Thắng**
- **Loại chiến lược:** `SentenceChunker(max_sentences_per_chunk=2)`
- **Mô tả & lý do chọn:** Hai câu liên tiếp thường cùng mô tả một điều kiện, lịch hoặc quy trình, nên giữ chúng trong cùng chunk giúp bảo toàn ngữ cảnh. Giới hạn hai câu cũng tránh trường hợp cấu hình mặc định ba câu gom gần như toàn bộ một tài liệu ngắn vào một record. Điểm yếu là không có giới hạn cứng theo ký tự.
- **Code snippet (built-in):**
```python
chunker = SentenceChunker(max_sentences_per_chunk=2)
```

**Thành viên 3 — Trần Nguyễn Anh Minh**
- **Loại chiến lược:** `RecursiveChunker(chunk_size=450, separators=["\n\n", "\n", ". ", " ", ""])`
- **Mô tả & lý do chọn:** Tài liệu quy định dịch vụ đại học được cấu trúc rõ ràng theo các tiêu đề Markdown và đoạn văn (`\n\n`, `\n`). Việc phân chia đệ quy ưu tiên ranh giới đoạn/tiêu đề giúp bảo toàn ngữ cảnh cấp phần (section context) tốt nhất trước khi tách nhỏ theo câu hay từ.
- **Code snippet (built-in):**
```python
chunker = RecursiveChunker(
    chunk_size=450,
    separators=["\n\n", "\n", ". ", " ", ""]
)
```

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Hit Rate @ 3 | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|--------------|-----------|----------|
| **Trần Nguyễn Anh Minh** | RecursiveChunker (size=450) | **8.0 / 10** | **100.0%** | Giữ trọn cấu trúc đoạn/mục Markdown, Hit@3 đạt 100% (5/5 câu đều nằm trong Top-3). | Tạo ra một số chunk tiêu đề ngắn nếu tài liệu có nhiều heading liên tiếp. |
| **Nguyễn Hữu Thắng** | SentenceChunker (2 câu/chunk) | **6.0 / 10** | **60.0%** | 100% giữ nguyên ranh giới câu; lịch đăng ký, thủ tục và học phí đạt Top-1. | Tài liệu tổng quát lấn át query học bổng Trần Đại Nghĩa và đăng ký bổ sung Toán. |
| **Nguyễn Hữu Hiếu** | FixedSizeChunker (size=400) | **5.0 / 10** | **60.0%** | Đơn giản, tốc độ xử lý nhanh, khống chế độ dài chunk đều đặn. | Cắt dở từ và câu ngẫu nhiên làm mất liên kết ngữ nghĩa giữa các ý. |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> **`RecursiveChunker` (Trần Nguyễn Anh Minh)** là chiến lược tốt nhất cho bộ dữ liệu dịch vụ & quy định đại học. Nguyên nhân vì các văn bản quy phạm và thông báo hành chính được trình bày theo cấu trúc phân cấp (Tiêu đề `#`, `##`, Các đợt `\n\n`, Các bước `-`). `RecursiveChunker` tôn trọng ranh giới đoạn văn và tiêu đề Markdown trước khi chia nhỏ, giúp giữ trọn ý nghĩa của một quy trình hay điều kiện học bổng, qua đó đạt **Hit Rate @ 3 = 100%** và tổng điểm cao nhất (**8.0/10.0**).

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Bộ Công Cụ Benchmark Dùng Chung (`scripts/benchmark.py`)

Bộ module benchmark dùng chung cho toàn nhóm được lập trình tại [scripts/benchmark.py](file:///d:/tai%20lieu%20hoc%20tap/VinAI/Day07/Lap/DAY07-Fishing/scripts/benchmark.py), bao gồm:
- **5 Câu hỏi đánh giá chuẩn hóa (`BENCHMARK_QUERIES`)**: Bao phủ 10 tài liệu dịch vụ HUST và có 1 câu bắt buộc lọc siêu dữ liệu `metadata_filter={"audience": "student"}` theo yêu cầu K3 Variant.
- **Bộ tính toán điểm tự động (`evaluate_store`)**: Đánh giá theo thang 10.0 điểm chuẩn của `docs/SCORING.md` (2.0 điểm/câu cho Top-1 match, 1.0 điểm/câu cho Top-3 match).
- **Trình tạo báo cáo tự động (`generate_markdown_report`)**: Xuất thống kê Hit Rate @ 1, Hit Rate @ 3, Filter Accuracy và snippet trích đoạn ngữ cảnh.

---

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)


| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Thời hạn và các đợt đăng ký học phần kỳ 1 năm học 2026-2027 diễn ra khi nào? | Đăng ký chính thức: 16:00 ngày 22/07/2026 - 14:00 ngày 03/08/2026. Đăng ký điều chỉnh: 16:00 ngày 03/08/2026 - 14:00 ngày 15/08/2026. Đăng ký thêm: 15/08/2026 - 22/08/2026. | `hust-course-registration-20261` (Chunk đợt đăng ký) |
| 2 | Điều kiện và đối tượng được xét trao Học bổng Trần Đại Nghĩa là gì? | Sinh viên có hoàn cảnh khó khăn, hộ nghèo/cận nghèo, mồ côi, có nghị lực vươn lên; sinh viên các khóa khác có CPA >= 2.0 và điểm rèn luyện tích lũy >= 65. | `hust-tran-dai-nghia-scholarship` (Chunk điều kiện) |
| 3 | Thông báo đăng ký bổ sung học phần môn Toán kỳ 2025.2 yêu cầu sinh viên thực hiện như thế nào? | Sinh viên đăng ký trên hệ thống QLDT tại `qldt.hust.edu.vn` và điền biểu mẫu "Đơn xin đăng ký vào lớp đầy" gửi Viện Toán. | `hust-math-course-supplementary-registration` (Chunk hướng dẫn) |
| 4 | Quy trình xin ký xác nhận các thủ tục hành chính cho sinh viên tại trường như thế nào? | Sinh viên tự in biểu mẫu, nộp qua Ban CTSV hoặc phòng một cửa; Giấy chứng nhận sinh viên tạm thời trả buổi chiều từ 15:30. | `hust-student-administrative-procedures` (Chunk quy trình) |
| 5 | Các mức học phí và quy định đóng học phí áp dụng cho sinh viên là gì? | Mức học phí tính theo tín chỉ tùy thuộc từng chương trình đào tạo năm học 2025–2026; nộp qua tài khoản ngân hàng liên kết. (Lọc `audience: student`). | `hust-tuition-information` (Chunk thông tin học phí) |

### Tổng hợp chất lượng truy xuất của nhóm

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | Đăng ký học phần 2026.1 | `RecursiveChunker` & `SentenceChunker` | **Có (Top-1)** | Cả Recursive (#1: 0.7217) và Sentence (#1: 0.7204) đều đạt Top-1 chính xác. |
| 2 | Học bổng Trần Đại Nghĩa | `FixedSizeChunker` & `RecursiveChunker` | **Có (Top-2 / Top-3)** | FixedSize đạt Top-2 (0.7003), Recursive đạt Top-3 (0.7550). Sentence bị lấn át bởi doc học bổng tổng hợp. |
| 3 | Đăng ký bổ sung môn Toán | `FixedSizeChunker` & `RecursiveChunker` | **Có (Top-1 / Top-2)** | FixedSize đạt Top-1 (0.8241), Recursive đạt Top-2 (0.7139). |
| 4 | Thủ tục hành chính sinh viên | **Cả 3 chiến lược** | **Có (Top-1)** | Tất cả 3 chiến lược đều đạt Top-1 match xuất sắc (Sentence: 0.6870, Recursive: 0.7113, FixedSize: 0.7269). |
| 5 | Quy định học phí (Lọc `audience: student`) | `RecursiveChunker` & `SentenceChunker` | **Có (Top-1)** | Recursive (#1: 0.7336) và Sentence (#1: 0.7336) đều đạt Top-1 match chính xác. |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> **Lọc bằng metadata có giúp ích vô cùng rõ rệt ở Câu hỏi #5.** Khi thêm điều kiện pre-filtering `metadata_filter={"audience": "student"}`, kho vector store loại bỏ toàn bộ các tài liệu học phí/quy định dành cho cán bộ, giảng viên hay đối tác bên ngoài. Kết quả trả về 100% tập trung đúng các văn bản học phí dành cho sinh viên, giúp `RecursiveChunker` và `SentenceChunker` đạt điểm tuyệt đối Top-1 (0.7336) và Filter Accuracy đạt **100%**.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
1. **Cấu trúc tài liệu quyết định chiến lược Chunking**: Với tài liệu dạng quy định/dịch vụ hành chính có tiêu đề mục rõ ràng, `RecursiveChunker` vượt trội hoàn toàn so với `FixedSizeChunker` (Hit@3 100% vs 60%).
2. **Nguy cơ lấn át thông tin (Document Overlap Interference)**: Các tài liệu tổng quan (như `hust-scholarships`) dễ có điểm tương tự Cosine cao với câu hỏi học bổng cụ thể (Trần Đại Nghĩa), khiến tài liệu mục tiêu bị đẩy xuống Rank 2 hoặc Rank 3.
3. **Sức mạnh của Pre-filtering Metadata**: Lọc thuộc tính `audience` và `category` trước khi tính similarity giúp giảm nhiễu rác không gian vector, cải thiện độ chính xác truy xuất đáng kể.

**Bài học rút ra khi so sánh trong nhóm:**
> Cùng một bộ tài liệu và câu hỏi benchmark, việc chọn chiến lược chia nhỏ văn bản khác nhau dẫn đến khác biệt lớn về hiệu năng retrieval (Recursive: 8.0 điểm > Sentence: 6.0 điểm > FixedSize: 5.0 điểm). Việc cắt cố định theo số ký tự (`FixedSizeChunker`) tạo ra nhiều lỗi cắt dở câu nhất, trong khi chia theo cấu trúc ngữ đoạn (`RecursiveChunker`) giúp bảo toàn ngữ cảnh thông tin bài toán tốt nhất.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> Nhóm sẽ bổ sung thêm các thuộc tính metadata chi tiết hơn như `sub_category` (ví dụ: `toan_dai_hoc`, `hoc_bong_xa_hoi`) và áp dụng kĩ thuật **Header-Aware Chunking** (gắn thông tin tiêu đề cha `#` vào đầu mỗi chunk con) để khi chunk bị tách nhỏ vẫn giữ được ngữ cảnh của phần mục lớn.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | 10 / 10 |
| Thiết kế chiến lược (Strategy Design) | 15 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 10 / 10 |
| Thuyết trình (Demo) | 5 / 5 |
| **Tổng phần nhóm** | **40 / 40** |
