# Chiến lược retrieval cá nhân — HUST services

## Chiến lược duy nhất được dùng

Tôi dùng **`RecursiveChunker`** duy nhất cho toàn bộ corpus HUST:

```python
chunker = RecursiveChunker(
    separators=["\n\n", "\n", ". ", " ", ""],
    chunk_size=450,
)
```

Corpus là Markdown đã làm sạch, có tiêu đề và các đoạn ngắn. Recursive chunking ưu tiên giữ nguyên đoạn/section, sau đó mới tách theo dòng, câu, từ và ký tự nếu cần. `chunk_size=450` hướng đến chunk đủ bối cảnh cho điều kiện, mốc thời gian và quy trình, đồng thời tránh gom nhiều dịch vụ độc lập vào một chunk. Không dùng `FixedSizeChunker` hay `SentenceChunker` khi chạy benchmark cá nhân.

## Metadata profile

Ngoài metadata bắt buộc (`doc_id`, `source_url`, `retrieved_at`, `document_version`, `audience`), profile này dùng:

| Field | Mục đích | Ví dụ |
|---|---|---|
| `service_domain` | Lọc theo miền dịch vụ | `academic`, `finance`, `international` |
| `document_type` | Phân biệt lịch, quy trình, chính sách | `term-schedule`, `procedure`, `eligibility-policy` |
| `validity_scope` | Nhận biết độ nhạy thời gian | `term-specific`, `academic-year`, `ongoing` |

Các trường này được lưu trong `experiments/minh/metadata_overrides.json` và chỉ được thêm trong bộ nhớ lúc index; shared corpus không bị thay đổi. Ví dụ: `search_with_filter(query, metadata_filter={"service_domain": "finance"})` chỉ tìm trong tài liệu học phí và học bổng. Benchmark bắt buộc theo K3 vẫn dùng ít nhất một lần `metadata_filter={"audience": "student"}`.
