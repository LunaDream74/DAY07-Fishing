"""Benchmark SentenceChunker của Nguyễn Hữu Thắng trên corpus HUST dùng chung.

Thí nghiệm này giữ nguyên corpus, bộ năm query và mô hình embedding của nhóm.
Biến strategy duy nhất là cấu hình ``SentenceChunker`` bên dưới.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Bảo đảm PowerShell/Windows console in được nội dung tiếng Việt.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from ingest import build_knowledge_base, parse_front_matter
from scripts.benchmark import BENCHMARK_QUERIES
from src import ChunkingStrategyComparator, SentenceChunker
from src.embeddings import LocalEmbedder, MockEmbedder

EXPERIMENT_DIR = Path(__file__).resolve().parent
CORPUS_DIR = PROJECT_ROOT / "data" / "hust_services"
RESULTS_DIR = EXPERIMENT_DIR / "results"

# DÒNG STRATEGY DUY NHẤT KHÁC VỚI CÁC THÀNH VIÊN KHÁC.
CHUNKER = SentenceChunker(max_sentences_per_chunk=2)

BASELINE_DOCUMENTS = (
    "hust-course-registration-20261.md",
    "hust-student-administrative-procedures.md",
    "hust-tran-dai-nghia-scholarship.md",
)


@dataclass(frozen=True)
class EvidenceSpec:
    """Gold answer và các chuỗi bắt buộc phải có trong context trả lời đúng."""

    gold_answer: str
    required_phrases: tuple[str, ...]
    coherence_note: str
    failure_cause: str
    proposed_fix: str


EVIDENCE_SPECS = {
    1: EvidenceSpec(
        gold_answer=(
            "Ba đợt lần lượt là đăng ký chính thức 22/07–03/08/2026, điều chỉnh "
            "03/08–15/08/2026 và đăng ký thêm 15/08–22/08/2026."
        ),
        required_phrases=(
            "Đăng ký chính thức: từ 16:00 ngày 22/07/2026",
            "Đăng ký điều chỉnh: từ 16:00 ngày 03/08/2026",
            "Đăng ký thêm: từ 16:00 ngày 15/08/2026",
        ),
        coherence_note=(
            "Hai đợt đầu nằm cùng chunk, đợt đăng ký thêm nằm ở chunk kế tiếp; "
            "top-3 vẫn ghép đủ lịch nhưng thông tin không còn trong một chunk duy nhất."
        ),
        failure_cause="Không phải failure: top-1 và top-2 bổ sung cho nhau, đủ ba đợt.",
        proposed_fix="Nếu cần một chunk tự đủ nghĩa, tăng lên 3 câu/chunk cho riêng section lịch.",
    ),
    2: EvidenceSpec(
        gold_answer=(
            "Đối tượng gồm sinh viên năm nhất nổi bật; sinh viên khóa khác học đúng "
            "tiến độ, đủ tín chỉ, CPA từ 2,0 và điểm rèn luyện từ 65; hoặc sinh viên "
            "gặp rủi ro, tai nạn, bệnh hiểm nghèo hay thiên tai."
        ),
        required_phrases=(
            "sinh viên năm nhất có thành tích tuyển sinh nổi bật",
            "CPA từ 2,0 và điểm rèn luyện tích lũy từ 65",
            "rủi ro, tai nạn, bệnh hiểm nghèo",
        ),
        coherence_note=(
            "Chunk gold giữ trọn các nhóm điều kiện, nhưng ba kết quả đầu đều đến từ "
            "trang học bổng tổng quan và chỉ nói cùng chủ đề."
        ),
        failure_cause=(
            "Cosine ưu tiên các chunk lặp nhiều từ 'học bổng' và tên chương trình; "
            "score cao phản ánh giống chủ đề, không phản ánh có đủ điều kiện xét."
        ),
        proposed_fix=(
            "Gắn lại tiêu đề tài liệu/heading vào mọi chunk hoặc thêm overlap một câu "
            "để chunk điều kiện luôn mang tên Học bổng Trần Đại Nghĩa."
        ),
    ),
    3: EvidenceSpec(
        gold_answer=(
            "Sinh viên thao tác trên QLDT và điền mẫu 'Đơn xin đăng ký vào lớp đầy'; "
            "thời gian tiếp nhận từ 00:01 ngày 05/02/2026 đến 23:59 ngày 11/02/2026."
        ),
        required_phrases=(
            "Đơn xin đăng ký vào lớp đầy",
            "00:01 ngày 05/02/2026",
            "23:59 ngày 11/02/2026",
        ),
        coherence_note=(
            "Chunk gold rất mạch lạc và chứa cả thao tác lẫn thời hạn, nhưng đứng ngoài top-3."
        ),
        failure_cause=(
            "Các chunk hành chính/đăng ký chung thắng nhờ từ vựng gần query; chunk có "
            "tên biểu mẫu và ngày cụ thể chỉ đứng hạng 4."
        ),
        proposed_fix=(
            "Gắn title vào chunk, tăng top_k khi câu hỏi chứa học kỳ cụ thể, hoặc dùng "
            "metadata document_version/category để thu hẹp ứng viên trước khi xếp hạng."
        ),
    ),
    4: EvidenceSpec(
        gold_answer=(
            "Ví dụ với giấy vay vốn, sinh viên tự in biểu mẫu, nộp lớp trưởng để tổng "
            "hợp; giấy chứng nhận tạm thời cần ảnh 3x4 và quy trình xác nhận, ký, đóng dấu."
        ),
        required_phrases=(
            "sinh viên tự in biểu mẫu",
            "lớp trưởng tổng hợp",
            "ảnh 3x4",
        ),
        coherence_note=(
            "Chunk hạng 3 giữ trọn điều kiện và các bước của hai thủ tục; chunk hạng 1 "
            "chỉ là phần giới thiệu/lịch nhận trả nên chưa tự trả lời được."
        ),
        failure_cause=(
            "Partial failure: đúng doc_id ở top-1 nhưng chunk chứa quy trình thật ở hạng 3."
        ),
        proposed_fix="Gắn heading 'Một số quy trình' vào từng chunk con và cân nhắc overlap một câu.",
    ),
    5: EvidenceSpec(
        gold_answer=(
            "Corpus không nêu con số học phí cụ thể; sinh viên phải xem đúng tài liệu "
            "theo năm học và chương trình đào tạo để tra mức áp dụng."
        ),
        required_phrases=(
            "mức học phí theo từng chương trình đào tạo",
            "xem đúng tài liệu của năm học",
        ),
        coherence_note="Top-1 là một chunk tự đủ nghĩa và nêu đúng giới hạn của corpus.",
        failure_cause="Không phải failure: top-1 chứa đủ bằng chứng và không suy diễn mức tiền.",
        proposed_fix="Không cần đổi chunking; cần giữ câu trả lời trung thực rằng corpus thiếu con số.",
    ),
}


def get_embedder():
    """Chọn backend tường minh; không âm thầm fallback làm sai ý nghĩa kết quả."""
    provider = os.getenv("EMBEDDING_PROVIDER", "local").lower()
    if provider == "mock":
        print(
            "[CẢNH BÁO] Đang dùng MockEmbedder: chỉ kiểm tra pipeline, "
            "không dùng điểm này để kết luận chất lượng retrieval."
        )
        return MockEmbedder()
    if provider == "local":
        os.environ.setdefault("HF_HOME", str(EXPERIMENT_DIR / ".venv" / ".hf-cache"))
        os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
        os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")
        os.environ.setdefault("HF_HUB_OFFLINE", "1")
        os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
        try:
            return LocalEmbedder()
        except ModuleNotFoundError as error:
            raise RuntimeError(
                "Chế độ local cần sentence-transformers. Hoặc cài "
                "requirements-local.txt, hoặc đặt EMBEDDING_PROVIDER=mock "
                "để chạy smoke test không cần tải model."
            ) from error
    raise ValueError("EMBEDDING_PROVIDER chỉ nhận 'local' hoặc 'mock'.")


def run_baseline() -> list[dict]:
    """So sánh ba built-in strategy trên body của ba tài liệu đại diện."""
    rows: list[dict] = []
    comparator = ChunkingStrategyComparator()

    for filename in BASELINE_DOCUMENTS:
        raw_text = (CORPUS_DIR / filename).read_text(encoding="utf-8")
        _, body = parse_front_matter(raw_text)
        if body.startswith("---"):
            raise ValueError(f"Front matter chưa được loại bỏ khỏi {filename}")

        comparison = comparator.compare(body, chunk_size=200)
        for strategy, metrics in comparison.items():
            rows.append(
                {
                    "document": filename.removesuffix(".md"),
                    "strategy": strategy,
                    "count": metrics["count"],
                    "avg_length": metrics["avg_length"],
                }
            )
    return rows


def extractive_llm(prompt: str) -> str:
    """Offline LLM stand-in: trả lại ngữ cảnh truy xuất để kiểm tra grounding."""
    marker = "Context:\n"
    question_marker = "\n\nQuestion:"
    if marker not in prompt:
        return "Không có ngữ cảnh để trả lời."
    context = prompt.split(marker, 1)[1].split(question_marker, 1)[0].strip()
    compact = " ".join(context.split())
    return compact[:700] if compact else "Không có ngữ cảnh để trả lời."


def preview(text: str, limit: int = 180) -> str:
    compact = " ".join(text.split())
    return compact if len(compact) <= limit else compact[: limit - 3] + "..."


def render_report(embedder_name: str, store, summary, baseline_rows: list[dict]) -> str:
    lines = [
        "# Kết quả thí nghiệm SentenceChunker — Nguyễn Hữu Thắng",
        "",
        "## Cấu hình cố định",
        "",
        f"- Corpus: `{CORPUS_DIR.relative_to(PROJECT_ROOT).as_posix()}` (10 tài liệu)",
        f"- Strategy: `SentenceChunker(max_sentences_per_chunk={CHUNKER.max_sentences_per_chunk})`",
        f"- Embedder: `{embedder_name}`",
        f"- Số chunk đã nạp: **{store.get_collection_size()}**",
        "- Queries: `scripts.benchmark.BENCHMARK_QUERIES` (5 query chung)",
        "- Metadata overrides: không có; giữ nguyên metadata của corpus",
        "",
        "## Baseline (đã bỏ YAML front matter)",
        "",
        "`ChunkingStrategyComparator.compare(body, chunk_size=200)`",
        "",
        "| Tài liệu | Strategy | Số chunk | Độ dài trung bình |",
        "|---|---|---:|---:|",
    ]
    for row in baseline_rows:
        lines.append(
            f"| `{row['document']}` | `{row['strategy']}` | "
            f"{row['count']} | {row['avg_length']:.1f} |"
        )

    lines.extend(
        [
            "",
            "## Kết quả retrieval",
            "",
            f"- Điểm: **{summary.total_score:.1f}/10.0**",
            f"- Hit@1: **{summary.hit_rate_at_1 * 100:.1f}%**",
            f"- Hit@3: **{summary.hit_rate_at_3 * 100:.1f}%**",
            f"- Filter accuracy: **{summary.filter_accuracy * 100:.1f}%**",
            "",
        ]
    )

    agent = KnowledgeBaseAgent(store=store, llm_fn=extractive_llm)
    for query, result in zip(BENCHMARK_QUERIES, summary.results):
        filter_text = str(query.metadata_filter) if query.metadata_filter else "None"
        lines.extend(
            [
                f"### Query {query.id}",
                "",
                f"- Câu hỏi: {query.query_text}",
                f"- Target: `{query.target_doc_id}`",
                f"- Filter: `{filter_text}`",
                f"- Target rank: `{result.rank or 'N/A'}`; điểm: `{result.score:.1f}/2.0`",
                "",
                "| Rank | Score | doc_id | Preview |",
                "|---:|---:|---|---|",
            ]
        )
        for rank, item in enumerate(result.retrieved_results, start=1):
            metadata = item.get("metadata", {})
            lines.append(
                f"| {rank} | {float(item.get('score', 0.0)):.4f} | "
                f"`{metadata.get('doc_id', 'N/A')}` | {preview(item.get('content', ''))} |"
            )
        lines.extend(
            [
                "",
                "Câu trả lời của agent trích xuất (offline, dùng top-3 làm grounding):",
                "",
                f"> {agent.answer(query.query_text, top_k=3)}",
                "",
            ]
        )

    return "\n".join(lines)


def main() -> int:
    baseline_rows = run_baseline()
    embedder = get_embedder()
    store = build_knowledge_base(
        CORPUS_DIR,
        embedder,
        chunker=CHUNKER,
        collection_name="hust_sentence_nguyen_huu_thang",
    )
    summary = evaluate_store(store, queries=BENCHMARK_QUERIES, top_k=3)

    report = render_report(embedder._backend_name, store, summary, baseline_rows)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    output_path = RESULTS_DIR / "sentence_benchmark.md"
    output_path.write_text(report + "\n", encoding="utf-8")
    print(report)
    print(f"\nĐã lưu kết quả tại: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
