# GUI Interface Contract

**Feature**: 002-gui-interface  
**Date**: 2024-12-30  
**Status**: Complete

## 개요

GUI 컴포넌트 간의 인터페이스와 시그널/슬롯 계약을 정의한다.

---

## 컴포넌트 인터페이스

### 1. MainWindow

**파일**: `src/gui/main_window.py`

```python
class MainWindow(QMainWindow):
    """메인 애플리케이션 창"""
    
    # 속성
    shop_panel: ShopListView      # 좌측 상점 목록 패널
    search_panel: SearchPanel     # 우측 상단 검색 패널
    results_table: ResultsTable   # 우측 하단 결과 테이블
    splitter: QSplitter           # 좌우 분할 스플리터
    settings: GuiSettings         # GUI 설정
    
    # 공개 메서드
    def __init__(self): ...
    def closeEvent(self, event: QCloseEvent) -> None:
        """창 닫기 시 설정 저장"""
    
    # 내부 메서드
    def _setup_ui(self) -> None: ...
    def _connect_signals(self) -> None: ...
    def _restore_settings(self) -> None: ...
    def _save_settings(self) -> None: ...
```

---

### 2. ShopListView

**파일**: `src/gui/shop_panel.py`

```python
class ShopListView(QWidget):
    """상점 목록 사이드바 패널"""
    
    # Qt 시그널
    shop_selected = Signal(Shop)           # 상점 선택됨
    selection_changed = Signal(list)       # 체크박스 선택 변경 (list[str] - shop_ids)
    shop_added = Signal(Shop)              # 상점 추가됨
    shop_updated = Signal(Shop)            # 상점 수정됨
    shop_deleted = Signal(str)             # 상점 삭제됨 (shop_id)
    
    # 속성
    table: QTableWidget           # 상점 테이블
    add_button: QPushButton       # 추가 버튼
    edit_button: QPushButton      # 수정 버튼
    delete_button: QPushButton    # 삭제 버튼
    select_all_button: QPushButton # 전체 선택 버튼
    shop_store: ShopStore         # 상점 저장소 (기존)
    
    # 공개 메서드
    def __init__(self, shop_store: ShopStore): ...
    def refresh(self) -> None:
        """상점 목록 새로고침"""
    def get_selected_shops(self) -> list[Shop]:
        """체크박스가 선택된 상점 목록 반환"""
    def get_selected_shop_ids(self) -> list[str]:
        """체크박스가 선택된 상점 ID 목록 반환"""
    def select_all(self) -> None:
        """모든 상점 선택"""
    def deselect_all(self) -> None:
        """모든 상점 선택 해제"""
    
    # 슬롯
    def _on_add_clicked(self) -> None: ...
    def _on_edit_clicked(self) -> None: ...
    def _on_delete_clicked(self) -> None: ...
    def _on_checkbox_changed(self, row: int) -> None: ...
```

---

### 3. ShopEditDialog

**파일**: `src/gui/shop_dialog.py`

```python
class ShopEditDialog(QDialog):
    """상점 추가/수정 대화상자"""
    
    # 속성
    name_input: QLineEdit           # 상점명 입력
    url_input: QLineEdit            # URL 입력
    search_template_input: QLineEdit # 검색 URL 템플릿
    product_selector_input: QLineEdit # 상품 CSS 셀렉터
    name_selector_input: QLineEdit   # 상품명 셀렉터
    price_selector_input: QLineEdit  # 가격 셀렉터
    stock_selector_input: QLineEdit  # 재고 셀렉터
    save_button: QPushButton        # 저장 버튼
    cancel_button: QPushButton      # 취소 버튼
    
    # 공개 메서드
    def __init__(self, parent: QWidget = None, shop: Shop = None): ...
    def get_shop_data(self) -> dict:
        """입력된 상점 데이터 반환"""
    def validate(self) -> tuple[bool, str]:
        """입력값 검증, (성공여부, 에러메시지)"""
    
    # 클래스 메서드
    @classmethod
    def create_new(cls, parent: QWidget) -> Shop | None:
        """새 상점 생성 대화상자, 저장 시 Shop 반환, 취소 시 None"""
    @classmethod
    def edit_existing(cls, parent: QWidget, shop: Shop) -> Shop | None:
        """기존 상점 수정 대화상자"""
```

---

### 4. SearchPanel

