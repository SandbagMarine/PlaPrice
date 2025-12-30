# -*- coding: utf-8 -*-
"""
메인 윈도우

PlaPrice GUI의 메인 애플리케이션 창.
사이드바(좌측: 상점목록) + 메인 영역(우측: 검색/결과) 구조.
"""

import webbrowser
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow,
    QSplitter,
    QWidget,
    QVBoxLayout,
    QLabel,
    QMessageBox,
)

from src.gui.settings import GuiSettings
from src.gui.shop_panel import ShopListView
from src.gui.search_panel import SearchPanel
from src.gui.results_table import ResultsTable
from src.gui.worker import SearchWorker
from src.storage.shop_store import ShopStore


class MainWindow(QMainWindow):
    """메인 애플리케이션 창"""
    
    def __init__(
        self,
        settings: GuiSettings | None = None,
        shop_store: ShopStore | None = None
    ):
        """
        메인 윈도우 초기화
        
        Args:
            settings: GUI 설정 (None이면 기본값 로드)
            shop_store: 상점 저장소 (None이면 기본 경로 사용)
        """
        super().__init__()
        
        # 설정 로드
        self.settings = settings or GuiSettings.load()
        
        # 상점 저장소
        self.shop_store = shop_store or ShopStore()
        
        # 검색 워커
        self._search_worker: SearchWorker | None = None
        
        # UI 설정
        self._setup_ui()
        
        # 시그널 연결
        self._connect_signals()
        
        # 설정 복원
        self._restore_settings()
    
    def _setup_ui(self) -> None:
        """UI 구성요소 설정"""
        # 윈도우 기본 설정
        self.setWindowTitle("PlaPrice")
        self.setMinimumSize(800, 600)
        
        # 메인 스플리터 (좌우 분할)
        self.splitter = QSplitter(Qt.Horizontal)
        
        # 좌측: 상점 목록 패널
        self.shop_list_view = ShopListView(self.shop_store)
        self.splitter.addWidget(self.shop_list_view)
        
        # 우측: 검색 + 결과 영역
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # 검색 패널
        self.search_panel = SearchPanel()
        right_layout.addWidget(self.search_panel)
        
        # 결과 테이블
        self.results_table = ResultsTable()
        right_layout.addWidget(self.results_table)
        
        self.splitter.addWidget(right_panel)
        
        # 스플리터 초기 크기 설정
        self.splitter.setSizes(self.settings.splitter.sizes)
        
        # 중앙 위젯 설정
        self.setCentralWidget(self.splitter)
    
    def _connect_signals(self) -> None:
        """시그널 연결"""
        # 검색 시그널
        self.search_panel.search_requested.connect(self._on_search_requested)
        self.search_panel.cancel_requested.connect(self._on_cancel_requested)
        
        # 결과 더블클릭 시그널
        self.results_table.url_open_requested.connect(self._on_url_requested)
    
    def _on_search_requested(self, keyword: str) -> None:
        """
        검색 요청 처리
        
        Args:
            keyword: 검색 키워드
        """
        # 선택된 상점 가져오기
        selected_shops = self.shop_list_view.get_selected_shops()
        
        if not selected_shops:
            QMessageBox.warning(
                self,
                "상점 선택 필요",
                "검색할 상점을 선택해주세요."
            )
            return
        
        # 기존 워커 정리
        if self._search_worker is not None:
            self._search_worker.cancel()
            self._search_worker.wait()
        
        # 결과 초기화
        self.results_table.clear_results()
        
        # 검색 상태로 전환
        self.search_panel.set_searching(True)
        
        # 워커 생성 및 시작
        self._search_worker = SearchWorker(keyword, selected_shops)
        self._search_worker.progress.connect(self._on_search_progress)
        self._search_worker.shop_completed.connect(self._on_shop_completed)
        self._search_worker.finished_with_results.connect(self._on_search_finished)
        self._search_worker.error_occurred.connect(self._on_search_error)
        self._search_worker.start()
    
    def _on_cancel_requested(self) -> None:
        """검색 취소 요청 처리"""
        if self._search_worker is not None:
            self._search_worker.cancel()
            self.search_panel.set_searching(False)
            self.search_panel.set_status("검색이 취소되었습니다.")
    
    def _on_search_progress(self, current: int, total: int) -> None:
        """
        검색 진행률 업데이트
        
        Args:
            current: 현재 진행 수
            total: 전체 수
        """
        self.search_panel.update_progress(current, total)
    
    def _on_shop_completed(self, shop_name: str, result_count: int) -> None:
        """
        상점 검색 완료 처리
        
        Args:
            shop_name: 상점 이름
            result_count: 결과 수
        """
        self.search_panel.set_status(f"{shop_name}: {result_count}개 결과")
    
    def _on_search_finished(self, results: list) -> None:
        """
        검색 완료 처리
        
        Args:
            results: 검색 결과 목록
        """
        self.search_panel.set_searching(False)
        self.results_table.display_results(results)
        self.search_panel.set_status(f"검색 완료: 총 {len(results)}개 결과")
    
    def _on_search_error(self, error_message: str) -> None:
        """
        검색 오류 처리
        
        Args:
            error_message: 오류 메시지
        """
        self.search_panel.set_searching(False)
        self.search_panel.set_status(f"오류: {error_message}")
        QMessageBox.critical(
            self,
            "검색 오류",
            f"검색 중 오류가 발생했습니다:\n{error_message}"
        )
    
    def _on_url_requested(self, url: str) -> None:
        """
        URL 열기 요청 처리
        
        Args:
            url: 열 URL
        """
        if url:
            webbrowser.open(url)
    
    def _restore_settings(self) -> None:
        """설정에서 창 상태 복원"""
        geometry = self.settings.window
        
        if geometry.is_maximized:
            self.showMaximized()
        else:
            self.setGeometry(
                geometry.x,
                geometry.y,
                geometry.width,
                geometry.height
            )
    
    def _save_settings(self) -> None:
        """창 상태를 설정에 저장"""
        # 창 크기/위치 저장
        self.settings.window.is_maximized = self.isMaximized()
        
        if not self.isMaximized():
            geometry = self.geometry()
            self.settings.window.x = geometry.x()
            self.settings.window.y = geometry.y()
            self.settings.window.width = geometry.width()
            self.settings.window.height = geometry.height()
        
        # 스플리터 크기 저장
        self.settings.splitter.sizes = self.splitter.sizes()
        
        # 파일에 저장
        self.settings.save()
    
    def closeEvent(self, event) -> None:
        """창 닫기 이벤트 처리"""
        self._save_settings()
        super().closeEvent(event)
