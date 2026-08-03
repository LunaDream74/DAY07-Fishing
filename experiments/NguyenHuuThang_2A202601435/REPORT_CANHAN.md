# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Nguyễn Hữu Thắng

**MSSV:** 2A202601435

**Nhóm:** K3 — Retrieval Quy Định & Dịch Vụ Đại Học

**Ngày:** 03/08/2026

> Báo cáo này mô tả phần lập trình cá nhân và thí nghiệm retrieval dùng
> `SentenceChunker`. Phần dữ liệu, benchmark chung và so sánh ba thành viên được
> trình bày trong `report/REPORT_NHOM.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn
thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất (10).

---

## 1. Khởi động (Warm-up) — 5 điểm

### 1.1. Độ tương tự cosine

**Cosine similarity cao nghĩa là gì?**

Cosine similarity đo góc giữa hai vector. Điểm gần 1 cho biết hai embedding có
hướng gần nhau; với một embedding model có chất lượng, điều này thường tương ứng
với nội dung hoặc ý định gần nhau. Điểm cao chỉ là tín hiệu xếp hạng, không tự
chứng minh chunk chứa câu trả lời.

**Ví dụ có độ tương tự dự kiến cao:**

- Câu A: “Sinh viên cần nộp học phí trước ngày nào?”
- Câu B: “Hạn cuối thanh toán học phí của học kỳ là khi nào?”
- Hai câu cùng hỏi thời hạn đóng học phí, chỉ khác cách diễn đạt.

**Ví dụ có độ tương tự dự kiến thấp:**

- Câu A: “Thư viện mở cửa vào lúc mấy giờ?”
- Câu B: “Cá voi xanh là loài động vật lớn nhất.”
- Hai câu thuộc hai miền nội dung không liên quan.

**Vì sao thường dùng cosine thay vì Euclidean distance cho text embedding?**

Cosine tập trung vào hướng của vector và ít bị ảnh hưởng bởi độ lớn. Hướng
vector thường mang thông tin ngữ nghĩa quan trọng hơn độ lớn đối với văn bản.
Trong thí nghiệm này, local embedder còn chuẩn hóa vector về norm 1, nên dot
product trong store tương đương cosine similarity.

### 1.2. Bài toán số lượng chunk

Với tài liệu dài `L = 10.000`, `chunk_size = 500`, `overlap = 50`, bước trượt là:

```text
step = 500 - 50 = 450
chunks = ceil((10.000 - 50) / 450) = ceil(22,11) = 23
```

Nếu tăng overlap lên 100:

```text
step = 500 - 100 = 400
chunks = ceil((10.000 - 100) / 400) = ceil(24,75) = 25
```

Số chunk tăng từ 23 lên 25. Overlap lớn hơn giúp một ý nằm gần ranh giới có thêm
cơ hội xuất hiện nguyên vẹn ở chunk kế tiếp, đổi lại tăng nội dung lặp, dung
lượng lưu trữ và chi phí embedding.

---

## 2. Hướng tiếp cận của tôi (My Approach) — 10 điểm

### 2.1. Các chiến lược chunking

**`SentenceChunker.chunk`**

Tôi dùng regex:

```python
r"(?:(?<=[.!?])[ \t]+|(?<=\.)\n+)"
```

Regex tách sau dấu kết câu nhưng giữ dấu câu trong nội dung. Các mảnh rỗng được
loại bỏ và các câu được ghép theo `max_sentences_per_chunk`. Đầu vào rỗng hoặc
chỉ có khoảng trắng trả về danh sách rỗng.

**`RecursiveChunker.chunk` / `_split`**

Thuật toán thử lần lượt ranh giới đoạn, dòng, câu, từ và cuối cùng là ký tự. Mỗi
cấp cố gắng ghép các đơn vị mà không vượt `chunk_size`; phần quá dài được xử lý
đệ quy bằng separator kế tiếp. Khi không còn separator hữu ích, thuật toán cắt
cứng để luôn tiến triển và không sinh chunk rỗng.

**`compute_similarity` và `ChunkingStrategyComparator`**

`compute_similarity` tính dot product chia cho tích hai norm và trả `0.0` nếu
một vector có độ lớn bằng 0. Comparator chạy ba built-in chunker trên cùng văn
bản và trả số chunk, độ dài trung bình cùng nội dung từng chunk. Khi làm baseline
tôi gọi `parse_front_matter()` trước để không đưa YAML vào số liệu.

### 2.2. EmbeddingStore

- `add_documents()` tạo ID duy nhất, giữ toàn bộ metadata và embedding của từng
  `Document`. Một chunk đi vào store là một record; chunking xảy ra trước store.
- `search()` embed query, tính similarity, sắp xếp giảm dần và lấy top-k. Store
  ưu tiên ChromaDB nếu khả dụng và duy trì bản mirror trong bộ nhớ để fallback.
- `search_with_filter()` lọc record bằng metadata trước khi xếp hạng. Nhờ
  `ingest.py` trải front matter lên mọi chunk, bộ lọc `audience` có dữ liệu để
  hoạt động.
- `delete_document()` xóa tất cả chunk có cùng `metadata["doc_id"]`, không chỉ
  một chunk ID.

### 2.3. KnowledgeBaseAgent

Agent truy xuất top-k, gắn số thứ tự và nguồn cho từng chunk, sau đó tạo prompt
yêu cầu chỉ trả lời từ context và thừa nhận khi thiếu thông tin. `llm_fn` được
tiêm từ ngoài để tách retrieval khỏi backend sinh câu trả lời. Trong benchmark
cá nhân tôi dùng một hàm extractive offline: nó trả lại bằng chứng truy xuất để
kiểm tra grounding, không giả vờ là một LLM tổng hợp đầy đủ.

### 2.4. Strategy retrieval cá nhân

Chọn đúng một built-in strategy:

```python
chunker = SentenceChunker(max_sentences_per_chunk=2)
```

Hai câu liên tiếp thường cùng mô tả một lịch, điều kiện hoặc bước thủ tục. Giới
hạn hai câu giữ quan hệ này nhưng tránh cấu hình ba câu gom gần như toàn bộ một
tài liệu ngắn. Thí nghiệm dùng nguyên 10 tài liệu chung, 5 query chung và local
multilingual embedder; `metadata_overrides.json` để trống nên biến khác biệt
chính là strategy chunking.

Hạn chế dự kiến là SentenceChunker không có giới hạn cứng theo ký tự, không có
overlap và không hiểu heading Markdown. Một câu rất dài vẫn tạo chunk lớn; các
chunk phía sau cũng có thể mất title của tài liệu.

---

## 3. Hoàn thiện code (Core Implementation) — 30 điểm

Tôi chạy test trực tiếp trên package cá nhân, không dùng nhầm `src/` tại root:

```text
Testing package: .../experiments/NguyenHuuThang_2A202601435/src/__init__.py
.......................................... [100%]
42 passed in 0.04s
```

**Kết quả:** 42/42 tests pass.

Các nhóm hành vi đã được kiểm tra gồm API/class, SentenceChunker,
RecursiveChunker, cosine similarity, comparator, EmbeddingStore, metadata
filter, delete theo `doc_id` và KnowledgeBaseAgent.

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — 5 điểm

Tôi dự đoán trước theo ngữ nghĩa, sau đó đo bằng `MockEmbedder` trong package cá
nhân. Mock tạo vector xác định từ hash của chuỗi nhưng không học ngữ nghĩa.

| Cặp | Nội dung rút gọn | Dự đoán | Điểm thực tế | Đánh giá dự đoán |
|---:|---|---|---:|---|
| 1 | Hai cách hỏi hạn đóng học phí | Cao nhất | -0,0958 | Sai; thực tế thấp nhất |
| 2 | Giờ mở cửa và cách mượn sách thư viện | Cao | -0,0540 | Sai |
| 3 | Đăng ký và hủy học phần | Cao | -0,0473 | Sai |
| 4 | Tiêu chí học bổng và máy tính lượng tử | Thấp | -0,0388 | Không phản ánh đúng thứ tự mong đợi |
| 5 | Giờ ký túc xá và cá voi xanh | Thấp nhất | 0,1561 | Sai; thực tế cao nhất |

Kết quả bất ngờ nhất là cặp 5 hoàn toàn không liên quan lại có score cao nhất,
trong khi cặp 1 đồng nghĩa lại thấp nhất. Đây không phải bằng chứng cosine sai;
nó cho thấy embedding đầu vào không mã hóa ngữ nghĩa. Vì vậy tôi chỉ dùng mock
cho unit test và dùng `paraphrase-multilingual-MiniLM-L12-v2` cho benchmark
retrieval tiếng Việt.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — 10 điểm

### 5.1. Cấu hình

| Thành phần | Giá trị |
|---|---|
| Corpus | `data/hust_services/` — 10 tài liệu |
| Chunker | `SentenceChunker(max_sentences_per_chunk=2)` |
| Embedder | `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` |
| Số chunk | 32 |
| Top-k | 3 |
| Metadata override | Không có |
| Query có filter | Query 5 — `{"audience": "student"}` |

Kết quả tự động theo `doc_id`: **6,0/10**, Hit@1 **60%**, Hit@3 **60%**, filter
accuracy **100%**. Tuy nhiên, tôi audit thêm nội dung chunk vì đúng `doc_id` chưa
chắc chứa bằng chứng trả lời. Theo rubric chunk + agent, kết quả thận trọng là
**5,0/10**.

### 5.2. Kết quả từng query

| # | Top-1 (`doc_id`, score) | Evidence trong top-3 | Agent extractive và đánh giá | Điểm audit |
|---:|---|---|---|---:|
| 1 | `hust-course-registration-20261`, 0,7204 | Hạng 1 có chính thức + điều chỉnh; hạng 2 có đăng ký thêm. | Ghép đủ ba đợt và đúng mốc thời gian; có một chunk biên lai nhiễu ở hạng 3. | 2/2 |
| 2 | `hust-scholarships`, 0,7676 | Không có `CPA từ 2,0`, rèn luyện 65 hay nhóm rủi ro trong top-3. | Chỉ trả mô tả học bổng tổng quan, không trả được điều kiện chi tiết. | 0/2 |
| 3 | `hust-student-administrative-procedures`, 0,7157 | Không có `Đơn xin đăng ký vào lớp đầy` hoặc hạn 05–11/02/2026. | Context gồm thủ tục hành chính và đăng ký kỳ 2026.1, nên không thể trả lời đúng. | 0/2 |
| 4 | `hust-student-administrative-procedures`, 0,6870 | Chunk quy trình thật ở hạng 3: tự in mẫu, lớp trưởng tổng hợp, ảnh 3x4. | Có grounding nhưng bằng chứng chính không đứng top-1 và câu trả lời còn lẫn context trao đổi quốc tế. | 1/2 |
| 5 | `hust-tuition-information`, 0,7336 | Top-1 nói phải xem đúng năm học và chương trình; corpus không có con số cụ thể. | Trả lời đúng giới hạn dữ liệu, không suy diễn mức tiền. | 2/2 |

**Số query có ít nhất một chunk chứa bằng chứng trong top-3:** 3/5 (60%).

### 5.3. Failure case chính: Học bổng Trần Đại Nghĩa

Query: **“Điều kiện và đối tượng được xét trao Học bổng Trần Đại Nghĩa là gì?”**

| Rank | Score | Chunk | Nội dung và mức liên quan |
|---:|---:|---|---|
| 1 | 0,7676 | `hust-scholarships::chunk_2` | Học bổng tài trợ cho sinh viên học tốt/khó khăn; sai chương trình. |
| 2 | 0,7558 | `hust-scholarships::chunk_1` | Có tên Trần Đại Nghĩa nhưng chỉ nói “khó khăn, nghị lực”; thiếu CPA và điểm rèn luyện. |
| 3 | 0,7378 | `hust-scholarships::chunk_4` | Học bổng gắn kết quê hương; không chứa điều kiện cần hỏi. |

Score cao ở đây chỉ cho biết các chunk cùng chủ đề học bổng. Trang tổng quan có
nhiều câu ngắn, mỗi câu trở thành một chunk và chiếm cả ba vị trí. Chunk chính
sách chi tiết không lọt top-3, nên agent không có bằng chứng về `CPA từ 2,0`,
điểm rèn luyện từ 65 hoặc nhóm sinh viên gặp rủi ro.

**Thay đổi đề xuất:** gắn title/heading vào mỗi sentence chunk, thêm overlap một
câu hoặc rerank bằng metadata kiểu tài liệu (`eligibility-policy`). Nếu được dùng
custom domain chunker, tôi sẽ tách theo heading trước; section dài mới fallback
về Sentence/Recursive và gắn lại heading vào mọi mảnh con.

### 5.4. Phân tích filter và grounding

Query 5 được chạy với `metadata_filter={"audience": "student"}` và filter
accuracy đạt 100%. Tuy nhiên, cả 10 tài liệu hiện đều có `audience: student`, nên
A/B có và không filter cho cùng top-3. Filter hoạt động đúng về kỹ thuật nhưng
không làm giảm nhiễu trong corpus đồng nhất này; muốn đo utility thực sự cần tài
liệu cho nhiều audience hoặc một filter có tính phân biệt hơn.

Agent extractive luôn dựa trên context, nên không bịa ngoài top-k. Điểm yếu là
nó có thể lặp lại context nhiễu và không tự nhận biết một chunk chỉ đúng chủ đề
nhưng thiếu đáp án. Do đó tôi kiểm evidence đặc trưng bên cạnh similarity score.

### 5.5. Điều học được từ so sánh nhóm

- `RecursiveChunker(chunk_size=450)` đạt điểm `doc_id` cao nhất (8/10, Hit@3
  100%) vì phù hợp cấu trúc đoạn/section của Markdown.
- `FixedSizeChunker` kiểm soát kích thước và có overlap nhưng có thể cắt giữa
  từ/câu; SentenceChunker giữ câu tốt hơn nhưng tạo nhiều chunk cạnh tranh.
- Bài học quan trọng nhất là không chấm chỉ bằng `doc_id`. Ví dụ đúng tài liệu
  nhưng sai section vẫn không cung cấp bằng chứng cho agent.

---

## 6. Tự đánh giá

| Tiêu chí | Điểm tự đánh giá | Cơ sở |
|---|---:|---|
| Khởi động | 5/5 | Hoàn thành cosine và phép tính chunking. |
| Hướng tiếp cận | 10/10 | Giải thích các phần chính và strategy cá nhân. |
| Hoàn thiện code | 30/30 | Package cá nhân vượt 42/42 tests. |
| Dự đoán độ tương tự | 5/5 | Có dự đoán, số đo thật và phản ngẫm về mock. |
| Kết quả truy xuất | 5/10 | Chấm thận trọng theo bằng chứng chunk + agent, không chỉ `doc_id`. |
| **Tổng** | **55/60** | Điểm retrieval tự động theo `doc_id` là 6/10; audit nội dung là 5/10. |

---

## 7. Tệp minh chứng

- `experiments/NguyenHuuThang_2A202601435/src/` — mã nguồn cá nhân.
- `experiments/NguyenHuuThang_2A202601435/bench.py` — script benchmark.
- `experiments/NguyenHuuThang_2A202601435/results/sentence_benchmark.md` — top-3,
  score và agent answer cho 5 query.
- `experiments/NguyenHuuThang_2A202601435/metadata_overrides.json` — metadata
  override để trống, bảo toàn corpus dùng chung.
- `report/REPORT_NHOM.md` — dữ liệu, benchmark và so sánh strategy của nhóm.
