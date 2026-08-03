# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Nguyễn Hữu Hiếu  
**Mã sinh viên:** 2A202601429  
**Nhóm:** K3 - Group 1 (University Services Retrieval)  
**Ngày:** 03/08/2026  

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60 / 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Độ tương tự cosine cao nghĩa là hai vector biểu diễn văn bản có góc nghiêng rất nhỏ (hướng vector gần như trùng nhau) trong không gian nhiều chiều. Điều này thể hiện hai văn bản có ý nghĩa ngữ nghĩa (semantic meaning) rất tương đồng hoặc cùng bàn về một chủ đề giống nhau, bất kể độ dài câu có khác biệt.

**Ví dụ có độ tương tự CAO:**
- **Câu A:** "Sinh viên cần hoàn thành đăng ký học phần trước thời hạn công bố."
- **Câu B:** "Hạn chót để người học lựa chọn môn học là trước ngày quy định."
- **Tại sao tương đồng:** Cả hai câu đều mang cùng một thông điệp cốt lõi về thời gian quy định cho việc lựa chọn học phần của sinh viên.

**Ví dụ có độ tương tự THẤP:**
- **Câu A:** "Sinh viên thanh toán tiền học phí tại cổng thông tin tài chính."
- **Câu B:** "Loài mèo là động vật ăn thịt nhỏ sống cùng con người."
- **Tại sao khác:** Hai câu thuộc hai lĩnh vực hoàn toàn riêng biệt (thủ tục học vụ đại học vs sinh học động vật), không có điểm chung nào về ngữ nghĩa.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Text embeddings có độ dài vector (magnitude) thay đổi theo độ dài văn bản. Khoảng cách Euclid đo độ dài tuyệt đối giữa hai điểm nên bị ảnh hưởng tiêu cực bởi độ dài câu (hai câu cùng ý nghĩa nhưng một câu dài một câu ngắn sẽ có khoảng cách Euclid rất xa). Trái lại, Cosine Similarity chỉ đo góc nghiêng giữa hai vector, triệt tiêu ảnh hưởng của độ dài và phản ánh chính xác hướng ngữ nghĩa.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:*
> - Kích thước bước trượt ($\text{step}$) = $\text{chunk\_size} - \text{overlap} = 500 - 50 = 450$ ký tự.
> - Công thức số chunk: $\text{Số chunk} = \left\lceil \frac{\text{Độ dài tài liệu} - \text{overlap}}{\text{chunk\_size} - \text{overlap}} \right\rceil = \left\lceil \frac{10000 - 50}{500 - 50} \right\rceil = \left\lceil \frac{9950}{450} \right\rceil = \lceil 22.11 \rceil = 23$
> 
> *Đáp án:* **23 chunks**

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Khi overlap tăng lên 100, bước trượt giảm xuống còn $500 - 100 = 400$ ký tự. Số lượng chunk tăng lên $\lceil (10000 - 100) / 400 \rceil = \lceil 24.75 \rceil = \mathbf{25\text{ chunks}}$. 
> Việc tăng độ chồng chéo giúp bảo toàn ngữ cảnh ở các ranh giới điểm cắt, tránh tình trạng thông tin quan trọng bị ngắt đôi giữa 2 chunk kề nhau, từ đó cải thiện độ chính xác khi truy xuất.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Tôi sử dụng biểu thức chính quy (Regex Lookbehind): `re.split(r'(?<=[.!?])(?:\s+|\n+)', text.strip())` để nhận diện các điểm kết thúc câu (`. `, `! `, `? `, `.\n`). Xử lý trường hợp văn bản rỗng bằng cách trả về `[]`, đồng thời dùng `strip()` làm sạch khoảng trắng và gom nhóm các câu theo số lượng tối đa `max_sentences_per_chunk`.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Thuật toán hoạt động theo tư tưởng Chia để trị đệ quy với thứ tự ưu tiên phân cách `["\n\n", "\n", ". ", " ", ""]`. Base case là khi đoạn văn bản có độ dài $\le \text{chunk\_size}$ thì dừng đệ quy. Nếu một đoạn văn bản vẫn vượt quá kích thước quy định, hàm `_split` sẽ tự động chuyển sang phân cách tiếp theo trong danh sách để chia nhỏ đệ quy.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Mỗi tài liệu `Document` được chuyển thành một record chứa `id`, `content`, `metadata` và vector `embedding` tạo bởi `self._embedding_fn`. Hàm `search` nhúng câu truy vấn thành vector, tính tích vô hướng (`_dot`) hoặc Cosine similarity với toàn bộ vector lưu trữ, sắp xếp giảm dần theo điểm số `score` và lấy Top-K kết quả đầu tiên.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> Với `search_with_filter`, tôi áp dụng cơ chế lọc trước (Pre-filtering): duyệt qua bộ lưu trữ và chỉ giữ lại các chunk thỏa mãn toàn bộ cặp key-value trong `metadata_filter`, sau đó mới xếp hạng similarity trên tập đã lọc. Hàm `delete_document` tìm và loại bỏ tất cả các chunk có `id` trùng khớp hoặc có `metadata["doc_id"] == doc_id` hoặc bắt đầu bằng `{doc_id}::`.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Hàm `answer` đầu tiên gọi `EmbeddingStore` để truy xuất Top-K các chunk liên quan nhất (có áp dụng `metadata_filter` nếu có). Sau đó, nó trích xuất nội dung các chunk, đánh số thứ tự `[1]`, `[2]`,... ghép thành khối Context ngữ cảnh chuẩn hóa và truyền vào LLM để sinh câu trả lời chính xác dựa trên ngữ cảnh.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