**파일**: `src/gui/search_panel.py`

```python
class SearchPanel(QWidget):
    """검색 입력 및 제어 패널"""
    
    # Qt 시그널
    search_started = Signal(str, list)  # (keyword, shop_ids)
    search_cancelled = Signal()
    
    # 속성
    keyword_input: QLineEdit      # 검색어 입력
    search_button: QPushButton    # 검색 버튼
    cancel_button: QPushButton    # 취소 버튼
    progress_bar: QProgressBar    # 진행률 바
    status_label: QLabel          # 상태 메시지
    worker: SearchWorker | None   # 백그라운드 워커
    
    # 공개 메서드
    def __init__(self): ...
    def start_search(self, shops: list[Shop], keyword: str) -> None:
        """검색 시작"""
    def cancel_search(self) -> None:
        """검색 취소"""
    def set_progress(self, current: int, total: int) -> None:
        """진행률 업데이트"""
    def set_status(self, message: str) -> None:
        """상태 메시지 설정"""
    def reset(self) -> None:
        """검색 상태 초기화"""
    
    # 슬롯
    def _on_search_clicked(self) -> None: ...
    def _on_cancel_clicked(self) -> None: ...
    def _on_worker_progress(self, current: int, total: int) -> None: ...
    def _on_worker_finished(self, results: list) -> None: ...
    def _on_worker_error(self, message: str) -> None: ...
```

---

### 5. ResultsTable

**파일**: `src/gui/results_table.py`

```python
class ResultsTable(QWidget):
    """검색 결과 테이블"""
    
    # Qt 시그널
    row_double_clicked = Signal(str)  # product_url
    
    # 상수
    COLUMNS = ["상점", "상품명", "가격", "재고"]
    HIGHLIGHT_COLOR = QColor(144, 238, 144)  # 연두색
    
    # 속성
    table: QTableWidget           # 결과 테이블
    export_csv_button: QPushButton # CSV 내보내기 버튼
    copy_button: QPushButton      # 클립보드 복사 버튼
    results: list[SearchResult]   # 현재 결과 목록
    
    # 공개 메서드
    def __init__(self): ...
    def clear(self) -> None:
        """결과 테이블 초기화"""
    def add_result(self, result: SearchResult) -> None:
        """결과 한 건 추가"""
    def add_results(self, results: list[SearchResult]) -> None:
        """결과 여러 건 추가"""
    def highlight_lowest_price(self) -> None:
        """최저가 행 강조"""
    def export_to_csv(self, path: Path) -> None:
        """CSV 파일로 내보내기"""
    def copy_to_clipboard(self) -> None:
        """클립보드에 복사"""
    def get_results(self) -> list[SearchResult]:
        """현재 결과 목록 반환"""
    
    # 슬롯
    def _on_row_double_clicked(self, row: int) -> None:
        """행 더블클릭 시 브라우저 열기"""
    def _on_export_clicked(self) -> None: ...
    def _on_copy_clicked(self) -> None: ...
```

---

### 6. SearchWorker

**파일**: `src/gui/worker.py`

```python
class SearchWorker(QThread):
    """백그라운드 검색 워커"""
    
    # Qt 시그널
    progress = Signal(int, int)       # (current, total)
    result = Signal(list)             # list[SearchResult] - 한 상점 결과
    finished = Signal(list)           # list[SearchResult] - 전체 결과
    error = Signal(str, str)          # (shop_name, error_message)
    
    # 속성
    crawler: MultiShopCrawler   # 크롤러 (기존)
    shops: list[Shop]           # 검색 대상 상점
    keyword: str                # 검색 키워드
    max_results_per_shop: int   # 상점당 최대 결과 수 (기본 5)
    
    # 공개 메서드
    def __init__(
        self,
        crawler: MultiShopCrawler,
        shops: list[Shop],
        keyword: str,
        max_results_per_shop: int = 5
    ): ...
    def run(self) -> None:
        """검색 실행 (QThread.run 오버라이드)"""
    def cancel(self) -> None:
        """검색 취소 요청"""
    
    # 내부 속성
    _is_cancelled: bool
```

---

### 7. GuiSettings

**파일**: `src/gui/settings.py`

