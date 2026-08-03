"""
scripts/benchmark.py - Bộ công cụ đánh giá Retrieval Benchmark chuẩn cho Lab 07 (K3 Variant).

Tuân thủ tiêu chí chấm điểm trong docs/SCORING.md và docs/EVALUATION.md:
- 5 câu hỏi đánh giá kèm câu trả lời chuẩn (Gold Answers).
- Có 1 câu hỏi bắt buộc sử dụng metadata_filter={"audience": "student"}.
- Chấm điểm từng câu hỏi theo thang 2.0 điểm:
    * 2.0 điểm: Target chunk/document ở vị trí Top-1 + Similarity score cao.
    * 1.0 điểm: Target chunk/document nằm trong Top-3 (vị trí #2 hoặc #3).
    * 0.0 điểm: Không tìm thấy target document trong Top-3.
"""
from __future__ import annotations

import dataclasses
from typing import Any, Callable, Dict, List, Optional
from src.models import Document
from src.store import EmbeddingStore


@dataclasses.dataclass
class BenchmarkQuery:
    id: int
    query_text: str
    target_doc_id: str
    gold_keywords: List[str]
    metadata_filter: Optional[Dict[str, Any]] = None
    description: str = ""


# Bộ 5 câu hỏi Benchmark chuẩn theo quy định K3 Variant
BENCHMARK_QUERIES: List[BenchmarkQuery] = [
    BenchmarkQuery(
        id=1,
        query_text="Thời hạn và các đợt đăng ký học phần kỳ 1 năm học 2026-2027 diễn ra khi nào?",
        target_doc_id="hust-course-registration-20261",
        gold_keywords=["đợt 1", "đợt 2", "kế hoạch", "20261"],
        description="Đánh giá truy xuất thông tin lịch đăng ký môn học",
    ),
    BenchmarkQuery(
        id=2,
        query_text="Điều kiện và đối tượng được xét trao Học bổng Trần Đại Nghĩa là gì?",
        target_doc_id="hust-tran-dai-nghia-scholarship",
        gold_keywords=["hoàn cảnh khó khăn", "hộ nghèo", "trần đại nghĩa", "học bổng"],
        description="Đánh giá truy xuất chính sách học bổng đặc thù",
    ),
    BenchmarkQuery(
        id=3,
        query_text="Thông báo đăng ký bổ sung học phần môn Toán kỳ 2025.2 yêu cầu sinh viên thực hiện như thế nào?",
        target_doc_id="hust-math-course-supplementary-registration",
        gold_keywords=["môn toán", "bổ sung", "2025.2", "viện toán"],
        description="Đánh giá định vị thông tin môn học cụ thể",
    ),
    BenchmarkQuery(
        id=4,
        query_text="Quy trình xin ký xác nhận các thủ tục hành chính cho sinh viên tại trường như thế nào?",
        target_doc_id="hust-student-administrative-procedures",
        gold_keywords=["thủ tục hành chính", "ký xác nhận", "giấy xác nhận", "dịch vụ một cửa"],
        description="Đánh giá tổng hợp quy trình hành chính",
    ),
    BenchmarkQuery(
        id=5,
        query_text="Các mức học phí và quy định đóng học phí áp dụng cho sinh viên là gì?",
        target_doc_id="hust-tuition-information",
        gold_keywords=["học phí", "tín chỉ", "nộp học phí"],
        metadata_filter={"audience": "student"},
        description="Bắt buộc K3: Đánh giá truy xuất kèm lọc siêu dữ liệu (audience: student)",
    ),
]


@dataclasses.dataclass
class QueryEvaluationResult:
    query_id: int
    query_text: str
    target_doc_id: str
    found_in_top3: bool
    rank: Optional[int]  # 1, 2, 3 or None
    score: float         # 0.0, 1.0, or 2.0
    top1_similarity: float
    filter_passed: bool
    retrieved_results: List[Dict[str, Any]]
    notes: str


@dataclasses.dataclass
class BenchmarkSummary:
    total_score: float         # Max 10.0
    hit_rate_at_1: float       # Percentage (0.0 - 1.0)
    hit_rate_at_3: float       # Percentage (0.0 - 1.0)
    filter_accuracy: float     # Percentage (0.0 - 1.0)
    results: List[QueryEvaluationResult]


