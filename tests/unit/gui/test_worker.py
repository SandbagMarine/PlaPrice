# -*- coding: utf-8 -*-
"""
SearchWorker 테스트

QThread 기반 검색 워커 테스트.
진행률 시그널, 취소, 결과 반환 테스트.
"""

import pytest
from unittest.mock import MagicMock, patch
from PySide6.QtCore import QThread


class TestSearchWorker:
    """SearchWorker 클래스 테스트"""

    @pytest.fixture
    def sample_shops(self):
        """샘플 상점 목록"""
        from src.models.shop import Shop, ShopSelectors
        return [
            Shop(
                name="상점A",
                base_url="https://shop-a.com",
                search_url_template="https://shop-a.com/search?q={keyword}",
                selectors=ShopSelectors(
                    product_container=".product",
                    product_name=".name",
                    product_price=".price"
                )
            ),
            Shop(
                name="상점B",
                base_url="https://shop-b.com",
                search_url_template="https://shop-b.com/search?q={keyword}",
                selectors=ShopSelectors(
                    product_container=".product",
                    product_name=".name",
                    product_price=".price"
                )
            ),
        ]

    def test_is_qthread(self, qtbot):
        """QThread 상속 확인"""
        from src.gui.worker import SearchWorker
        
        worker = SearchWorker("키워드", [])
        
        assert isinstance(worker, QThread)

    def test_has_progress_signal(self, qtbot):
        """진행률 시그널 존재"""
        from src.gui.worker import SearchWorker
        
        worker = SearchWorker("키워드", [])
        
        assert hasattr(worker, 'progress')

    def test_has_finished_signal(self, qtbot):
        """완료 시그널 존재"""
        from src.gui.worker import SearchWorker
        
        worker = SearchWorker("키워드", [])
        
        assert hasattr(worker, 'finished_with_results')

    def test_has_error_signal(self, qtbot):
        """에러 시그널 존재"""
        from src.gui.worker import SearchWorker
        
        worker = SearchWorker("키워드", [])
        
        assert hasattr(worker, 'error_occurred')

    def test_has_shop_completed_signal(self, qtbot):
        """개별 상점 완료 시그널"""
        from src.gui.worker import SearchWorker
        
        worker = SearchWorker("키워드", [])
        
        assert hasattr(worker, 'shop_completed')

    def test_cancel_sets_flag(self, qtbot):
        """취소 요청 시 플래그 설정"""
        from src.gui.worker import SearchWorker
        
        worker = SearchWorker("키워드", [])
        
        worker.cancel()
        
        assert worker._cancelled

    def test_is_cancelled(self, qtbot):
        """취소 상태 확인"""
        from src.gui.worker import SearchWorker
        
        worker = SearchWorker("키워드", [])
        
        assert not worker.is_cancelled()
        worker.cancel()
        assert worker.is_cancelled()

    @patch('src.gui.worker.MultiShopCrawler')
    def test_run_calls_crawler(self, mock_crawler_class, qtbot, sample_shops):
        """run 메서드가 크롤러 호출"""
        from src.gui.worker import SearchWorker
        
        # Mock 설정
        mock_crawler = MagicMock()
        mock_crawler.search_all.return_value = []
        mock_crawler_class.return_value = mock_crawler
        
        worker = SearchWorker("테스트", sample_shops)
        
        # 동기적으로 run 호출 (테스트 목적)
        worker.run()
        
        mock_crawler.search_all.assert_called_once_with("테스트")

    @patch('src.gui.worker.MultiShopCrawler')
    def test_progress_emitted(self, mock_crawler_class, qtbot, sample_shops):
        """진행률 시그널 발생 확인"""
        from src.gui.worker import SearchWorker
        
        mock_crawler = MagicMock()
        mock_crawler.search_all.return_value = []
        mock_crawler_class.return_value = mock_crawler
        
        worker = SearchWorker("테스트", sample_shops)
        
        progress_values = []
        worker.progress.connect(lambda cur, total: progress_values.append((cur, total)))
        
        worker.run()
        
        # 진행률 시그널이 발생했는지 확인
        assert len(progress_values) > 0

    @patch('src.gui.worker.MultiShopCrawler')
    def test_finished_with_results_emitted(self, mock_crawler_class, qtbot, sample_shops):
        """완료 시그널에 결과 포함"""
        from src.gui.worker import SearchWorker
        from src.models.search import SearchResult, StockStatus
        
        mock_results = [
            SearchResult(
                shop_id="shop-a",
                shop_name="상점A",
                product_name="상품1",
                price=10000,
                stock_status=StockStatus.IN_STOCK,
                product_url="https://shop-a.com/1"
            )
        ]
        
        mock_crawler = MagicMock()
        mock_crawler.search_all.return_value = mock_results
        mock_crawler_class.return_value = mock_crawler
        
        worker = SearchWorker("테스트", sample_shops)
        
        results = []
        worker.finished_with_results.connect(lambda r: results.append(r))
        
        worker.run()
        
        assert len(results) == 1
        assert len(results[0]) == 1

    @patch('src.gui.worker.MultiShopCrawler')
    def test_error_emitted_on_exception(self, mock_crawler_class, qtbot, sample_shops):
        """예외 발생 시 에러 시그널"""
        from src.gui.worker import SearchWorker
        
        mock_crawler = MagicMock()
        mock_crawler.search_all.side_effect = Exception("네트워크 오류")
        mock_crawler_class.return_value = mock_crawler
        
        worker = SearchWorker("테스트", sample_shops)
        
        errors = []
        worker.error_occurred.connect(lambda e: errors.append(e))
        
        worker.run()
        
        assert len(errors) == 1
        assert "네트워크 오류" in errors[0]

    def test_keyword_property(self, qtbot):
        """키워드 속성 확인"""
        from src.gui.worker import SearchWorker
        
        worker = SearchWorker("테스트 키워드", [])
        
        assert worker.keyword == "테스트 키워드"

    def test_shops_property(self, qtbot, sample_shops):
        """상점 목록 속성 확인"""
        from src.gui.worker import SearchWorker
        
        worker = SearchWorker("테스트", sample_shops)
        
        assert worker.shops == sample_shops
        assert len(worker.shops) == 2
