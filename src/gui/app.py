# -*- coding: utf-8 -*-
"""
GUI 애플리케이션 진입점

PlaPrice GUI를 시작하는 메인 함수.
"""

import sys

from PySide6.QtWidgets import QApplication

from src.gui.main_window import MainWindow


def run_gui() -> int:
    """
    GUI 애플리케이션 실행
    
    Returns:
        종료 코드
    """
    app = QApplication(sys.argv)
    
    # 메인 윈도우 생성 및 표시
    window = MainWindow()
    window.show()
    
    # 이벤트 루프 시작
    return app.exec()


if __name__ == "__main__":
    sys.exit(run_gui())
