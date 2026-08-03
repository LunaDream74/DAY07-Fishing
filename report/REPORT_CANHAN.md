# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Trần Nguyễn Anh Minh
**Nhóm:** [Điền sau]
**Ngày:** 03/08/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Hai embedding có hướng gần giống nhau trong không gian vector, nên hai đoạn văn thường nói về nội dung hoặc ý định tương tự. Điểm càng gần 1 thì mức tương đồng theo embedding càng cao.

**Ví dụ có độ tương tự CAO:**
- Câu A: Sinh viên cần nộp học phí trước ngày nào?
- Câu B: Hạn cuối thanh toán học phí của học kỳ là khi nào?
- Tại sao tương đồng: Cả hai cùng hỏi thời hạn đóng học phí.

**Ví dụ có độ tương tự THẤP:**
- Câu A: Thư viện mở cửa vào lúc mấy giờ?
- Câu B: Cá voi xanh là loài động vật lớn nhất.
- Tại sao khác: Hai câu thuộc hai chủ đề hoàn toàn khác nhau: dịch vụ thư viện và sinh học.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Cosine đo góc giữa các vector nên tập trung vào hướng/ngữ nghĩa và ít bị ảnh hưởng bởi độ lớn vector. Với text embeddings, độ lớn thường không phản ánh trực tiếp độ giống nghĩa, vì vậy cosine thường phù hợp hơn Euclidean distance.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:* ceil((10.000 - 50) / (500 - 50)) = ceil(9.950 / 450) = ceil(22,11).
> *Đáp án:* 23 chunks.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Số chunk là ceil((10.000 - 100) / (500 - 100)) = ceil(9.900 / 400) = 25, nên tăng từ 23 lên 25. Overlap lớn hơn giữ lại ngữ cảnh ở ranh giới chunk, giảm nguy cơ một ý hoặc câu bị tách rời; đổi lại dữ liệu lưu trữ và xử lý bị lặp nhiều hơn.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Tôi dùng regex `(?<=[.!?])(?:\s+|$)` để tách tại khoảng trắng hoặc xuống dòng sau dấu kết câu, đồng thời giữ dấu câu trong nội dung câu. Các câu rỗng sau khi tách được bỏ đi; đầu vào rỗng hoặc chỉ có khoảng trắng trả về danh sách rỗng. Các câu được ghép lại theo đúng giới hạn `max_sentences_per_chunk`.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Thuật toán thử lần lượt các separator ưu tiên: đoạn văn, dòng, câu, từ rồi đến cắt theo ký tự. Nó ghép các phần nhỏ nhất có thể trong giới hạn `chunk_size`; phần vẫn quá dài được gọi đệ quy với separator tiếp theo. Base case là đoạn đã đủ ngắn, hết separator, hoặc separator rỗng, khi đó đoạn được trả về/cắt cứng theo kích thước.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Mỗi `Document` được chuẩn hóa thành record gồm ID duy nhất, nội dung, metadata, và embedding; store ưu tiên ChromaDB nếu khả dụng, nếu không dùng danh sách trong bộ nhớ. Khi tìm kiếm, query được embed rồi chấm điểm từng record bằng dot product, sắp xếp giảm dần và lấy `top_k` kết quả.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> `search_with_filter` lọc metadata trước, rồi chỉ xếp hạng các record còn lại để tránh kết quả sai đối tượng. `delete_document` dùng trường metadata `doc_id` để xóa mọi chunk của cùng một tài liệu và trả về `True` khi có ít nhất một chunk bị xóa.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Agent truy xuất `top_k` chunks trước, đánh số và ghép chúng thành phần Context trong prompt. Prompt yêu cầu LLM chỉ trả lời dựa trên context và nói rõ khi context không đủ, sau đó gọi `llm_fn` để tạo câu trả lời.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
python -m unittest discover -s tests -v
Ran 42 tests in 0.023s
OK
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Học phí được thanh toán trước hạn nào? | Hạn cuối đóng học phí của học kỳ là khi nào? | cao nhất | 0,1913 | Không |
| 2 | Thư viện mở cửa lúc nào? | Sinh viên mượn sách tại thư viện ra sao? | cao | 0,1285 | Không |
| 3 | Quy trình đăng ký học phần như thế nào? | Cách hủy một môn học đã đăng ký? | cao | -0,2076 | Không |
| 4 | Học bổng xét theo tiêu chí nào? | Máy tính lượng tử dùng qubit để tính toán. | thấp | 0,0600 | Không |
| 5 | Ký túc xá có giờ giới nghiêm không? | Cá voi xanh là loài động vật lớn nhất. | thấp nhất | 0,3256 | Không |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Cặp 5, vốn không liên quan về nghĩa, lại có điểm cao nhất; cặp 3 có cùng chủ đề đăng ký học phần lại thấp nhất. Thí nghiệm này dùng `_mock_embed`, vốn sinh vector xác định theo chuỗi nhưng không biểu diễn ngữ nghĩa, nên kết quả xác nhận không thể dùng mock embedder để đánh giá retrieval. Khi làm phần nhóm cần dùng local multilingual embedder như hướng dẫn.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Chờ 5 benchmark queries chung của nhóm | — | — | — | — |
| 2 | Chờ 5 benchmark queries chung của nhóm | — | — | — | — |
| 3 | Chờ 5 benchmark queries chung của nhóm | — | — | — | — |
| 4 | Chờ 5 benchmark queries chung của nhóm | — | — | — | — |
| 5 | Chờ 5 benchmark queries chung của nhóm | — | — | — | — |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** Chờ đánh giá chung của nhóm.

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> Chờ hoàn thành demo và so sánh cùng nhóm.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | Chờ phần nhóm / 10 |
| **Tổng phần cá nhân hiện tại** | **50 / 50; chờ 10 điểm retrieval** |
