# 태스크: 다중 상점 가격 크롤러 (Multi-Shop Price Crawler)

**Input**: 설계 문서 `/specs/001-shop-price-crawler/`  
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**테스트 정책**: 헌법 I항에 따라 테스트 우선 개발(TDD) 적용 - 모든 구현 전 테스트 작성 필수

**조직**: 사용자 스토리별로 태스크 그룹화 (독립 구현/테스트 가능)

## 형식: `[ID] [P?] [Story?] 설명`

- **[P]**: 병렬 실행 가능 (다른 파일, 의존성 없음)
- **[Story]**: 해당 사용자 스토리 (US1, US2, US3)
- 모든 태스크에 정확한 파일 경로 포함

---

## Phase 1: 초기 설정 (Setup)

**목적**: 프로젝트 초기화 및 기본 구조 생성

- [x] T001 프로젝트 디렉토리 구조 생성 (src/, tests/ 하위 폴더)
- [x] T002 Python 가상환경 설정 및 requirements.txt 생성
- [x] T003 [P] requirements-dev.txt 생성 (pytest, pytest-mock, responses)
- [x] T004 [P] pyproject.toml 또는 setup.py 설정 (plaprice 패키지)
- [x] T005 [P] .gitignore 설정

---

## Phase 2: 기초 (Foundational) - 블로킹 전제조건

**목적**: 모든 사용자 스토리 구현 전에 완료해야 하는 핵심 인프라

**⚠️ 중요**: 이 Phase가 완료되어야 사용자 스토리 작업 시작 가능

### 테스트 (먼저 작성, 실패 확인)

- [x] T006 [P] tests/unit/test_models.py - Shop 모델 테스트 작성
- [x] T007 [P] tests/unit/test_models.py - SearchResult 모델 테스트 작성
- [x] T008 [P] tests/unit/test_models.py - SearchQuery 모델 테스트 작성
- [x] T009 [P] tests/unit/test_http_client.py - HTTP 클라이언트 테스트 작성

### 구현 (테스트 통과시키기)

- [x] T010 [P] src/models/__init__.py 생성
- [x] T011 src/models/shop.py - Shop, ShopSelectors, StockPatterns 모델 구현
- [x] T012 src/models/search.py - SearchResult, SearchQuery, StockStatus 모델 구현
- [x] T013 [P] src/utils/__init__.py 생성
- [x] T014 src/utils/http_client.py - requests 기반 HTTP 클라이언트 구현

**체크포인트**: 기초 모델 및 유틸리티 준비 완료

---

## Phase 3: 사용자 스토리 1 - 단일 상점 가격 조회 (Priority: P1) 🎯 MVP

**목표**: 하나의 상점에서 키워드 검색 후 결과를 표 형태로 출력

**독립 테스트**: 단일 상점 URL + 키워드 입력 → 상품 정보 테이블 출력

### 테스트 (먼저 작성, 실패 확인)

- [x] T015 [P] [US1] tests/unit/test_crawlers.py - BaseCrawler 테스트 작성
- [x] T016 [P] [US1] tests/unit/test_crawlers.py - HtmlCrawler 테스트 작성
- [x] T017 [P] [US1] tests/unit/test_display.py - TableRenderer 테스트 작성
- [x] T018 [P] [US1] tests/fixtures/sample_html/ - 테스트용 HTML 샘플 생성
- [ ] T019 [US1] tests/integration/test_single_shop_search.py - 단일 상점 검색 통합 테스트 작성

### 구현 (테스트 통과시키기)

- [x] T020 [P] [US1] src/crawlers/__init__.py 생성
- [x] T021 [US1] src/crawlers/base.py - BaseCrawler 추상 클래스 구현
- [x] T022 [US1] src/crawlers/html_crawler.py - HtmlCrawler 구현 (BeautifulSoup 기반)
- [x] T023 [P] [US1] src/display/__init__.py 생성
- [x] T024 [US1] src/display/table_renderer.py - rich 테이블 렌더러 구현
- [x] T025 [US1] src/crawlers/html_crawler.py - 가격 파싱 로직 추가 (통화 기호 처리)
- [x] T026 [US1] src/crawlers/html_crawler.py - 재고 상태 판별 로직 추가
- [x] T027 [US1] src/crawlers/html_crawler.py - 에러 처리 (타임아웃, HTTP 오류, 파싱 실패)

**체크포인트**: US1 완료 - 단일 상점 크롤링 및 결과 표시 가능

---

## Phase 4: 사용자 스토리 2 - 다중 상점 설정 및 관리 (Priority: P2)

**목표**: 상점 추가/삭제/조회 및 영구 저장

**독립 테스트**: 상점 추가 → 프로그램 재시작 → 상점 목록 유지 확인

### 테스트 (먼저 작성, 실패 확인)

- [x] T028 [P] [US2] tests/unit/test_storage.py - ShopStore 테스트 작성
- [x] T029 [P] [US2] tests/fixtures/sample_shop.json - 테스트용 상점 JSON 생성
- [ ] T030 [US2] tests/integration/test_shop_management.py - 상점 관리 통합 테스트 작성

### 구현 (테스트 통과시키기)

- [x] T031 [P] [US2] src/storage/__init__.py 생성
- [x] T032 [US2] src/storage/shop_store.py - ShopStore 클래스 구현 (CRUD 기능)
- [x] T033 [US2] src/storage/shop_store.py - JSON 파일 저장/로드 구현
- [x] T034 [US2] src/storage/shop_store.py - 설정 디렉토리 자동 생성 (~/.plaprice/)
- [x] T035 [US2] src/storage/shop_store.py - 상점 유효성 검사 (URL, 선택자)

