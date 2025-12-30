"""
테스트: 크롤러 (BaseCrawler, HtmlCrawler)

TDD에 따라 구현 전 테스트 먼저 작성.
"""

import pytest
from pathlib import Path


# 테스트 픽스처 경로
FIXTURES_DIR = Path(__file__).parent.parent / "fixtures" / "sample_html"


class TestBaseCrawler:
    """BaseCrawler 추상 클래스 테스트"""

    def test_base_crawler_추상_클래스(self):
        """BaseCrawler는 직접 인스턴스화 불가"""
        from src.crawlers.base import BaseCrawler

        with pytest.raises(TypeError):
            BaseCrawler()

    def test_base_crawler_search_메서드_정의(self):
        """BaseCrawler는 search 추상 메서드 정의"""
        from src.crawlers.base import BaseCrawler
        from abc import ABC

        assert issubclass(BaseCrawler, ABC)
        assert hasattr(BaseCrawler, "search")


class TestHtmlCrawler:
    """HtmlCrawler 테스트"""

    def test_html_crawler_생성(self):
        """HtmlCrawler 인스턴스 생성"""
        from src.crawlers.html_crawler import HtmlCrawler
        from src.models.shop import Shop, ShopSelectors

        selectors = ShopSelectors(
            product_container=".product-item",
            product_name=".product-title",
            product_price=".product-price",
        )

        shop = Shop(
            name="테스트 상점",
            base_url="https://example.com",
            search_url_template="https://example.com/search?q={keyword}",
            selectors=selectors,
        )

        crawler = HtmlCrawler(shop)
        assert crawler.shop == shop

    def test_html_파싱_상품_추출(self):
        """HTML에서 상품 정보 추출"""
        from src.crawlers.html_crawler import HtmlCrawler
        from src.models.shop import Shop, ShopSelectors

        html_path = FIXTURES_DIR / "search_results.html"
        html_content = html_path.read_text(encoding="utf-8")

        selectors = ShopSelectors(
            product_container=".product-item",
            product_name=".product-title",
            product_price=".product-price",
            stock_status=".stock-status",
        )

        shop = Shop(
            name="테스트 상점",
            base_url="https://example.com",
            search_url_template="https://example.com/search?q={keyword}",
            selectors=selectors,
        )

        crawler = HtmlCrawler(shop)
        results = crawler.parse_html(html_content)

        assert len(results) == 3
        assert results[0].product_name == "무선 마우스 M100 블랙"
        assert results[0].price == 25000
        assert results[0].shop_name == "테스트 상점"

    def test_가격_파싱_다양한_형식(self):
        """다양한 가격 형식 파싱"""
        from src.crawlers.html_crawler import HtmlCrawler
        from src.models.shop import Shop, ShopSelectors

        html_path = FIXTURES_DIR / "various_prices.html"
        html_content = html_path.read_text(encoding="utf-8")

        selectors = ShopSelectors(
            product_container=".product-item",
            product_name=".product-title",
            product_price=".product-price",
        )

        shop = Shop(
            name="테스트",
            base_url="https://example.com",
            search_url_template="https://example.com/search?q={keyword}",
            selectors=selectors,
        )

        crawler = HtmlCrawler(shop)
        results = crawler.parse_html(html_content)

        # "15,000원" -> 15000
        assert results[0].price == 15000
        # "₩ 20,000" -> 20000
        assert results[1].price == 20000
        # "30000" -> 30000
        assert results[2].price == 30000
        # "가격문의" -> None
        assert results[3].price is None

    def test_재고_상태_판별(self):
        """재고 상태 텍스트로 판별"""
        from src.crawlers.html_crawler import HtmlCrawler
        from src.models.shop import Shop, ShopSelectors, StockPatterns
        from src.models.search import StockStatus

        html_path = FIXTURES_DIR / "search_results.html"
        html_content = html_path.read_text(encoding="utf-8")

        selectors = ShopSelectors(
            product_container=".product-item",
            product_name=".product-title",
            product_price=".product-price",
            stock_status=".stock-status",
        )

        stock_patterns = StockPatterns(
            in_stock=["재고 있음", "구매 가능"],
            out_of_stock=["품절", "재고 없음"],
        )

        shop = Shop(
            name="테스트",
            base_url="https://example.com",
            search_url_template="https://example.com/search?q={keyword}",
            selectors=selectors,
            stock_patterns=stock_patterns,
        )

        crawler = HtmlCrawler(shop)
        results = crawler.parse_html(html_content)

        assert results[0].stock_status == StockStatus.IN_STOCK  # "재고 있음"
        assert results[1].stock_status == StockStatus.OUT_OF_STOCK  # "품절"
        assert results[2].stock_status == StockStatus.IN_STOCK  # "재고 있음"

    def test_검색_결과_없음(self):
        """검색 결과가 없는 경우 빈 리스트 반환"""
        from src.crawlers.html_crawler import HtmlCrawler
        from src.models.shop import Shop, ShopSelectors

        html_path = FIXTURES_DIR / "no_results.html"
        html_content = html_path.read_text(encoding="utf-8")

        selectors = ShopSelectors(
            product_container=".product-item",
            product_name=".product-title",
            product_price=".product-price",
        )

        shop = Shop(
            name="테스트",
            base_url="https://example.com",
            search_url_template="https://example.com/search?q={keyword}",
            selectors=selectors,
        )

        crawler = HtmlCrawler(shop)
        results = crawler.parse_html(html_content)

        assert results == []

    def test_상품_링크_추출(self):
        """상품 상세 페이지 링크 추출"""
        from src.crawlers.html_crawler import HtmlCrawler
        from src.models.shop import Shop, ShopSelectors

        html_path = FIXTURES_DIR / "search_results.html"
        html_content = html_path.read_text(encoding="utf-8")

        selectors = ShopSelectors(
            product_container=".product-item",
            product_name=".product-title",
            product_price=".product-price",
            product_link=".product-link",
        )

        shop = Shop(
            name="테스트",
            base_url="https://example.com",
            search_url_template="https://example.com/search?q={keyword}",
            selectors=selectors,
        )

        crawler = HtmlCrawler(shop)
        results = crawler.parse_html(html_content)

        assert results[0].product_url == "https://example.com/product/1001"

    def test_parse_price_메서드(self):
        """가격 문자열 파싱 유틸리티"""
        from src.crawlers.html_crawler import HtmlCrawler
        from src.models.shop import Shop, ShopSelectors

        selectors = ShopSelectors(
            product_container=".product",
            product_name=".name",
            product_price=".price",
        )

        shop = Shop(
            name="테스트",
            base_url="https://example.com",
            search_url_template="https://example.com/search?q={keyword}",
            selectors=selectors,
        )

        crawler = HtmlCrawler(shop)

        assert crawler.parse_price("₩25,000") == 25000
        assert crawler.parse_price("15,000원") == 15000
        assert crawler.parse_price("₩ 30,000") == 30000
        assert crawler.parse_price("10000") == 10000
        assert crawler.parse_price("가격문의") is None
        assert crawler.parse_price("") is None
