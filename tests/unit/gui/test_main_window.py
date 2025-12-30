# -*- coding: utf-8 -*-
"""
MainWindow 테스트

메인 윈도우 기본 기능을 테스트한다.
"""

import pytest
from PySide6.QtCore import Qt


class TestMainWindow:
    """MainWindow 클래스 테스트"""

    def test_window_title(self, qtbot):
        """메인 윈도우 제목 테스트"""
        from src.gui.main_window import MainWindow
        
        window = MainWindow()
        qtbot.addWidget(window)
        
        assert window.windowTitle() == "PlaPrice"

    def test_window_minimum_size(self, qtbot):
        """최소 창 크기 테스트"""
        from src.gui.main_window import MainWindow
        
        window = MainWindow()
        qtbot.addWidget(window)
        
        min_size = window.minimumSize()
        assert min_size.width() >= 800
        assert min_size.height() >= 600

    def test_has_central_widget(self, qtbot):
        """중앙 위젯 존재 테스트"""
        from src.gui.main_window import MainWindow
        
        window = MainWindow()
        qtbot.addWidget(window)
        
        assert window.centralWidget() is not None

    def test_has_splitter(self, qtbot):
        """스플리터 존재 테스트"""
        from src.gui.main_window import MainWindow
        from PySide6.QtWidgets import QSplitter
        
        window = MainWindow()
        qtbot.addWidget(window)
        
        # 스플리터가 존재해야 함
        assert hasattr(window, 'splitter')
        assert isinstance(window.splitter, QSplitter)

    def test_splitter_orientation(self, qtbot):
        """스플리터 방향 테스트 (수평)"""
        from src.gui.main_window import MainWindow
        
        window = MainWindow()
        qtbot.addWidget(window)
        
        assert window.splitter.orientation() == Qt.Horizontal

    def test_has_settings(self, qtbot):
        """GuiSettings 속성 존재 테스트"""
        from src.gui.main_window import MainWindow
        from src.gui.settings import GuiSettings
        
        window = MainWindow()
        qtbot.addWidget(window)
        
        assert hasattr(window, 'settings')
        assert isinstance(window.settings, GuiSettings)
