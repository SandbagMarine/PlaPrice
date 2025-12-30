# Research: GUI 인터페이스

**Feature**: 002-gui-interface  
**Date**: 2024-12-30  
**Status**: Complete

## 연구 목표

1. PySide6 기본 사용법 및 프로젝트 구조
2. 사이드바 + 메인 영역 레이아웃 구현 방법
3. QTableView/QTableWidget 사용법 및 스타일링
4. 백그라운드 작업 처리 (QThread)
5. pytest-qt를 활용한 GUI 테스트 방법
6. 설정 저장/복원 (QSettings)

---

## 1. PySide6 기본 구조

### 결정: PySide6 표준 구조 사용

**Rationale**: PySide6는 Qt 공식 Python 바인딩으로 LGPL 라이선스, PyQt와 API 호환, 안정적인 장기 지원을 제공한다.

### 기본 애플리케이션 패턴

```python
from PySide6.QtWidgets import QApplication, QMainWindow
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PlaPrice")
        self.setMinimumSize(800, 600)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
```

### 대안 고려

| 옵션 | 장점 | 단점 | 결정 |
|------|------|------|------|
| PyQt6 | 풍부한 문서 | GPL/상용 라이선스 | 기각 |
| tkinter | 표준 라이브러리 | 제한된 위젯, 구식 UI | 기각 |
| CustomTkinter | 모던 UI | 추가 의존성, 제한된 기능 | 기각 |
| **PySide6** | LGPL, 풍부한 위젯 | 대용량 패키지 | **채택** |

---

## 2. 사이드바 + 메인 영역 레이아웃

### 결정: QSplitter + QWidget 조합

**Rationale**: QSplitter는 사용자가 영역 크기를 조절할 수 있고, 각 영역에 독립적인 위젯을 배치할 수 있다.

### 구현 패턴

```python
from PySide6.QtWidgets import QSplitter, QWidget, QVBoxLayout
from PySide6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # 메인 스플리터 (좌우 분할)
        splitter = QSplitter(Qt.Horizontal)
        
        # 좌측: 상점 목록 패널
        self.shop_panel = ShopListView()
        splitter.addWidget(self.shop_panel)
        
        # 우측: 검색 + 결과 영역
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        self.search_panel = SearchPanel()
        self.results_table = ResultsTable()
        right_layout.addWidget(self.search_panel)
        right_layout.addWidget(self.results_table, stretch=1)
        splitter.addWidget(right_widget)
        
        # 초기 비율 설정 (좌측 250px)
        splitter.setSizes([250, 750])
        
        self.setCentralWidget(splitter)
```

### 대안 고려

| 옵션 | 장점 | 단점 | 결정 |
|------|------|------|------|
| QDockWidget | 분리/부동 가능 | 복잡한 상태 관리 | 기각 |
| 고정 QHBoxLayout | 단순함 | 크기 조절 불가 | 기각 |
| **QSplitter** | 크기 조절, 단순 | - | **채택** |

---

## 3. 테이블 위젯 (QTableView vs QTableWidget)

### 결정: QTableWidget 사용

**Rationale**: 소규모 데이터(상점 10-50개, 결과 수백 개)에서는 QTableWidget이 더 간단하고 직관적이다. 커스텀 모델이 필요한 대규모 데이터가 아니므로 QTableWidget으로 충분하다.

### 상점 목록 테이블 (체크박스 포함)

```python
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QCheckBox
from PySide6.QtCore import Qt

class ShopListView(QTableWidget):
    def __init__(self):
        super().__init__()
        self.setColumnCount(3)
        self.setHorizontalHeaderLabels(["선택", "상점명", "URL"])
        self.setSelectionBehavior(QTableWidget.SelectRows)
        
    def add_shop(self, shop):
        row = self.rowCount()
        self.insertRow(row)
        
        # 체크박스
        checkbox = QCheckBox()
        checkbox.setChecked(True)
        self.setCellWidget(row, 0, checkbox)
        
        # 상점명, URL
        self.setItem(row, 1, QTableWidgetItem(shop.name))
        self.setItem(row, 2, QTableWidgetItem(shop.base_url))
```

### 결과 테이블 (최저가 강조)

```python
from PySide6.QtGui import QColor

class ResultsTable(QTableWidget):
    HIGHLIGHT_COLOR = QColor(144, 238, 144)  # 연두색
    
    def highlight_lowest_price(self):
        """최저가 행을 연두색으로 강조"""
        if self.rowCount() == 0:
            return
            
        # 가격 컬럼에서 최저가 찾기
        min_price = float('inf')
        min_row = -1
        
        for row in range(self.rowCount()):
            price_item = self.item(row, 2)  # 가격 컬럼
            if price_item:
                try:
                    price = float(price_item.text().replace(',', '').replace('원', ''))
                    if price < min_price:
                        min_price = price
                        min_row = row
                except ValueError:
                    continue
        
        # 최저가 행 강조
        if min_row >= 0:
            for col in range(self.columnCount()):
                item = self.item(min_row, col)
                if item:
                    item.setBackground(self.HIGHLIGHT_COLOR)
```

---

## 4. 백그라운드 작업 (QThread)

### 결정: QThread + Signal/Slot 패턴

**Rationale**: 검색 작업은 네트워크 I/O를 포함하므로 메인 스레드에서 실행하면 UI가 프리징된다. QThread와 시그널을 사용하여 비동기 처리한다.

### 구현 패턴

