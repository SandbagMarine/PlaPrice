# -*- coding: utf-8 -*-
"""
검색 패널

키워드 입력, 검색/취소 버튼, 진행률 바를 포함하는 검색 패널.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QProgressBar,
    QLabel,
    QMessageBox,
)


class SearchPanel(QWidget):
    """검색 패널"""
    
    # 시그널
    search_requested = Signal(str)  # keyword
    cancel_requested = Signal()
    
    def __init__(self, parent=None):
        """SearchPanel 초기화"""
        super().__init__(parent)
        
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self) -> None:
        """UI 구성"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 검색 입력 영역
        search_layout = QHBoxLayout()
        
        # 검색어 입력
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("검색어를 입력하세요...")
        search_layout.addWidget(self.search_input)
        
        # 검색 버튼
        self.search_button = QPushButton("검색")
        self.search_button.setMinimumWidth(80)
        search_layout.addWidget(self.search_button)
        
        # 취소 버튼
        self.cancel_button = QPushButton("취소")
        self.cancel_button.setMinimumWidth(80)
        self.cancel_button.setEnabled(False)
        search_layout.addWidget(self.cancel_button)
        
        layout.addLayout(search_layout)
        
        # 진행률 바
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(True)
        layout.addWidget(self.progress_bar)
        
        # 상태 레이블
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
    
    def _connect_signals(self) -> None:
        """시그널 연결"""
        self.search_button.clicked.connect(self._on_search_clicked)
        self.cancel_button.clicked.connect(self._on_cancel_clicked)
        self.search_input.returnPressed.connect(self._on_search_clicked)
    
    def _on_search_clicked(self) -> None:
        """검색 버튼 클릭 처리"""
        keyword = self.get_keyword()
        
        if not keyword:
            QMessageBox.warning(
                self,
                "검색어 필요",
                "검색어를 입력해주세요."
            )
            return
        
        self.search_requested.emit(keyword)
    
    def _on_cancel_clicked(self) -> None:
        """취소 버튼 클릭 처리"""
        self.cancel_requested.emit()
    
    def get_keyword(self) -> str:
        """
        검색어 가져오기 (공백 제거)
        
        Returns:
            검색어 문자열
        """
        return self.search_input.text().strip()
    
    def set_searching(self, searching: bool) -> None:
        """
        검색 중 상태 설정
        
        Args:
            searching: 검색 중 여부
        """
        self.search_button.setEnabled(not searching)
        self.search_input.setEnabled(not searching)
        self.cancel_button.setEnabled(searching)
        self.progress_bar.setVisible(searching)
        
        if searching:
            self.progress_bar.setValue(0)
            self.status_label.setText("검색 중...")
        else:
            self.status_label.setText("")
    
    def update_progress(self, current: int, total: int) -> None:
        """
        진행률 업데이트
        
        Args:
            current: 현재 진행 수
            total: 전체 수
        """
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        
        if total > 0:
            percentage = int(current / total * 100)
            self.status_label.setText(f"검색 중... {current}/{total} ({percentage}%)")
    
    def set_status(self, message: str) -> None:
        """
        상태 메시지 설정
        
        Args:
            message: 상태 메시지
        """
        self.status_label.setText(message)
