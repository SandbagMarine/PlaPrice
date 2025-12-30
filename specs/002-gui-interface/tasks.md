# Tasks: GUI 인터페이스

**Input**: Design documents from `/specs/002-gui-interface/`  
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Tests**: 이 기능은 TDD(테스트 우선 개발) 원칙을 따름. 각 컴포넌트 구현 전 테스트 작성.

**Organization**: User Story 기준으로 구성. 각 스토리는 독립적으로 구현/테스트 가능.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: 병렬 실행 가능 (다른 파일, 의존성 없음)
- **[Story]**: 해당 User Story (US1, US2, US3)
- 정확한 파일 경로 포함

---

## Phase 1: Setup (프로젝트 설정)

**Purpose**: GUI 모듈 초기화 및 의존성 설치

- [X] T001 PySide6, pytest-qt 의존성 추가 in requirements.txt, requirements-dev.txt
- [X] T002 [P] GUI 디렉토리 구조 생성 in src/gui/__init__.py
- [X] T003 [P] GUI 테스트 디렉토리 생성 in tests/unit/gui/__init__.py
- [X] T004 [P] GUI 통합 테스트 디렉토리 생성 in tests/integration/gui/__init__.py

---

## Phase 2: Foundational (기초 인프라)

**Purpose**: 모든 User Story가 의존하는 핵심 컴포넌트

**⚠️ CRITICAL**: 이 단계 완료 전 User Story 작업 불가

### 테스트 (TDD)

- [X] T005 [P] GuiSettings 테스트 작성 in tests/unit/gui/test_settings.py
- [X] T006 [P] MainWindow 기본 테스트 작성 in tests/unit/gui/test_main_window.py

### 구현

- [X] T007 GuiSettings 모델 구현 in src/gui/settings.py (T005 테스트 통과)
- [X] T008 MainWindow 기본 레이아웃 구현 in src/gui/main_window.py (T006 테스트 통과)
- [X] T009 앱 진입점 구현 in src/gui/app.py
- [X] T010 __main__.py에 --gui 옵션 추가 in src/__main__.py

**Checkpoint**: `python -m src --gui` 실행 시 빈 메인 윈도우 표시

---

## Phase 3: User Story 1 - 상점 목록 관리 (Priority: P1) 🎯 MVP

**Goal**: GUI에서 상점 추가/수정/삭제, 체크박스로 검색 대상 선택

**Independent Test**: 상점 CRUD만으로 독립적 가치 제공

### 테스트 (TDD)

- [X] T011 [P] [US1] ShopListView 테스트 작성 in tests/unit/gui/test_shop_panel.py
- [X] T012 [P] [US1] ShopEditDialog 테스트 작성 in tests/unit/gui/test_shop_dialog.py

### 구현

- [X] T013 [US1] ShopListView 기본 구조 구현 in src/gui/shop_panel.py (테이블, 체크박스)
- [X] T014 [US1] ShopListView 버튼 및 시그널 구현 in src/gui/shop_panel.py (추가/수정/삭제/전체선택)
- [X] T015 [US1] ShopEditDialog 폼 구현 in src/gui/shop_dialog.py (입력 필드, 검증)
- [X] T016 [US1] ShopEditDialog CRUD 로직 구현 in src/gui/shop_dialog.py (ShopStore 연동)
- [X] T017 [US1] MainWindow에 ShopListView 통합 in src/gui/main_window.py (사이드바 배치)

**Checkpoint**: GUI에서 상점 추가/수정/삭제 가능, 체크박스로 선택 가능

---

## Phase 4: User Story 2 - 검색 실행 및 결과 표시 (Priority: P2)

**Goal**: 키워드 검색, 결과 테이블, 최저가 강조, 진행률 표시

**Independent Test**: 등록된 상점에 검색 수행, 결과 확인

### 테스트 (TDD)

- [X] T018 [P] [US2] SearchPanel 테스트 작성 in tests/unit/gui/test_search_panel.py
- [X] T019 [P] [US2] ResultsTable 테스트 작성 in tests/unit/gui/test_results_table.py
- [X] T020 [P] [US2] SearchWorker 테스트 작성 in tests/unit/gui/test_worker.py

### 구현

- [X] T021 [US2] SearchWorker 구현 in src/gui/worker.py (QThread, 시그널, 취소)
- [X] T022 [US2] SearchPanel 기본 구조 구현 in src/gui/search_panel.py (입력, 버튼, 진행률)
- [X] T023 [US2] SearchPanel 검색 로직 구현 in src/gui/search_panel.py (워커 연동)
- [X] T024 [US2] ResultsTable 기본 구조 구현 in src/gui/results_table.py (테이블, 컬럼)
- [X] T025 [US2] ResultsTable 최저가 강조 구현 in src/gui/results_table.py (녹색 배경)
- [X] T026 [US2] ResultsTable 더블클릭 URL 열기 in src/gui/results_table.py (webbrowser)
- [X] T027 [US2] MainWindow에 SearchPanel, ResultsTable 통합 in src/gui/main_window.py

**Checkpoint**: 검색 실행, 결과 표시, 최저가 강조, 진행률 바 동작

---

## Phase 5: User Story 3 - 검색 결과 내보내기 (Priority: P3)

**Goal**: CSV 파일 저장, 클립보드 복사

**Independent Test**: 결과가 있는 상태에서 내보내기 기능 테스트

### 테스트 (TDD)

