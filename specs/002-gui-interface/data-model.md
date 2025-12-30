# Data Model: GUI 인터페이스

**Feature**: 002-gui-interface  
**Date**: 2024-12-30  
**Status**: Complete

## 개요

GUI 인터페이스에서 사용하는 데이터 모델을 정의한다. 기존 CLI 프로젝트의 모델(Shop, SearchResult, SearchQuery 등)을 재사용하며, GUI 전용 모델을 추가한다.

---

## 기존 모델 (재사용)

### Shop (src/models/shop.py)

```python
class Shop(BaseModel):
    id: str                          # UUID
    name: str                        # 상점명
    base_url: str                    # 기본 URL
    search_url_template: str         # 검색 URL 템플릿
    selectors: ShopSelectors         # CSS 셀렉터
    stock_patterns: StockPatterns    # 재고 패턴
    created_at: datetime
    updated_at: datetime
```

### SearchResult (src/models/search.py)

```python
class SearchResult(BaseModel):
    shop_name: str       # 상점명
    product_name: str    # 상품명
    price: int | None    # 가격 (원)
    stock_status: StockStatus  # 재고 상태
    product_url: str     # 상품 URL
    crawled_at: datetime # 크롤링 시각
```

### SearchQuery (src/models/search.py)

```python
class SearchQuery(BaseModel):
    keyword: str         # 검색 키워드
    shop_ids: list[str] | None  # 대상 상점 ID (None이면 전체)
```

---

## 신규 모델 (GUI 전용)

### GuiSettings

**위치**: `src/gui/settings.py`  
**저장 경로**: `~/.plaprice/gui_settings.json`

GUI 상태 저장/복원을 위한 설정 모델.

```python
class WindowGeometry(BaseModel):
    """창 크기 및 위치"""
    x: int = 100
    y: int = 100
    width: int = 1000
    height: int = 700
    is_maximized: bool = False

class SplitterState(BaseModel):
    """스플리터 상태"""
    sizes: list[int] = [250, 750]  # 좌측, 우측 크기

class GuiSettings(BaseModel):
    """GUI 전체 설정"""
    window: WindowGeometry = WindowGeometry()
    splitter: SplitterState = SplitterState()
    last_search_keyword: str = ""
    selected_shop_ids: list[str] = []  # 마지막으로 선택된 상점들
    
    @classmethod
    def load(cls, path: Path | None = None) -> "GuiSettings":
        """설정 파일 로드"""
        ...
    
    def save(self, path: Path | None = None) -> None:
        """설정 파일 저장"""
        ...
```

### SearchState

**위치**: `src/gui/worker.py`

검색 진행 상태를 나타내는 열거형 및 상태 모델.

```python
from enum import Enum

class SearchStatus(str, Enum):
    """검색 상태"""
    IDLE = "idle"           # 대기 중
    SEARCHING = "searching" # 검색 중
    CANCELLED = "cancelled" # 취소됨
    COMPLETED = "completed" # 완료
    ERROR = "error"         # 오류

class SearchProgress(BaseModel):
    """검색 진행 상태"""
    status: SearchStatus = SearchStatus.IDLE
    current: int = 0        # 현재 완료된 상점 수
    total: int = 0          # 전체 상점 수
    results: list[SearchResult] = []
    errors: list[str] = []
```

### ShopSelection

**위치**: `src/gui/shop_panel.py`

상점 선택 상태를 나타내는 모델.

```python
class ShopSelection(BaseModel):
    """상점 선택 상태"""
    shop_id: str
    is_selected: bool = True
```

---

## 엔티티 관계도

```
┌─────────────────────────────────────────────────────────────────┐
│                         MainWindow                               │
│  ┌─────────────────┐    ┌─────────────────────────────────────┐ │
│  │  ShopListView   │    │           Right Panel               │ │
│  │  ───────────────│    │  ┌─────────────────────────────────┐│ │
│  │  [✓] 상점1      │    │  │         SearchPanel             ││ │
│  │  [✓] 상점2      │    │  │  [검색어 입력]  [검색] [취소]   ││ │
│  │  [ ] 상점3      │    │  │  [진행률 바]                    ││ │
│  │  ───────────────│    │  └─────────────────────────────────┘│ │
│  │  [추가][수정]   │    │  ┌─────────────────────────────────┐│ │
│  │  [삭제][전체선택]│    │  │         ResultsTable            ││ │
│  └─────────────────┘    │  │  상점 | 상품명 | 가격 | 재고    ││ │
│         ↓               │  │  ─────────────────────────────  ││ │
│  ┌─────────────────┐    │  │  A점 | 상품X | 10,000 | 재고있음││ │
│  │ ShopEditDialog  │    │  │  B점 | 상품X | 9,500  | 품절   ││ │← 최저가 강조
│  │ [이름] [URL]    │    │  │  ─────────────────────────────  ││ │
│  │ [셀렉터 설정]   │    │  │  [CSV 내보내기] [클립보드 복사] ││ │
│  └─────────────────┘    │  └─────────────────────────────────┘│ │
│                         └─────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
              │                           │
              ↓                           ↓
        ┌──────────┐              ┌──────────────┐
        │ ShopStore│              │ SearchWorker │
        │ (기존)   │              │ (QThread)    │
        └──────────┘              └──────────────┘
              │                           │
              ↓                           ↓
        ~/.plaprice/              MultiShopCrawler
        shops.json                    (기존)
```

---

## 데이터 흐름

### 1. 상점 관리 흐름

```
ShopListView → ShopEditDialog → ShopStore → shops.json
     ↑               │
     └───────────────┘ (상점 목록 새로고침)
```

### 2. 검색 흐름

```
SearchPanel (키워드 입력)
     │
     ↓
ShopListView (선택된 상점 목록)
     │
     ↓
SearchWorker (QThread)
     │ progress signal
     ↓
SearchPanel (진행률 표시)
     │ result signal
     ↓
ResultsTable (결과 추가)
     │ finished signal
     ↓
ResultsTable (최저가 강조)
```

### 3. 설정 저장 흐름

```
MainWindow (창 닫기 이벤트)
     │
     ↓
GuiSettings.save()
     │
     ↓
~/.plaprice/gui_settings.json
```

---

## 검증 규칙

### Shop 검증

- `name`: 1-100자, 공백만 불가
- `base_url`: 유효한 HTTP(S) URL
- `search_url_template`: `{keyword}` 플레이스홀더 포함 필수

### SearchQuery 검증

- `keyword`: 1-100자, 공백만 불가
- `shop_ids`: None이거나 1개 이상의 유효한 UUID

### GuiSettings 검증

- `window.width`: 400 이상
- `window.height`: 300 이상
- `splitter.sizes`: 2개 요소, 각각 100 이상

---

## 마이그레이션

기존 모델 변경 없음. 신규 모델만 추가.

| 모델 | 상태 | 비고 |
|------|------|------|
| Shop | 기존 유지 | 변경 없음 |
| SearchResult | 기존 유지 | 변경 없음 |
| SearchQuery | 기존 유지 | 변경 없음 |
| GuiSettings | **신규** | GUI 전용 |
| SearchProgress | **신규** | GUI 전용 |
| ShopSelection | **신규** | GUI 전용 |