```python
from PySide6.QtCore import QThread, Signal

class SearchWorker(QThread):
    """백그라운드 검색 워커"""
    progress = Signal(int, int)  # (현재, 전체)
    result = Signal(object)  # SearchResult
    finished = Signal(list)  # 전체 결과 리스트
    error = Signal(str)  # 에러 메시지
    
    def __init__(self, crawler, shops, query):
        super().__init__()
        self.crawler = crawler
        self.shops = shops
        self.query = query
        self._is_cancelled = False
    
    def run(self):
        results = []
        for i, shop in enumerate(self.shops):
            if self._is_cancelled:
                break
            try:
                result = self.crawler.search(shop, self.query)
                results.extend(result[:5])  # 상점당 최대 5개
                self.progress.emit(i + 1, len(self.shops))
                self.result.emit(result)
            except Exception as e:
                self.error.emit(f"{shop.name}: {str(e)}")
        self.finished.emit(results)
    
    def cancel(self):
        self._is_cancelled = True
```

### 사용 패턴

```python
class SearchPanel(QWidget):
    def start_search(self):
        self.worker = SearchWorker(self.crawler, self.shops, self.query)
        self.worker.progress.connect(self.update_progress)
        self.worker.result.connect(self.add_result)
        self.worker.finished.connect(self.search_finished)
        self.worker.error.connect(self.show_error)
        self.worker.start()
    
    def cancel_search(self):
        if self.worker and self.worker.isRunning():
            self.worker.cancel()
            self.worker.wait()
```

---

## 5. pytest-qt GUI 테스트

### 결정: pytest-qt + qtbot fixture

**Rationale**: pytest-qt는 Qt 위젯 테스트를 위한 표준 도구로, TDD 원칙을 GUI 개발에 적용할 수 있다.

### 설치

```bash
pip install pytest-qt
```

### 테스트 패턴

```python
import pytest
from PySide6.QtCore import Qt

def test_main_window_title(qtbot):
    """메인 윈도우 타이틀 테스트"""
    window = MainWindow()
    qtbot.addWidget(window)
    
    assert window.windowTitle() == "PlaPrice"

def test_shop_add_button_click(qtbot):
    """상점 추가 버튼 클릭 테스트"""
    panel = ShopListView()
    qtbot.addWidget(panel)
    
    # 버튼 클릭 시뮬레이션
    qtbot.mouseClick(panel.add_button, Qt.LeftButton)
    
    # 대화상자 열림 확인
    assert panel.dialog is not None

def test_search_with_empty_query(qtbot):
    """빈 검색어 경고 테스트"""
    panel = SearchPanel()
    qtbot.addWidget(panel)
    
    # 빈 상태에서 검색 버튼 클릭
    qtbot.mouseClick(panel.search_button, Qt.LeftButton)
    
    # 경고 메시지 표시 확인
    assert panel.warning_label.isVisible()
```

### 시그널 테스트

```python
def test_worker_progress_signal(qtbot):
    """워커 진행률 시그널 테스트"""
    worker = SearchWorker(mock_crawler, [shop], "query")
    
    with qtbot.waitSignal(worker.finished, timeout=5000):
        worker.start()
    
    # 결과 확인
    assert worker.results is not None
```

---

## 6. 설정 저장/복원 (QSettings)

### 결정: QSettings 사용

**Rationale**: QSettings는 플랫폼별 표준 위치에 설정을 저장하며, Windows에서는 레지스트리 또는 INI 파일을 사용한다. JSON 파일로도 구현 가능하지만 QSettings가 Qt 표준이다.

### 구현 패턴

```python
from PySide6.QtCore import QSettings

class GuiSettings:
    def __init__(self):
        self.settings = QSettings("PlaPrice", "GUI")
    
    def save_window_geometry(self, window):
        self.settings.setValue("geometry", window.saveGeometry())
        self.settings.setValue("state", window.saveState())
    
    def restore_window_geometry(self, window):
        geometry = self.settings.value("geometry")
        state = self.settings.value("state")
        if geometry:
            window.restoreGeometry(geometry)
        if state:
            window.restoreState(state)
    
    def save_splitter_sizes(self, splitter):
        self.settings.setValue("splitter_sizes", splitter.sizes())
    
    def restore_splitter_sizes(self, splitter):
        sizes = self.settings.value("splitter_sizes")
        if sizes:
            splitter.setSizes([int(s) for s in sizes])
```

### 대안: JSON 파일

기존 ShopStore와 일관성을 위해 JSON 파일 사용도 가능:

```python
import json
from pathlib import Path

class GuiSettings:
    DEFAULT_PATH = Path.home() / ".plaprice" / "gui_settings.json"
    
    def __init__(self, path=None):
        self.path = path or self.DEFAULT_PATH
        self.data = self._load()
    
    def _load(self):
        if self.path.exists():
            return json.loads(self.path.read_text(encoding='utf-8'))
        return {}
    
    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.data, indent=2), encoding='utf-8')
```

### 결정: JSON 파일 사용

**Rationale**: 기존 ShopStore가 JSON을 사용하므로 일관성 유지. 사용자가 설정 파일을 직접 편집할 수 있는 장점도 있음.

---

## 의존성 요약

### requirements.txt 추가 항목

```
PySide6>=6.6.0
```

### requirements-dev.txt 추가 항목

```
pytest-qt>=4.2.0
```

---

## 다음 단계

1. **data-model.md**: GUI 관련 엔티티 정의 (GuiSettings, 검색 상태 등)
2. **contracts/gui-interface.md**: 컴포넌트 간 인터페이스 정의
3. **quickstart.md**: GUI 개발 빠른 시작 가이드
