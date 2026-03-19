"""Batch 임베딩 실행 스크립트.

실행 모드:
- incremental (기본): SHA-256 해시 비교로 변경된 문서만 처리
- full (--full): 모든 DB를 초기화하고 전체 문서를 재임베딩
"""

import argparse
import logging
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table

sys.path.insert(0, str(Path(__file__).parent.parent))

from batch.embedding import (
    chunk_texts,
    compute_file_hash,
    detect_changes,
    extract_entities,
    parse_document,
    scan_documents,
)
from shared.config import DOCUMENTS_DIR
from shared.db import ChromaRepository, KuzuRepository, SQLiteRepository
from shared.embeddings import embed_texts

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)
console = Console()


def process_document(doc_id: str, file_path: str, file_hash: str, chroma: ChromaRepository, kuzu: KuzuRepository, sqlite: SQLiteRepository) -> bool:
    """단일 문서의 임베딩 파이프라인: 파싱 → 청킹 → 벡터 임베딩 → 엔티티 추출 → 저장."""
    try:
        ext = Path(file_path).suffix.lower()

        texts = parse_document(file_path)
        if not texts:
            return False

        chunks = chunk_texts(texts)
        if not chunks:
            logger.warning(f"청크 생성 실패: {doc_id}")
            return False

        # 기존 데이터를 먼저 삭제하여 upsert 시 고아 청크가 남지 않도록 한다
        chroma.delete_by_doc(doc_id)
        kuzu.delete_by_doc(doc_id)

        embeddings = embed_texts(chunks)
        chunk_ids = [f"{doc_id}##{i}" for i in range(len(chunks))]
        metadatas = [{"doc_id": doc_id, "chunk_index": i, "file_name": Path(file_path).name} for i in range(len(chunks))]
        chroma.upsert(doc_id, chunk_ids, chunks, embeddings, metadatas)

        # 상위 5개 청크만 엔티티 추출 (LLM API 비용 절감)
        all_entities, all_relations = [], []
        for chunk in chunks[:5]:
            result = extract_entities(chunk)
            all_entities.extend([e.model_dump() for e in result.entities])
            all_relations.extend([r.model_dump() for r in result.relations])

        if all_entities:
            kuzu.upsert_entities(doc_id, all_entities, all_relations)

        sqlite.save_doc_meta(doc_id, file_path, file_hash, ext, "embedded", len(chunks))
        return True

    except Exception as e:
        logger.error(f"문서 처리 실패 ({doc_id}): {e}")
        sqlite.save_doc_meta(doc_id, file_path, file_hash, Path(file_path).suffix.lower(), "error", 0)
        return False


def run(full: bool = False):
    """메인 실행."""
    run_id = str(uuid.uuid4())[:8]
    started_at = datetime.now(timezone.utc).isoformat()
    mode = "full" if full else "incremental"

    console.print(f"\n[bold blue]NH-RAG Batch Embedding[/bold blue] (mode: {mode})\n")

    chroma = ChromaRepository()
    kuzu = KuzuRepository()
    sqlite = SQLiteRepository()

    try:
        if full:
            console.print("[yellow]전체 재임베딩: 기존 데이터 초기화 중...[/yellow]")
            chroma.reset()
            kuzu.reset()
            sqlite.reset()
            current_files = scan_documents(DOCUMENTS_DIR)
            targets = [(doc_id, fpath, compute_file_hash(fpath)) for doc_id, fpath in current_files.items()]
            deleted = []
            skipped = 0
        else:
            # 증분 모드: 기존 해시와 비교하여 변경분만 처리
            existing_hashes = sqlite.get_all_doc_hashes()
            changes = detect_changes(DOCUMENTS_DIR, existing_hashes)
            targets = changes["new"] + changes["modified"]
            deleted = changes["deleted"]
            skipped = len(changes["unchanged"])

        total = len(targets)
        processed, failed = 0, 0

        if not targets and not deleted:
            console.print("[green]변경된 문서 없음.[/green]")
        else:
            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), BarColumn(), TaskProgressColumn(), console=console) as progress:
                task = progress.add_task("임베딩 처리 중...", total=len(targets))
                for doc_id, fpath, fhash in targets:
                    success = process_document(doc_id, fpath, fhash, chroma, kuzu, sqlite)
                    if success:
                        processed += 1
                    else:
                        failed += 1
                    progress.advance(task)

            # 디렉토리에서 삭제된 문서의 데이터를 3개 DB에서 모두 제거
            for doc_id in deleted:
                chroma.delete_by_doc(doc_id)
                kuzu.delete_by_doc(doc_id)
                sqlite.delete_doc_meta(doc_id)

        table = Table(title="실행 결과")
        table.add_column("항목", style="cyan")
        table.add_column("값", style="green")
        table.add_row("모드", mode)
        table.add_row("전체 파일", str(total + skipped + len(deleted)))
        table.add_row("처리 완료", str(processed))
        table.add_row("건너뜀 (변경 없음)", str(skipped))
        table.add_row("실패", str(failed))
        table.add_row("삭제", str(len(deleted)))
        console.print(table)

        sqlite.save_batch_log(run_id, mode, total + skipped + len(deleted), processed, skipped, failed, len(deleted), started_at)

    finally:
        kuzu.close()
        sqlite.close()


def main():
    parser = argparse.ArgumentParser(description="NH-RAG 문서 임베딩 배치")
    parser.add_argument("--full", action="store_true", help="전체 재임베딩 (기존 데이터 초기화)")
    args = parser.parse_args()
    run(full=args.full)


if __name__ == "__main__":
    main()
