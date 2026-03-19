# Batch Unit - Domain Entities

## Entity: Document

| 필드 | 타입 | 설명 |
|---|---|---|
| doc_id | str | 파일 경로 기반 고유 ID |
| file_path | str | 원본 파일 절대 경로 |
| file_hash | str | SHA-256 해시 (변경 감지용) |
| file_type | str | 파일 확장자 (.txt, .csv, .md) |
| status | str | embedded / deleted / error |
| chunk_count | int | 생성된 청크 수 |
| updated_at | datetime | 마지막 임베딩 시각 |

## Entity: Chunk

| 필드 | 타입 | 설명 |
|---|---|---|
| chunk_id | str | doc_id + chunk_index 조합 |
| doc_id | str | 소속 문서 ID |
| content | str | 청크 텍스트 |
| embedding | list[float] | 임베딩 벡터 |
| chunk_index | int | 문서 내 순서 |
| metadata | dict | 파일명, 페이지 등 메타정보 |

## Entity: KnowledgeEntity

| 필드 | 타입 | 설명 |
|---|---|---|
| entity_id | str | 엔티티 고유 ID |
| name | str | 엔티티명 (용어, 개념, 인물 등) |
| entity_type | str | 유형 (CONCEPT, PERSON, SYSTEM, PROCESS 등) |
| source_doc_id | str | 추출 원본 문서 ID |

## Entity: KnowledgeRelation

| 필드 | 타입 | 설명 |
|---|---|---|
| source_entity | str | 시작 엔티티 ID |
| target_entity | str | 대상 엔티티 ID |
| relation_type | str | 관계 유형 (RELATED_TO, PART_OF, USES 등) |
| source_doc_id | str | 추출 원본 문서 ID |

## Entity: BatchResult

| 필드 | 타입 | 설명 |
|---|---|---|
| run_id | str | 실행 고유 ID |
| mode | str | incremental / full |
| total_files | int | 전체 파일 수 |
| processed | int | 처리된 파일 수 |
| skipped | int | 건너뛴 파일 수 (변경 없음) |
| failed | int | 실패 파일 수 |
| deleted | int | 삭제 처리된 파일 수 |
| started_at | datetime | 시작 시각 |
| finished_at | datetime | 종료 시각 |

## Entity: ChangeSet

| 필드 | 타입 | 설명 |
|---|---|---|
| new_files | list[str] | 신규 파일 목록 |
| modified_files | list[str] | 변경된 파일 목록 |
| deleted_files | list[str] | 삭제된 파일 목록 |
| unchanged_files | list[str] | 변경 없는 파일 목록 |
