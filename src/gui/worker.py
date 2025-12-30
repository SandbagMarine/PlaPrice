# -*- coding: utf-8 -*-
"""
검색 워커

QThread 기반 백그라운드 검색 워커.
메인 UI 블로킹 없이 크롤링 수행.
"""

from PySide6.QtCore import QThread, Signal

from src.models.shop import Shop
from src.models.search import SearchResult
from src.crawlers.multi_crawler import MultiShopCrawler


class SearchWorker(QThread):
    """백그라운드 검색 워커"""
    
    # 시그널
    progress = Signal(int, int)  # (current, total)
    shop_completed = Signal(str, list)  # (shop_name, results)
    finished_with_results = Signal(list)  # all results
    error_occurred = Signal(str)  # error message
    
    def __init__(self, keyword: str, shops: list[Shop], parent=None):
        """
        SearchWorker 초기화
        
        Args:
            keyword: 검색 키워드
            shops: 검색할 상점 목록
            parent: 부모 QObject
        """
        super().__init__(parent)
        
        self._keyword = keyword
        self._shops = shops
        self._cancelled = False
    
    @property
    def keyword(self) -> str:
        """검색 키워드"""
        return self._keyword
    
    @property
    def shops(self) -> list[Shop]:
        """검색 대상 상점 목록"""
        return self._shops
    
    def cancel(self) -> None:
        """검색 취소 요청"""
        self._cancelled = True
    
    def is_cancelled(self) -> bool:
        """취소 상태 확인"""
        return self._cancelled
    
    def run(self) -> None:
        """검색 실행 (백그라운드 스레드)"""
        try:
            all_results: list[SearchResult] = []
            total_shops = len(self._shops)
            
            if total_shops == 0:
                self.finished_with_results.emit([])
                return
            
            # 진행률 초기화
            self.progress.emit(0, total_shops)
            
            # MultiShopCrawler 사용
            crawler = MultiShopCrawler(self._shops)
            
            # 전체 검색 수행
            all_results = crawler.search_all(self._keyword)
            
            # 취소 확인
            if self._cancelled:
                self.finished_with_results.emit([])
                return
            
            # 완료 진행률
            self.progress.emit(total_shops, total_shops)
            
            # 결과 반환
            self.finished_with_results.emit(all_results)
            
        except Exception as e:
            self.error_occurred.emit(str(e))
            self.finished_with_results.emit([])