- [X] T028 [P] [US3] CSV 내보내기 테스트 추가 in tests/unit/gui/test_results_table.py
- [X] T029 [P] [US3] 클립보드 복사 테스트 추가 in tests/unit/gui/test_results_table.py

### 구현

- [X] T030 [US3] ResultsTable CSV 내보내기 구현 in src/gui/results_table.py (파일 대화상자)
- [X] T031 [US3] ResultsTable 클립보드 복사 구현 in src/gui/results_table.py (QClipboard)
- [X] T032 [US3] 내보내기 버튼 UI 추가 in src/gui/results_table.py

**Checkpoint**: CSV 저장 및 클립보드 복사 정상 동작

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: 마무리, 테스트 보강, 문서화

- [X] T033 [P] GUI 통합 테스트 작성 in tests/integration/gui/test_gui_integration.py
- [X] T034 [P] 설정 저장/복원 통합 테스트 in tests/integration/gui/test_gui_integration.py
- [X] T035 MainWindow 설정 저장/복원 구현 in src/gui/main_window.py (closeEvent)
- [X] T036 [P] 에러 핸들링 개선 (네트워크 오류, 빈 검색어) in src/gui/search_panel.py
- [X] T037 [P] README.md 업데이트 (GUI 사용법 추가) in README.md
- [X] T038 quickstart.md 검증 실행

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup) → Phase 2 (Foundational) → Phase 3/4/5 (User Stories) → Phase 6 (Polish)
                                          ↓
                                    [병렬 가능]
```

- **Phase 1 (Setup)**: 의존성 없음 - 즉시 시작
- **Phase 2 (Foundational)**: Phase 1 완료 필요 - **모든 User Story 차단**
- **Phase 3 (US1)**: Phase 2 완료 후 시작 가능
- **Phase 4 (US2)**: Phase 2 완료 후 시작 가능 (US1과 병렬 가능)
- **Phase 5 (US3)**: Phase 4 완료 필요 (ResultsTable에 의존)
- **Phase 6 (Polish)**: 모든 User Story 완료 후

### User Story Dependencies

- **US1 (상점 관리)**: Phase 2만 의존 - 독립 구현 가능
- **US2 (검색/결과)**: Phase 2만 의존 - US1과 병렬 가능 (ShopStore는 기존 모듈)
- **US3 (내보내기)**: US2 의존 (ResultsTable 필요)

### Within Each User Story (TDD 순서)

1. 테스트 작성 (FAIL 확인)
2. 최소 구현 (테스트 PASS)
3. 리팩토링
4. 다음 컴포넌트로 진행

### Parallel Opportunities

```bash
# Phase 1: 모든 태스크 병렬 가능
T002, T003, T004

# Phase 2: 테스트 병렬 → 구현 순차
T005, T006 (병렬)
→ T007, T008 (순차)

# Phase 3 (US1): 테스트 병렬 → 구현 순차
T011, T012 (병렬)
→ T013 → T014 → T015 → T016 → T017

# Phase 4 (US2): 테스트 병렬 → 구현 순차
T018, T019, T020 (병렬)
→ T021 → T022 → T023 → T024 → T025 → T026 → T027

# Phase 5 (US3): 테스트 병렬 → 구현 순차
T028, T029 (병렬)
→ T030 → T031 → T032
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1: Setup 완료
2. Phase 2: Foundational 완료
3. Phase 3: User Story 1 완료
4. **검증**: 상점 CRUD만으로 동작 확인
5. 필요시 배포/데모

### Incremental Delivery

1. Setup + Foundational → 기초 완료
2. US1 추가 → 테스트 → MVP 완성!
3. US2 추가 → 검색 기능 → 핵심 기능 완성!
4. US3 추가 → 내보내기 → 전체 기능 완성!
5. Polish → 품질 개선

---

## Summary

| Phase | 태스크 수 | 주요 산출물 |
|-------|----------|------------|
| 1. Setup | 4 | 프로젝트 구조, 의존성 |
| 2. Foundational | 6 | GuiSettings, MainWindow 기본 |
| 3. US1 (P1) | 7 | ShopListView, ShopEditDialog |
| 4. US2 (P2) | 10 | SearchPanel, ResultsTable, SearchWorker |
| 5. US3 (P3) | 5 | CSV/클립보드 내보내기 |
| 6. Polish | 6 | 통합 테스트, 문서화 |
| **Total** | **38** | |

### Parallel Opportunities

- Phase 1: 3개 태스크 병렬
- Phase 2: 2개 테스트 병렬
- Phase 3: 2개 테스트 병렬
- Phase 4: 3개 테스트 병렬
- Phase 5: 2개 테스트 병렬
- Phase 6: 4개 태스크 병렬

### Independent Test Criteria

| User Story | 독립 테스트 기준 |
|------------|-----------------|
| US1 | 상점 추가/수정/삭제, 체크박스 선택 동작 |
| US2 | 검색 실행, 결과 표시, 최저가 강조, 진행률 |
| US3 | CSV 저장, 클립보드 복사 |

### Suggested MVP Scope

**US1 (상점 관리)만으로 MVP 가능** - 상점 데이터베이스 관리 기능만으로도 CLI 대비 사용성 향상

---

## Notes

- [P] 태스크 = 다른 파일, 의존성 없음
- [Story] 라벨 = 특정 User Story 연결
- TDD 원칙: 테스트 FAIL 확인 후 구현
- 각 태스크 또는 논리적 그룹 후 커밋
- 체크포인트에서 독립 검증 가능