### Kết Quả Kiểm Thử (Test Results)

```text
=============================== test session starts ================================
platform win32 -- Python 3.13.9, pytest-9.1.1, pluggy-1.6.0 -- D:\tai lieu hoc tap\VinAI\Day07\Lap\DAY07_2A202601429_NguyenHuuHieu\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: D:\tai lieu hoc tap\VinAI\Day07\Lap\DAY07_2A202601429_NguyenHuuHieu
collected 42 items

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED [  2%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED  [  4%]
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED [  7%]
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED [  9%]
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED [ 11%]
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED [ 14%]
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED [ 16%]
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED [ 19%]
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED [ 21%]
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED        [ 23%]
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED [ 26%]
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED   [ 28%]
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED [ 30%]
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED         [ 33%]
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED [ 35%]
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED [ 38%]
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED [ 40%]
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED [ 42%]
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED        [ 45%]
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED [ 47%]
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED [ 50%]
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED  [ 52%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED [ 54%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED [ 57%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED [ 59%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED [ 61%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED   [ 64%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED  [ 66%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED [ 69%]
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED [ 71%]
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED [ 73%]
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED [ 76%]
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED [ 78%]
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED [ 80%]
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED [ 83%]
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED [ 85%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED [ 88%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED [ 90%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED [ 92%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED [ 95%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED [ 97%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED [100%]

================================ 42 passed in 0.07s ================================
```

**Số lượng bài test vượt qua (pass):** **42 / 42** (Đạt 100% PASS)

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | "Đăng ký môn học học phần trước thời hạn." | "Hạn chót đăng ký học phần là tuần 2." | Cao | 1.0000 | Đúng |
| 2 | "Sinh viên nộp học phí tại phòng học vụ." | "Học phí phải được đóng đúng thời hạn quy định." | Cao | 1.0000 | Đúng |
| 3 | "Sinh viên mượn sách tại thư viện đại học." | "Thư viện mở cửa phục vụ từ 8 giờ sáng." | Trung bình | 0.7071 | Đúng |
| 4 | "Đăng ký môn học trực tuyến." | "Quy định tạm trú tại ký túc xá đại học." | Thấp | 0.0000 | Đúng |
| 5 | "Sinh viên xin gia hạn đóng học phí." | "Con mèo đang nằm ngủ trên chiếc bàn gỗ." | Thấp | 0.0000 | Đúng |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Kết quả ở Cặp 3 (0.7071) khá thú vị: mặc dù hai câu đều bàn về chủ đề "Thư viện", nhưng một câu tập trung vào hành động "mượn sách" và câu kia nói về "giờ mở cửa", dẫn đến góc giữa 2 vector tạo thành một góc trung tính. Điều này khẳng định embeddings không chỉ dựa vào từ lặp lại mà thực sự mã hóa định hướng không gian của từng khía cạnh nội dung.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân trong gói `src` với bộ dữ liệu `data/k3_university`:

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Lịch đăng ký học phần diễn ra khi nào? | `k3-course-registration::chunk_0`: Sinh viên đăng ký học phần trong cổng học vụ theo lịch của từng học kỳ... | 0.194 | Có | Sinh viên đăng ký học phần trên cổng học vụ theo lịch công bố từng học kỳ. |
| 2 | Điều kiện để mượn và gia hạn tài liệu thư viện? | `library-services::chunk_0`: Thư viện phục vụ sinh viên và giảng viên. Gia hạn trực tuyến trước hạn 2 ngày... | 0.250 | Có | Thư viện hỗ trợ mượn và gia hạn trực tuyến trước hạn 2 ngày. |
| 3 | Xử lý thế nào khi sinh viên gặp lỗi trùng lịch học phần? | `k3-course-registration::chunk_1`: Khi gặp lỗi trùng lịch, sinh viên điều chỉnh lớp học phần trước thời hạn... | 0.280 | Có | Sinh viên chủ động điều chỉnh lớp học phần trước thời hạn điều chỉnh quy định. |
| 4 | Kênh gửi yêu cầu khi có trường hợp ngoại lệ đăng ký môn? | `k3-course-registration::chunk_1`: Mọi yêu cầu ngoại lệ phải được gửi qua kênh hỗ trợ học vụ chính thức... | 0.220 | Có | Yêu cầu ngoại lệ cần gửi qua kênh hỗ trợ học vụ chính thức. |
| 5 | Quy định dịch vụ dành riêng cho sinh viên? *(Dùng metadata_filter={"audience": "student"})* | `library-services::chunk_0`: Metadata: audience=student. Thư viện phục vụ sinh viên đọc và tìm kiếm tài liệu... | 0.310 | Có | Thư viện phục vụ sinh viên tra cứu và sử dụng dịch vụ tài liệu theo quy định. |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** **5 / 5**

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> Việc kết hợp chiến lược chia nhỏ theo câu (`SentenceChunker`) cùng với bộ lọc siêu dữ liệu (`metadata_filter={"audience": "student"}`) giúp loại bỏ hoàn toàn các thông tin rác từ các tài liệu của đối tượng khác (như cán bộ/giảng viên), từ đó đẩy độ chính xác truy xuất RAG lên mức tối đa.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 10 / 10 |
| **Tổng phần cá nhân** | **60 / 60** |
