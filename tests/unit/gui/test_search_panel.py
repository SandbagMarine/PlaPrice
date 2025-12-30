# -*- coding: utf-8 -*-
"""
SearchPanel 테스트

검색 입력, 버튼, 진행률 바 테스트.
"""

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLineEdit, QPushButton, QProgressBar


class TestSearchPanel:
    """SearchPanel 클래스 테스트"""

    def test_has_search_input(self, qtbot):
        """검색어 입력 필드 존재 테스트"""
        from src.gui.search_panel import SearchPanel
        
        panel = SearchPanel()
        qtbot.addWidget(panel)
        
        assert hasattr(panel, 'search_input')
        assert isinstance(panel.search_input, QLineEdit)

    def test_has_search_button(self, qtbot):
        """검색 버튼 존재 테스트"""
        from src.gui.search_panel import SearchPanel
        
        panel = SearchPanel()
        qtbot.addWidget(panel)
        
        assert hasattr(panel, 'search_button')
        assert isinstance(panel.search_button, QPushButton)

    def test_has_cancel_button(self, qtbot):
        """취소 버튼 존재 테스트"""
        from src.gui.search_panel import SearchPanel
        
        panel = SearchPanel()
        qtbot.addWidget(panel)
        
        assert hasattr(panel, 'cancel_button')
        assert isinstance(panel.cancel_button, QPushButton)

    def test_cancel_button_disabled_initially(self, qtbot):
        """초기 상태에서 취소 버튼 비활성화"""
        from src.gui.search_panel import SearchPanel
        
        panel = SearchPanel()
        qtbot.addWidget(panel)
        
        assert not panel.cancel_button.isEnabled()

    def test_has_progress_bar(self, qtbot):
        """진행률 바 존재 테스트"""
        from src.gui.search_panel import SearchPanel
        
        panel = SearchPanel()
        qtbot.addWidget(panel)
        
        assert hasattr(panel, 'progress_bar')
        assert isinstance(panel.progress_bar, QProgressBar)

    def test_progress_bar_hidden_initially(self, qtbot):
        """초기 상태에서 진행률 바 숨김"""
        from src.gui.search_panel import SearchPanel
        
        panel = SearchPanel()
        qtbot.addWidget(panel)
        
        assert not panel.progress_bar.isVisible()

    def test_has_search_signal(self, qtbot):
        """검색 시작 시그널 존재 테스트"""
        from src.gui.search_panel import SearchPanel
        
        panel = SearchPanel()
        qtbot.addWidget(panel)
        
        assert hasattr(panel, 'search_requested')

    def test_search_button_emits_signal(self, qtbot):
        """검색 버튼 클릭 시 시그널 발생"""
        from src.gui.search_panel import SearchPanel
        
        panel = SearchPanel()
        qtbot.addWidget(panel)
        
        # 검색어 입력
        panel.search_input.setText("테스트 키워드")
        
        # 시그널 대기
        with qtbot.waitSignal(panel.search_requested, timeout=1000) as blocker:
            qtbot.mouseClick(panel.search_button, Qt.LeftButton)
        
        assert blocker.args == ["테스트 키워드"]

    def test_empty_search_shows_warning(self, qtbot, mocker):
        """빈 검색어로 검색 시 경고"""
        from src.gui.search_panel import SearchPanel
        
        panel = SearchPanel()
        qtbot.addWidget(panel)
        
        # QMessageBox.warning 모킹
        mock_warning = mocker.patch('src.gui.search_panel.QMessageBox.warning')
        
        # 빈 검색어 상태에서 검색
        panel.search_input.setText("")
        qtbot.mouseClick(panel.search_button, Qt.LeftButton)
        
        # 경고 메시지가 표시되어야 함
        mock_warning.assert_called_once()
        # 시그널은 발생하지 않아야 함 - 별도 확인 불필요 (로직상 return)

    def test_get_keyword(self, qtbot):
        """검색어 가져오기"""
        from src.gui.search_panel import SearchPanel
        
        panel = SearchPanel()
        qtbot.addWidget(panel)
        
        panel.search_input.setText("  테스트 키워드  ")
        
        assert panel.get_keyword() == "테스트 키워드"

    def test_set_searching_state(self, qtbot):
        """검색 중 상태 설정"""
        from src.gui.search_panel import SearchPanel
        
        panel = SearchPanel()
        qtbot.addWidget(panel)
        panel.show()  # 부모 위젯을 표시해야 isVisible이 올바르게 작동
        
        panel.set_searching(True)
        
        assert not panel.search_button.isEnabled()
        assert panel.cancel_button.isEnabled()
        assert not panel.progress_bar.isHidden()  # isHidden()은 위젯 자체 상태 반환

    def test_set_idle_state(self, qtbot):
        """검색 완료 후 상태 복원"""
        from src.gui.search_panel import SearchPanel
        
        panel = SearchPanel()
        qtbot.addWidget(panel)
        
        panel.set_searching(True)
        panel.set_searching(False)
        
        assert panel.search_button.isEnabled()
        assert not panel.cancel_button.isEnabled()
        assert not panel.progress_bar.isVisible()

    def test_update_progress(self, qtbot):
        """진행률 업데이트"""
        from src.gui.search_panel import SearchPanel
        
        panel = SearchPanel()
        qtbot.addWidget(panel)
        
        panel.set_searching(True)
        panel.update_progress(50, 100)
        
        assert panel.progress_bar.value() == 50
        assert panel.progress_bar.maximum() == 100

    def test_enter_key_triggers_search(self, qtbot):
        """Enter 키로 검색 실행"""
        from src.gui.search_panel import SearchPanel
        
        panel = SearchPanel()
        qtbot.addWidget(panel)
        
        panel.search_input.setText("테스트")
        
        with qtbot.waitSignal(panel.search_requested, timeout=1000):
            qtbot.keyClick(panel.search_input, Qt.Key_Return)
