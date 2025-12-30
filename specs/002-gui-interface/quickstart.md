# Quickstart: GUI 인터페이스 개발

**Feature**: 002-gui-interface  
**Date**: 2024-12-30

## 빠른 시작

### 1. 환경 설정

```powershell
# 가상환경 활성화
.\.venv\Scripts\Activate.ps1

# PySide6 설치
pip install PySide6>=6.6.0

# pytest-qt 설치 (테스트용)
pip install pytest-qt>=4.2.0
```

### 2. GUI 실행

```powershell
# GUI 모드로 실행
python -m src --gui

# 또는 직접 실행
python -m src.gui.app
```

### 3. 테스트 실행

```powershell
# GUI 테스트만 실행
pytest tests/unit/gui/ -v

# 전체 테스트 (GUI 포함)
pytest tests/ -v
```

---

## 프로젝트 구조

```
src/gui/
├── __init__.py       # 패키지 초기화
├── app.py            # 애플리케이션 진입점
├── main_window.py    # 메인 윈도우
├── shop_panel.py     # 상점 목록 사이드바
├── shop_dialog.py    # 상점 편집 대화상자
├── search_panel.py   # 검색 패널
├── results_table.py  # 결과 테이블
├── worker.py         # 백그라운드 워커
└── settings.py       # GUI 설정

tests/unit/gui/
├── test_main_window.py
├── test_shop_panel.py
├── test_shop_dialog.py
├── test_search_panel.py
├── test_results_table.py
├── test_worker.py
└── test_settings.py
```

---

## 개발 워크플로우 (TDD)

### 단계 1: 테스트 작성

```python
# tests/unit/gui/test_main_window.py
import pytest
from PySide6.QtCore import Qt

def test_window_title(qtbot):
    """메인 윈도우 제목 테스트"""
    from src.gui.main_window import MainWindow
    
    window = MainWindow()
    qtbot.addWidget(window)
    
    assert window.windowTitle() == "PlaPrice"
```

### 단계 2: 테스트 실행 (실패 확인)

```powershell
pytest tests/unit/gui/test_main_window.py -v
# FAILED - 아직 구현 안됨
```

### 단계 3: 최소 구현

```python
# src/gui/main_window.py
from PySide6.QtWidgets import QMainWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PlaPrice")
```

### 단계 4: 테스트 통과 확인

```powershell
pytest tests/unit/gui/test_main_window.py -v
# PASSED
```

### 단계 5: 리팩토링 및 다음 테스트

---

## 핵심 패턴

### 시그널/슬롯 연결

```python
from PySide6.QtCore import Signal

class SearchPanel(QWidget):
    search_started = Signal(str, list)  # (keyword, shop_ids)
    
    def __init__(self):
        super().__init__()
        self.search_button.clicked.connect(self._on_search_clicked)
    
    def _on_search_clicked(self):
        keyword = self.keyword_input.text()
        shop_ids = self.get_selected_shop_ids()
        self.search_started.emit(keyword, shop_ids)
```

### QThread 사용

```python
from PySide6.QtCore import QThread, Signal

class SearchWorker(QThread):
    progress = Signal(int, int)
    finished = Signal(list)
    
    def run(self):
        for i, shop in enumerate(self.shops):
            if self._is_cancelled:
                break
            result = self.crawler.search(shop, self.keyword)
            self.progress.emit(i + 1, len(self.shops))
        self.finished.emit(self.results)
```

### pytest-qt 테스트

```python
def test_button_click(qtbot):
    widget = MyWidget()
    qtbot.addWidget(widget)
    
    # 버튼 클릭 시뮬레이션
    qtbot.mouseClick(widget.button, Qt.LeftButton)
    
    # 시그널 대기
    with qtbot.waitSignal(widget.some_signal, timeout=1000):
        widget.trigger_action()
```

---

## 참고 문서

- [PySide6 문서](https://doc.qt.io/qtforpython-6/)
- [pytest-qt 문서](https://pytest-qt.readthedocs.io/)
- [research.md](research.md) - 기술 조사 결과
- [data-model.md](data-model.md) - 데이터 모델 정의
- [contracts/gui-interface.md](contracts/gui-interface.md) - 컴포넌트 인터페이스

---

## 체크리스트

### 구현 전

- [ ] PySide6 설치 확인
- [ ] pytest-qt 설치 확인
- [ ] 기존 테스트 통과 확인 (`pytest tests/ -v`)

### US1 (상점 관리) 완료 조건

- [ ] ShopListView 테스트 통과
- [ ] ShopEditDialog 테스트 통과
- [ ] 상점 추가/수정/삭제 동작 확인

### US2 (검색 및 결과) 완료 조건

- [ ] SearchPanel 테스트 통과
- [ ] ResultsTable 테스트 통과
- [ ] SearchWorker 테스트 통과
- [ ] 최저가 강조 동작 확인

### US3 (내보내기) 완료 조건

- [ ] CSV 내보내기 테스트 통과
- [ ] 클립보드 복사 테스트 통과

### 통합 테스트

- [ ] 전체 워크플로우 테스트 통과
- [ ] 설정 저장/복원 테스트 통과
