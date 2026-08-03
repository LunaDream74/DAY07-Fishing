# Thí nghiệm SentenceChunker — Nguyễn Hữu Thắng

Thí nghiệm dùng đúng 10 tài liệu trong `data/hust_services`, năm query chung ở
`scripts/benchmark.py` và local multilingual embedder
`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`.

Chỉ có strategy chunking khác với các thành viên khác:

```python
chunker = SentenceChunker(max_sentences_per_chunk=2)
```

Hai câu liên tiếp thường cùng mô tả một điều kiện, lịch hoặc quy trình. Giới hạn
hai câu giúp giữ quan hệ này trong cùng chunk, đồng thời tránh trường hợp cấu
hình mặc định ba câu gom gần như toàn bộ một tài liệu ngắn vào một record.
SentenceChunker không dùng overlap và không có giới hạn cứng theo ký tự; đây là
điểm yếu cần theo dõi ở những câu rất dài.

`metadata_overrides.json` để trống nhằm giữ nguyên metadata của corpus. Đặc biệt,
query số 5 vẫn chạy với `metadata_filter={"audience": "student"}` lấy trực tiếp
từ front matter dùng chung.

Chạy benchmark:

```powershell
$env:EMBEDDING_PROVIDER="local"
.\experiments\NguyenHuuThang_2A202601435\.venv\Scripts\python.exe experiments\NguyenHuuThang_2A202601435\bench.py
```

`local` là backend mặc định. Model đã được lưu trong cache của môi trường thí
nghiệm và script bật chế độ Hugging Face offline, nên các lần chạy sau không tải
lại checkpoint.

Script thực hiện cả baseline trên ba tài liệu sau khi gọi
`parse_front_matter()`, xây store bằng `build_knowledge_base()`, chạy năm query,
và lưu top-3 cùng câu trả lời agent vào `results/sentence_benchmark.md`.