def evaluate_store(
    store: EmbeddingStore,
    queries: Optional[List[BenchmarkQuery]] = None,
    top_k: int = 3,
) -> BenchmarkSummary:
    """Chạy đánh giá bộ benchmark trên một EmbeddingStore bất kỳ."""
    eval_queries = queries or BENCHMARK_QUERIES
    eval_results: List[QueryEvaluationResult] = []

    total_score = 0.0
    hits_at_1 = 0
    hits_at_3 = 0
    filter_correct = 0
    filter_total = 0

    for bq in eval_queries:
        if bq.metadata_filter:
            retrieved = store.search_with_filter(
                query=bq.query_text,
                top_k=top_k,
                metadata_filter=bq.metadata_filter,
            )
            filter_total += 1
            # Check if all retrieved docs satisfy the filter
            all_satisfy = all(
                item.get("metadata", {}).get("audience") == bq.metadata_filter.get("audience")
                for item in retrieved
            )
            if all_satisfy:
                filter_correct += 1
            filter_passed = all_satisfy
        else:
            retrieved = store.search(query=bq.query_text, top_k=top_k)
            filter_passed = True

        # Find target rank
        target_rank: Optional[int] = None
        for rank_idx, item in enumerate(retrieved, start=1):
            doc_id = item.get("metadata", {}).get("doc_id")
            if doc_id == bq.target_doc_id:
                target_rank = rank_idx
                break

        top1_sim = 0.0
        if retrieved:
            top1_sim = float(retrieved[0].get("score", 0.0))

        # Scoring logic according to docs/SCORING.md (2.0 max per query)
        score = 0.0
        found_top3 = target_rank is not None and target_rank <= 3
        if target_rank == 1:
            score = 2.0
            hits_at_1 += 1
            hits_at_3 += 1
        elif found_top3:
            score = 1.0
            hits_at_3 += 1
        else:
            score = 0.0

        total_score += score

        note = ""
        if target_rank == 1:
            note = f"PASSED (Top-1, Score: {top1_sim:.4f})"
        elif found_top3:
            note = f"ACCEPTABLE (Rank #{target_rank}, Score: {top1_sim:.4f})"
        else:
            note = f"FAILED (Target doc '{bq.target_doc_id}' not in Top-3)"

        eval_results.append(
            QueryEvaluationResult(
                query_id=bq.id,
                query_text=bq.query_text,
                target_doc_id=bq.target_doc_id,
                found_in_top3=found_top3,
                rank=target_rank,
                score=score,
                top1_similarity=top1_sim,
                filter_passed=filter_passed,
                retrieved_results=retrieved,
                notes=note,
            )
        )

    num_queries = len(eval_queries)
    return BenchmarkSummary(
        total_score=total_score,
        hit_rate_at_1=hits_at_1 / num_queries if num_queries > 0 else 0.0,
        hit_rate_at_3=hits_at_3 / num_queries if num_queries > 0 else 0.0,
        filter_accuracy=filter_correct / filter_total if filter_total > 0 else 1.0,
        results=eval_results,
    )


def generate_markdown_report(summary: BenchmarkSummary, store_name: str = "Store") -> str:
    """Tạo báo cáo kết quả đánh giá theo định dạng Markdown chi tiết."""
    lines = [
        f"# Báo Cáo Đánh Giá Benchmark Retrieval - {store_name}",
        "",
        "## 1. Tóm Tắt Chỉ Số (Aggregate Metrics)",
        f"- **Tổng điểm (Total Score)**: **{summary.total_score:.1f} / 10.0**",
        f"- **Hit Rate @ 1 (Top-1 Accuracy)**: {summary.hit_rate_at_1 * 100:.1f}%",
        f"- **Hit Rate @ 3 (Top-3 Accuracy)**: {summary.hit_rate_at_3 * 100:.1f}%",
        f"- **Độ chính xác Lọc Metadata (Filter Accuracy)**: {summary.filter_accuracy * 100:.1f}%",
        "",
        "## 2. Kết Quả Chi Tiết Cho 5 Câu Hỏi",
        "| # | Câu Hỏi (Query) | Target Doc ID | Rank | Similarity | Điểm (Score) | Trạng Thái |",
        "|---|---|---|---|---|---|---|",
    ]

    for res in summary.results:
        rank_str = f"#{res.rank}" if res.rank else "N/A"
        lines.append(
            f"| {res.query_id} | {res.query_text} | `{res.target_doc_id}` | {rank_str} | {res.top1_similarity:.4f} | {res.score:.1f}/2.0 | {res.notes} |"
        )

    lines.append("")
    lines.append("## 3. Chi Tiết Chunks Đã Truy Xuất (Top-1 Context Snippets)")
    for res in summary.results:
        lines.append(f"### Câu hỏi #{res.query_id}: *\"{res.query_text}\"*")
        lines.append(f"- **Target Document**: `{res.target_doc_id}` | **Filter**: `{'Pass' if res.filter_passed else 'Fail'}`")
        if res.retrieved_results:
            top_item = res.retrieved_results[0]
            content = top_item.get("content", "")
            chunk_id = top_item.get("metadata", {}).get("doc_id", "N/A")
            snippet = content[:200].replace("\n", " ") + "..."
            lines.append(f"- **Top-1 Doc ID**: `{chunk_id}`")
            lines.append(f"- **Nội dung trích đoạn**: *\"{snippet}\"*")
        else:
            lines.append("- **Không tìm thấy chunk nào.**")
        lines.append("")

    return "\n".join(lines)



if __name__ == "__main__":
    print("Benchmark Module for Lab 07 (K3 Variant) initialized.")