```python
class GuiSettings(BaseModel):
    """GUI 설정 (Pydantic 모델)"""
    
    # 속성
    window: WindowGeometry
    splitter: SplitterState
    last_search_keyword: str
    selected_shop_ids: list[str]
    
    # 클래스 상수
    DEFAULT_PATH: ClassVar[Path] = Path.home() / ".plaprice" / "gui_settings.json"
    
    # 클래스 메서드
    @classmethod
    def load(cls, path: Path | None = None) -> "GuiSettings":
        """설정 파일 로드, 없으면 기본값"""
    
    # 인스턴스 메서드
    def save(self, path: Path | None = None) -> None:
        """설정 파일 저장"""
```

---

## 시그널-슬롯 연결도

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              MainWindow                                  │
│                                                                          │
│  ShopListView                    SearchPanel                             │
│  ├─ selection_changed ──────────→ (연결 없음, get_selected_shops 호출)   │
│  ├─ shop_added ──────────────────→ _on_shop_changed()                   │
│  ├─ shop_updated ────────────────→ _on_shop_changed()                   │
│  └─ shop_deleted ────────────────→ _on_shop_changed()                   │
│                                                                          │
│  SearchPanel                                                             │
│  ├─ search_button.clicked ───────→ _start_search()                      │
│  │     │                                                                 │
│  │     ↓                                                                 │
│  │  SearchWorker                                                         │
│  │  ├─ progress ─────────────────→ SearchPanel._on_worker_progress()    │
│  │  ├─ result ───────────────────→ ResultsTable.add_results()           │
│  │  ├─ finished ─────────────────→ ResultsTable.highlight_lowest_price()│
│  │  └─ error ────────────────────→ SearchPanel._on_worker_error()       │
│  │                                                                       │
│  └─ cancel_button.clicked ───────→ SearchWorker.cancel()                │
│                                                                          │
│  ResultsTable                                                            │
│  ├─ row_double_clicked ──────────→ webbrowser.open(url)                 │
│  ├─ export_csv_button.clicked ───→ _on_export_clicked()                 │
│  └─ copy_button.clicked ─────────→ _on_copy_clicked()                   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 오류 처리 계약

### ShopEditDialog 검증 오류

| 필드 | 조건 | 오류 메시지 |
|------|------|------------|
| name | 비어있음 | "상점명을 입력하세요" |
| base_url | 비어있음 | "URL을 입력하세요" |
| base_url | 유효하지 않은 URL | "올바른 URL 형식이 아닙니다" |
| search_url_template | {keyword} 없음 | "검색 URL에 {keyword}를 포함해야 합니다" |

### SearchPanel 오류

| 상황 | 동작 |
|------|------|
| 검색어 비어있음 | 경고 메시지 표시, 검색 시작 안함 |
| 선택된 상점 없음 | "검색할 상점을 선택하세요" 메시지 |
| 네트워크 오류 | error 시그널로 상점별 오류 전달 |

### ResultsTable 오류

| 상황 | 동작 |
|------|------|
| CSV 저장 실패 | QMessageBox로 오류 표시 |
| 클립보드 복사 실패 | 상태 표시줄에 오류 메시지 |

---

## 테스트 계약

각 컴포넌트는 다음 테스트를 통과해야 한다:

### MainWindow

- `test_window_title`: 제목이 "PlaPrice"
- `test_initial_layout`: 스플리터와 3개 패널 존재
- `test_settings_restore`: 설정 파일 있으면 창 크기 복원
- `test_settings_save`: 창 닫을 때 설정 저장

### ShopListView

- `test_display_shops`: 상점 목록 테이블 표시
- `test_add_shop`: 추가 버튼 → 대화상자 → 목록 추가
- `test_edit_shop`: 수정 버튼 → 대화상자 → 목록 갱신
- `test_delete_shop`: 삭제 버튼 → 확인 → 목록 제거
- `test_checkbox_selection`: 체크박스 선택 시 시그널

### SearchPanel

- `test_empty_keyword_warning`: 빈 검색어 경고
- `test_search_progress`: 진행률 바 업데이트
- `test_cancel_search`: 취소 버튼 동작

### ResultsTable

- `test_add_results`: 결과 추가 및 표시
- `test_highlight_lowest`: 최저가 연두색 강조
- `test_double_click_url`: 더블클릭 시 URL 시그널
- `test_csv_export`: CSV 내보내기 형식
- `test_clipboard_copy`: 클립보드 복사 형식