**체크포인트**: US2 완료 - 상점 영구 저장 및 관리 가능

---

## Phase 5: 사용자 스토리 3 - 다중 상점 동시 검색 및 비교 (Priority: P3)

**목표**: 모든 활성 상점에서 동시 검색 후 비교 표 출력

**독립 테스트**: 3개 상점 등록 → 키워드 검색 → 통합 비교 표 출력

### 테스트 (먼저 작성, 실패 확인)

- [x] T036 [P] [US3] tests/unit/test_multi_crawler.py - 다중 상점 크롤러 테스트 작성
- [x] T037 [P] [US3] tests/unit/test_display.py - 비교 테이블 렌더러 테스트 추가
- [ ] T038 [US3] tests/integration/test_multi_shop_search.py - 다중 상점 검색 통합 테스트 작성

### 구현 (테스트 통과시키기)

- [x] T039 [US3] src/crawlers/multi_crawler.py - MultiShopCrawler 구현 (순차 크롤링)
- [x] T040 [US3] src/crawlers/multi_crawler.py - 부분 실패 처리 (일부 상점 오류 시 계속 진행)
- [x] T041 [US3] src/display/table_renderer.py - 다중 상점 비교 테이블 렌더링 추가
- [x] T042 [US3] src/display/table_renderer.py - 가격 정렬 및 최저가 하이라이트

**체크포인트**: US3 완료 - 다중 상점 비교 검색 가능

---

## Phase 6: CLI 인터페이스

**목적**: 사용자 인터페이스 통합

### 테스트 (먼저 작성, 실패 확인)

- [x] T043 [P] tests/unit/test_cli.py - CLI 명령어 파싱 테스트 작성
- [ ] T044 tests/integration/test_cli.py - CLI 전체 플로우 통합 테스트 작성

### 구현 (테스트 통과시키기)

- [x] T045 [P] src/cli/__init__.py 생성
- [x] T046 src/cli/main.py - CLI 엔트리포인트 및 argparse 설정
- [x] T047 src/cli/main.py - `search` 명령어 구현
- [x] T048 src/cli/main.py - `shop list` 명령어 구현
- [x] T049 src/cli/main.py - `shop add` 명령어 구현
- [x] T050 src/cli/main.py - `shop remove` 명령어 구현
- [x] T051 src/cli/main.py - `shop show` 명령어 구현
- [x] T052 src/cli/main.py - `config init` / `config path` 명령어 구현
- [x] T053 src/cli/main.py - `test` 명령어 구현 (상점 설정 테스트)
- [x] T054 src/cli/main.py - 전역 옵션 처리 (--json, --quiet, --help)
- [x] T055 src/__main__.py - `python -m plaprice` 지원

**체크포인트**: CLI 완료 - 모든 명령어 사용 가능

---

## Phase 7: 마무리 및 품질 (Polish)

**목적**: 문서화, 에러 처리 강화, 최종 검증

- [x] T056 [P] README.md 작성 (설치, 사용법, 예제)
- [x] T057 [P] src/cli/main.py - 에러 메시지 한국어화 및 사용자 친화적 포맷
- [x] T058 [P] 모든 모듈에 한국어 docstring 추가
- [x] T059 전체 테스트 실행 및 커버리지 확인 (pytest --cov)
- [ ] T060 타입 힌트 검증 (mypy 선택적)

---

## 의존성 그래프

```
Phase 1 (Setup)
    │
    ▼
Phase 2 (Foundational)
    │
    ├──────────────────────────────────┐
    ▼                                  │
Phase 3 (US1: 단일 상점)               │
    │                                  │
    ▼                                  │
Phase 4 (US2: 상점 관리) ◄─────────────┘
    │
    ▼
Phase 5 (US3: 다중 상점 비교)
    │
    ▼
Phase 6 (CLI 통합)
    │
    ▼
Phase 7 (마무리)
```

## 병렬 실행 가능 태스크

### Phase 2 병렬 그룹
- T006, T007, T008, T009 (테스트 작성)
- T010, T013 (__init__.py 생성)

### Phase 3 병렬 그룹
- T015, T016, T017, T018 (US1 테스트 작성)
- T020, T023 (__init__.py 생성)

### Phase 4 병렬 그룹
- T028, T029 (US2 테스트 작성)

### Phase 5 병렬 그룹
- T036, T037 (US3 테스트 작성)

### Phase 7 병렬 그룹
- T056, T057, T058 (문서화 및 폴리싱)

---

## 구현 전략

### MVP 범위 (권장 첫 배포)
- Phase 1~3 완료 (US1: 단일 상점 가격 조회)
- CLI `search` 명령어만 구현

### 증분 배포
1. **v0.1.0**: US1 완료 (단일 상점 CLI 검색)
2. **v0.2.0**: US2 완료 (상점 영구 저장)
3. **v0.3.0**: US3 완료 (다중 상점 비교)
4. **v1.0.0**: 전체 CLI 및 문서화 완료

---

## 요약

| 항목 | 수량 |
|------|------|
| 총 태스크 | 60개 |
| Phase 1 (Setup) | 5개 |
| Phase 2 (Foundational) | 9개 |
| Phase 3 (US1) | 13개 |
| Phase 4 (US2) | 8개 |
| Phase 5 (US3) | 7개 |
| Phase 6 (CLI) | 13개 |
| Phase 7 (Polish) | 5개 |
| 병렬 가능 태스크 | 27개 ([P] 표시) |
