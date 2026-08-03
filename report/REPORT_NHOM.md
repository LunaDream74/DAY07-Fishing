# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** [Tên nhóm]
**Thành viên:** [Họ tên từng thành viên]
**Ngày:** [Ngày nộp]

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Phạm vi bộ tài liệu (Scope)

**Chủ đề (cố định theo lớp K3):** Dịch vụ / quy định đại học (đăng ký môn, học phí, học bổng, thư viện, ký túc xá…).

**Phạm vi cụ thể nhóm tập trung:**
> *1 câu — ví dụ: thư viện + đăng ký môn học.*

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [ ] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [ ] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| | | | |
| | | | |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

Đã gọi `parse_front_matter()` và chỉ truyền phần thân tài liệu vào
`ChunkingStrategyComparator.compare(body, chunk_size=200)`, do đó số liệu không
bao gồm khối YAML.

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------:|-------------------:|-------------------|
| Đăng ký lớp kỳ 2026.1 | FixedSizeChunker (`fixed_size`) | 7 | 183,4 | Trung bình: kích thước đều nhưng có thể cắt giữa câu hoặc danh sách. |
| Đăng ký lớp kỳ 2026.1 | SentenceChunker (`by_sentences`) | 3 | 326,3 | Tốt ở ranh giới câu; một chunk có thể chứa nhiều mục liên tiếp. |
| Đăng ký lớp kỳ 2026.1 | RecursiveChunker (`recursive`) | 9 | 107,8 | Giữ ranh giới Markdown nhưng tạo một số chunk tiêu đề rất ngắn. |
| Thủ tục hành chính sinh viên | FixedSizeChunker (`fixed_size`) | 6 | 185,2 | Trung bình: có nguy cơ tách giấy tờ khỏi bước xử lý tương ứng. |
| Thủ tục hành chính sinh viên | SentenceChunker (`by_sentences`) | 3 | 285,7 | Khá tốt: mỗi quy trình vẫn nguyên câu, nhưng chunk tương đối dài. |
| Thủ tục hành chính sinh viên | RecursiveChunker (`recursive`) | 8 | 106,1 | Giữ đoạn/mục tốt, đổi lại có nhiều mảnh ngắn. |
| Học bổng Trần Đại Nghĩa | FixedSizeChunker (`fixed_size`) | 4 | 197,2 | Trung bình: câu điều kiện dài bị cắt theo ký tự. |
| Học bổng Trần Đại Nghĩa | SentenceChunker (`by_sentences`) | 1 | 637,0 | Giữ trọn câu nhưng gom cả tài liệu, làm giảm độ chi tiết retrieval. |
| Học bổng Trần Đại Nghĩa | RecursiveChunker (`recursive`) | 4 | 158,5 | Cân bằng hơn về kích thước, nhưng có thể tách tiêu đề khỏi nội dung. |

### Chiến lược của từng thành viên

> Mỗi thành viên điền một khối dưới đây (copy thêm nếu nhóm có nhiều hơn 3 người).

**Thành viên 1 — [Tên]**
- **Loại chiến lược:** [FixedSize / Sentence / Recursive / custom]
- **Mô tả & lý do chọn cho chủ đề này:** *(2-3 câu)*
- **Code snippet (nếu custom):**
```python
# Dán mã nguồn (implementation) vào đây
```

**Thành viên 2 — [Tên]**
- **Loại chiến lược:**
- **Mô tả & lý do chọn:**
- **Code snippet (nếu custom):**

**Thành viên 3 — Nguyễn Hữu Thắng**
- **Loại chiến lược:** `SentenceChunker(max_sentences_per_chunk=2)`
- **Mô tả & lý do chọn:** Hai câu liên tiếp thường cùng mô tả một điều kiện,
  lịch hoặc quy trình, nên giữ chúng trong cùng chunk giúp bảo toàn ngữ cảnh.
  Giới hạn hai câu cũng tránh trường hợp cấu hình mặc định ba câu gom gần như
  toàn bộ một tài liệu ngắn vào một record. Điểm yếu là không có giới hạn cứng
  theo ký tự, nên một câu rất dài vẫn có thể tạo chunk quá lớn.
- **Code snippet (built-in):**
```python
chunker = SentenceChunker(max_sentences_per_chunk=2)
```

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Nguyễn Hữu Thắng | SentenceChunker (2 câu/chunk) | 6,0 | Không cắt giữa câu; lịch đăng ký, thủ tục và học phí đạt Top-1. | Tài liệu gần chủ đề lấn át query học bổng Trần Đại Nghĩa và đăng ký bổ sung Toán. |
| | | | | |
| | | | | |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> *Viết 2-3 câu — đây là phần được đánh giá cao nhất (khả năng suy nghĩ & giải thích):*

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | | | |
| 2 | | | |
| 3 | | | |
| 4 | | | |
| 5 | | | |

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> *Viết 2-3 câu:*

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
> *Liệt kê 2-3 ý:*

**Bài học rút ra khi so sánh trong nhóm:**
> *Viết 2-3 câu — cùng tài liệu nhưng chiến lược khác nhau dẫn tới khác biệt gì?*

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> *Viết 2-3 câu:*

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | / 10 |
| Thiết kế chiến lược (Strategy Design) | / 15 |
| Chất lượng truy xuất (Retrieval Quality) | / 10 |
| Thuyết trình (Demo) | / 5 |
| **Tổng phần nhóm** | **/ 40** |
