"""
테스트: 다중 상점 크롤러 (MultiShopCrawler)

TDD에 따라 구현 전 테스트 먼저 작성.
"""

import pytest
from unittest.mock import MagicMock, patch


class TestMultiShopCrawler:
    """MultiShopCrawler 테스트"""

    @pytest.fixture
    def sample_shops(self):
        """테스트용 상점 목록"""
        from src.models.shop import Shop, ShopSelectors

        shops = []
        for i in range(3):
            selectors = ShopSelectors(
                product_container=".product",
                product_name=".name",
                product_price=".price",
            )
            shop = Shop(
                id=f"shop-{i+1}",
                name=f"상점{i+1}",
                base_url=f"https://shop{i+1}.example.com",
                search_url_template=f"https://shop{i+1}.example.com/search?q={{keyword}}",
                selectors=selectors,
            )
            shops.append(shop)
        return shops

    @pytest.fixture
    def mock_results(self):
        """테스트용 검색 결과"""
        from src.models.search import SearchResult, StockStatus

        return [
            SearchResult(
                shop_id="shop-1",
                shop_name="상점1",
                product_name="무선 마우스",
                price=20000,
                stock_status=StockStatus.IN_STOCK,
            ),
            SearchResult(
                shop_id="shop-2",
                shop_name="상점2",
                product_name="무선 마우스 Pro",
                price=25000,
                stock_status=StockStatus.IN_STOCK,
            ),
            SearchResult(
                shop_id="shop-3",
                shop_name="상점3",
                product_name="무선 마우스",
                price=18000,
                stock_status=StockStatus.OUT_OF_STOCK,
            ),
        ]

    def test_multi_crawler_생성(self, sample_shops):
        """MultiShopCrawler 인스턴스 생성"""
        from src.crawlers.multi_crawler import MultiShopCrawler

        crawler = MultiShopCrawler(sample_shops)
        assert crawler is not None
        assert len(crawler.shops) == 3

    def test_다중_상점_검색(self, sample_shops):
        """여러 상점에서 동시 검색"""
        from src.crawlers.multi_crawler import MultiShopCrawler
        from src.models.search import SearchResult, StockStatus

        # HtmlCrawler mock
        mock_result = SearchResult(
            shop_id="test",
            shop_name="테스트",
            product_name="테스트 상품",
            price=10000,
            stock_status=StockStatus.IN_STOCK,
        )

        with patch("src.crawlers.multi_crawler.HtmlCrawler") as MockHtmlCrawler:
            mock_crawler = MagicMock()
            mock_crawler.search.return_value = [mock_result]
            MockHtmlCrawler.return_value = mock_crawler

            crawler = MultiShopCrawler(sample_shops)
            results = crawler.search("마우스")

        # 3개 상점 x 1개 결과 = 3개 결과
        assert len(results) == 3

    def test_부분_실패_처리(self, sample_shops):
        """일부 상점 크롤링 실패 시 나머지 결과 반환"""
        from src.crawlers.multi_crawler import MultiShopCrawler
        from src.crawlers.html_crawler import CrawlError
        from src.models.search import SearchResult, StockStatus

        call_count = 0

        def mock_search(keyword):
            nonlocal call_count
            call_count += 1
            if call_count == 2:
                raise CrawlError("상점2 크롤링 실패")
            return [
                SearchResult(
                    shop_id=f"shop-{call_count}",
                    shop_name=f"상점{call_count}",
                    product_name="테스트 상품",
                    price=10000,
                    stock_status=StockStatus.IN_STOCK,
                )
            ]

        with patch("src.crawlers.multi_crawler.HtmlCrawler") as MockHtmlCrawler:
            mock_crawler = MagicMock()
            mock_crawler.search.side_effect = mock_search
            MockHtmlCrawler.return_value = mock_crawler

            crawler = MultiShopCrawler(sample_shops)
            results, errors = crawler.search_with_errors("마우스")

        # 2개 상점 성공, 1개 실패
        assert len(results) == 2
        assert len(errors) == 1
        assert "상점2" in str(errors[0]) or "shop-2" in str(errors[0])

    def test_빈_상점_목록(self):
        """상점 목록이 비어있는 경우"""
        from src.crawlers.multi_crawler import MultiShopCrawler

        crawler = MultiShopCrawler([])
        results = crawler.search("마우스")

        assert results == []

    def test_결과_가격순_정렬(self, sample_shops, mock_results):
        """검색 결과를 가격순으로 정렬"""
        from src.crawlers.multi_crawler import MultiShopCrawler

        with patch("src.crawlers.multi_crawler.HtmlCrawler") as MockHtmlCrawler:
            # 각 상점마다 다른 결과 반환
            def create_mock_crawler(shop):
                mock = MagicMock()
                for r in mock_results:
                    if r.shop_id == shop.id:
                        mock.search.return_value = [r]
                        break
                return mock

            MockHtmlCrawler.side_effect = create_mock_crawler

            crawler = MultiShopCrawler(sample_shops)
            results = crawler.search("마우스", sort_by_price=True)

        # 가격 오름차순 정렬 확인
        prices = [r.price for r in results if r.price is not None]
        assert prices == sorted(prices)
