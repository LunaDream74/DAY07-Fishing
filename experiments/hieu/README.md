# Experiment Folder: FixedSizeChunker Strategy (Author: Hieu)

Thư mục này chứa thí nghiệm độc lập cho chiến lược **FixedSizeChunker** trên tập dữ liệu dùng chung `data/hust_services/`.

## 📌 Quy Định Tuân Thủ (`AGENTS.md`)
1. **Không chỉnh sửa tập tài liệu gốc**: Mọi thuộc tính metadata cá nhân bổ sung được khai báo trong `metadata_overrides.json` và nạp vào bộ nhớ.
2. **Chiến lược áp dụng**: `FixedSizeChunker(chunk_size=400, overlap=50)`.
3. **Mô hình Embedder**: Sử dụng `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (`EMBEDDING_PROVIDER=local` hoặc `LocalEmbedder`).

## 🚀 Cách Chạy Thử Nghiệm
```powershell
python experiments/hieu/run_experiment.py
```
