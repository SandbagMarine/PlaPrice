# Implementation Plan: GUI 인터페이스

**Branch**: `002-gui-interface` | **Date**: 2024-12-30 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/002-gui-interface/spec.md`

**Note**: 이 플랜은 `/speckit.plan` 명령으로 생성됨.

## Summary

PySide6를 사용하여 PlaPrice 가격 크롤러의 GUI 인터페이스를 구현한다. 기존 CLI 버전의 핵심 로직(크롤러, 저장소, 모델)을 재사용하며, 사이드바(좌측: 상점목록) + 메인 영역(우측: 검색/결과) 구조의 데스크톱 애플리케이션을 개발한다. 상점 CRUD, 검색 실행, 결과 표시(최저가 강조), CSV/클립보드 내보내기 기능을 제공한다.

## Technical Context

**Language/Version**: Python 3.10+
**Primary Dependencies**: PySide6 (Qt 공식 Python 바인딩), requests, beautifulsoup4, lxml, pydantic, rich
**Storage**: JSON 파일 (~/.plaprice/shops.json, ~/.plaprice/gui_settings.json)
**Testing**: pytest, pytest-mock, pytest-qt
**Target Platform**: Windows 10/11 데스크톱
**Project Type**: single (기존 CLI 프로젝트에 GUI 모듈 추가)
**Performance Goals**: GUI 초기 로딩 3초 이내, 검색 결과 표시 30초 이내
**Constraints**: 메모리 <200MB, 상점당 검색 결과 최대 5개
**Scale/Scope**: 개인 사용, 상점 10-50개 수준

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| 원칙 | 상태 | 비고 |
|------|------|------|
| 테스트 우선 개발 (TDD) | ✅ 준수 | pytest-qt로 GUI 테스트, 단위 테스트 선행 작성 |
| 한국어 사용 | ✅ 준수 | UI 텍스트, 문서, 주석 모두 한국어 |
| Python 3.10+ | ✅ 준수 | 기존 프로젝트와 동일 |
| Windows 데스크톱 | ✅ 준수 | PySide6는 Windows 완전 지원 |
| 기존 구조 재사용 | ✅ 준수 | src/gui/ 디렉토리 추가, 기존 모듈 재사용 |

## Project Structure

### Documentation (this feature)

```text
specs/002-gui-interface/
├── plan.md              # 이 파일
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── gui-interface.md
└── tasks.md             # Phase 2 output (/speckit.tasks 명령으로 생성)
```

### Source Code (repository root)

```text
src/
├── models/              # 기존 데이터 모델 (Shop, SearchResult 등)
├── crawlers/            # 기존 크롤러 (HtmlCrawler, MultiShopCrawler)
├── storage/             # 기존 저장소 (ShopStore)
├── display/             # 기존 테이블 렌더러 (TableRenderer)
├── cli/                 # 기존 CLI 인터페이스
├── utils/               # 기존 유틸리티 (HttpClient)
├── gui/                 # [신규] GUI 모듈
│   ├── __init__.py
│   ├── main_window.py   # MainWindow: 메인 창, 레이아웃 관리
│   ├── shop_panel.py    # ShopListView: 상점 목록 사이드바
│   ├── shop_dialog.py   # ShopEditDialog: 상점 추가/수정 대화상자
│   ├── search_panel.py  # SearchPanel: 검색 입력 및 버튼
│   ├── results_table.py # ResultsTable: 검색 결과 테이블
│   ├── worker.py        # SearchWorker: 백그라운드 검색 스레드
│   ├── settings.py      # GuiSettings: 창 크기/위치 저장
│   └── app.py           # 애플리케이션 진입점
└── __main__.py          # CLI/GUI 분기 진입점 (수정)

tests/
├── unit/
│   ├── gui/             # [신규] GUI 단위 테스트
│   │   ├── test_main_window.py
│   │   ├── test_shop_panel.py
│   │   ├── test_shop_dialog.py
│   │   ├── test_search_panel.py
│   │   ├── test_results_table.py
│   │   ├── test_worker.py
│   │   └── test_settings.py
│   └── ...              # 기존 테스트
├── integration/
│   └── gui/             # [신규] GUI 통합 테스트
│       └── test_gui_integration.py
└── fixtures/            # 기존 테스트 픽스처
```

**Structure Decision**: 기존 single project 구조를 유지하면서 `src/gui/` 디렉토리를 추가한다. 기존 모듈(models, crawlers, storage)을 GUI에서 직접 import하여 재사용한다. 별도 패키지 분리 없이 동일 프로젝트 내에서 CLI/GUI를 모두 지원한다.

## Complexity Tracking

| 추가 사항 | 사유 | 대안 기각 이유 |
|-----------|------|---------------|
| pytest-qt 의존성 | GUI 위젯 테스트 필요 | 수동 테스트는 TDD 원칙 위반 |
| QThread 사용 | 검색 중 UI 프리징 방지 | 동기 검색은 UX 저하 |
| GUI 설정 파일 | 창 크기/위치 복원 | 매번 설정은 사용성 저하 |
