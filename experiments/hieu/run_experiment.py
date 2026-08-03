"""Script thực thi đánh giá benchmark cho FixedSizeChunker (Thủ nghiệm cá nhân Hieu)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from experiments.hieu.config import CHUNKER, build_store
from scripts.benchmark import evaluate_store, generate_markdown_report
from src.embeddings import LocalEmbedder, MockEmbedder


def get_embedder():
    """Lấy embedder dựa trên môi trường hoặc fallback."""
    provider = os.getenv("EMBEDDING_PROVIDER", "local").lower()
    if provider == "local":
        try:
            print("[INFO] Dang khoi tao LocalEmbedder (sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2)...")
            embedder = LocalEmbedder()
            print("[OK] Su dung LocalEmbedder thanh cong.")
            return embedder
        except Exception as err:
            print(f"[WARN] Khong the tai LocalEmbedder ({err}). Chuyen sang MockEmbedder fallback.")
            return MockEmbedder()
    else:
        print("[INFO] Su dung MockEmbedder theo cau hinh moi truong.")
        return MockEmbedder()



def main():
    embedder = get_embedder()
    print("[INFO] Dang nap du lieu va xay dung Vector Store voi FixedSizeChunker(chunk_size=400, overlap=50)...")
    store = build_store(embedder)
    print(f"[OK] Vector Store hoan tat. Tong so chunks: {store.get_collection_size()}")

    print("[INFO] Dang chay bo danh gia 5 Benchmark Queries...")
    summary = evaluate_store(store, top_k=3)

    report_md = generate_markdown_report(summary, store_name=f"FixedSizeChunker (size={CHUNKER.chunk_size}, overlap={CHUNKER.overlap})")

    # Lưu log vào my_workspace/logs/
    log_dir = PROJECT_ROOT / "my_workspace" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "LOG_v1.0_20260803_fixed_size_benchmark.md"

    log_content = f"""---
title: "Log Benchmark: FixedSizeChunker Evaluation"
version: "v1.0"
date: "2026-08-03"
author: "NguyenHuuHieu"
total_score: {summary.total_score}
hit_rate_at_1: {summary.hit_rate_at_1}
hit_rate_at_3: {summary.hit_rate_at_3}
filter_accuracy: {summary.filter_accuracy}
---

{report_md}
"""
    log_file.write_text(log_content, encoding="utf-8")
    print(f"[OK] Da luu bao cao benchmark vao: {log_file}")
    print("\n" + "=" * 60)
    print(f"[BENCHMARK RESULT] KET QUA BENCHMARK: {summary.total_score:.1f} / 10.0 DIEM")
    print(f"   - Hit Rate @ 1: {summary.hit_rate_at_1 * 100:.1f}%")
    print(f"   - Hit Rate @ 3: {summary.hit_rate_at_3 * 100:.1f}%")
    print(f"   - Metadata Filter Accuracy: {summary.filter_accuracy * 100:.1f}%")
    print("=" * 60)



if __name__ == "__main__":
    main()
