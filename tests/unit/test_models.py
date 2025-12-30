"""
테스트: 데이터 모델 (Shop, SearchResult, SearchQuery)

TDD에 따라 구현 전 테스트 먼저 작성.
"""

import pytest
from datetime import datetime
from uuid import UUID


class TestShopSelectors:
    """ShopSelectors 하위 객체 테스트"""

    def test_shop_selectors_생성_필수_필드(self):
        """필수 필드만으로 ShopSelectors 생성 가능"""
        from src.models.shop import ShopSelectors

        selectors = ShopSelectors(
            product_container=".product-item",
            product_name=".product-title",
            product_price=".product-price",
        )

        assert selectors.product_container == ".product-item"
        assert selectors.product_name == ".product-title"
        assert selectors.product_price == ".product-price"
        assert selectors.product_link is None
        assert selectors.stock_status is None

    def test_shop_selectors_생성_모든_필드(self):
        """모든 필드로 ShopSelectors 생성 가능"""
        from src.models.shop import ShopSelectors

        selectors = ShopSelectors(
            product_container=".product-item",
            product_name=".product-title",
            product_price=".product-price",
            product_link=".product-link a",
            stock_status=".stock-status",
        )

        assert selectors.product_link == ".product-link a"
        assert selectors.stock_status == ".stock-status"


class TestStockPatterns:
    """StockPatterns 하위 객체 테스트"""

    def test_stock_patterns_기본값(self):
        """기본 재고 패턴으로 생성 가능"""
        from src.models.shop import StockPatterns

        patterns = StockPatterns()

        assert patterns.in_stock == []
        assert patterns.out_of_stock == []

    def test_stock_patterns_커스텀_패턴(self):
        """커스텀 재고 패턴 설정 가능"""
        from src.models.shop import StockPatterns

        patterns = StockPatterns(
            in_stock=["재고 있음", "구매 가능"],
            out_of_stock=["품절", "일시 품절"],
        )

        assert "재고 있음" in patterns.in_stock
        assert "품절" in patterns.out_of_stock


class TestShop:
    """Shop 모델 테스트"""

    def test_shop_생성_필수_필드(self):
        """필수 필드로 Shop 생성 가능"""
        from src.models.shop import Shop, ShopSelectors

        selectors = ShopSelectors(
            product_container=".product",
            product_name=".title",
            product_price=".price",
        )

        shop = Shop(
            name="테스트 상점",
            base_url="https://example.com",
            search_url_template="https://example.com/search?q={keyword}",
            selectors=selectors,
        )

        assert shop.name == "테스트 상점"
        assert shop.base_url == "https://example.com"
        assert shop.enabled is True  # 기본값
        assert shop.id is not None  # 자동 생성
        assert isinstance(shop.id, str)

    def test_shop_id_자동생성(self):
        """Shop 생성 시 ID가 자동으로 UUID 형식으로 생성됨"""
        from src.models.shop import Shop, ShopSelectors

        selectors = ShopSelectors(
            product_container=".product",
            product_name=".title",
            product_price=".price",
        )

        shop = Shop(
            name="테스트",
            base_url="https://example.com",
            search_url_template="https://example.com/search?q={keyword}",
            selectors=selectors,
        )

        # UUID 형식 검증
        UUID(shop.id)  # ValueError 발생하면 테스트 실패

    def test_shop_search_url_template_필수_플레이스홀더(self):
        """search_url_template에 {keyword} 플레이스홀더 필수"""
        from src.models.shop import Shop, ShopSelectors
        from pydantic import ValidationError

        selectors = ShopSelectors(
            product_container=".product",
            product_name=".title",
            product_price=".price",
        )

        with pytest.raises(ValidationError):
            Shop(
                name="테스트",
                base_url="https://example.com",
                search_url_template="https://example.com/search?q=test",  # {keyword} 없음
                selectors=selectors,
            )

    def test_shop_name_길이_제한(self):
        """name은 1~50자 제한"""
        from src.models.shop import Shop, ShopSelectors
        from pydantic import ValidationError

        selectors = ShopSelectors(
            product_container=".product",
            product_name=".title",
            product_price=".price",
        )

        # 빈 이름
        with pytest.raises(ValidationError):
            Shop(
                name="",
                base_url="https://example.com",
                search_url_template="https://example.com/search?q={keyword}",
                selectors=selectors,
            )

        # 50자 초과
        with pytest.raises(ValidationError):
            Shop(
                name="a" * 51,
                base_url="https://example.com",
                search_url_template="https://example.com/search?q={keyword}",
                selectors=selectors,
            )

    def test_shop_base_url_유효성_검사(self):
        """base_url은 유효한 HTTP/HTTPS URL이어야 함"""
        from src.models.shop import Shop, ShopSelectors
        from pydantic import ValidationError

        selectors = ShopSelectors(
            product_container=".product",
            product_name=".title",
            product_price=".price",
        )

        # 잘못된 URL
        with pytest.raises(ValidationError):
            Shop(
                name="테스트",
                base_url="not-a-valid-url",
                search_url_template="https://example.com/search?q={keyword}",
                selectors=selectors,
            )

    def test_shop_timestamps_자동생성(self):
        """created_at, updated_at 자동 생성"""
        from src.models.shop import Shop, ShopSelectors

        selectors = ShopSelectors(
            product_container=".product",
            product_name=".title",
            product_price=".price",
        )

        shop = Shop(
            name="테스트",
            base_url="https://example.com",
            search_url_template="https://example.com/search?q={keyword}",
            selectors=selectors,
        )

        assert shop.created_at is not None
        assert shop.updated_at is not None
        assert isinstance(shop.created_at, datetime)

    def test_shop_get_search_url(self):
        """키워드로 검색 URL 생성"""
        from src.models.shop import Shop, ShopSelectors
        from urllib.parse import quote

        selectors = ShopSelectors(
            product_container=".product",
            product_name=".title",
            product_price=".price",
        )

        shop = Shop(
            name="테스트",
            base_url="https://example.com",
            search_url_template="https://example.com/search?q={keyword}",
            selectors=selectors,
        )

        url = shop.get_search_url("무선 마우스")
        # URL 인코딩이 적용됨
        expected = f"https://example.com/search?q={quote('무선 마우스')}"
        assert url == expected

    def test_shop_get_search_url_with_encoding(self):
        """키워드를 특정 인코딩으로 URL 생성"""
        from src.models.shop import Shop, ShopSelectors
        from urllib.parse import quote

        selectors = ShopSelectors(
            product_container=".product",
            product_name=".title",
            product_price=".price",
        )

        shop = Shop(
            name="테스트",
            base_url="https://example.com",
            search_url_template="https://example.com/search?q={keyword}",
            selectors=selectors,
            keyword_encoding="euc-kr",
        )

        url = shop.get_search_url("볼티모어")
        # EUC-KR 인코딩이 적용됨
        expected = f"https://example.com/search?q={quote('볼티모어'.encode('euc-kr'))}"
        assert url == expected

    def test_shop_json_직렬화(self):
        """Shop을 JSON으로 직렬화/역직렬화 가능"""
        from src.models.shop import Shop, ShopSelectors

        selectors = ShopSelectors(
            product_container=".product",
            product_name=".title",
            product_price=".price",
        )

        shop = Shop(
            name="테스트",
            base_url="https://example.com",
            search_url_template="https://example.com/search?q={keyword}",
            selectors=selectors,
        )

        json_str = shop.model_dump_json()
        restored = Shop.model_validate_json(json_str)

        assert restored.name == shop.name
        assert restored.id == shop.id


class TestStockStatus:
    """StockStatus Enum 테스트"""

    def test_stock_status_값들(self):
        """StockStatus에 필요한 값들이 존재"""
        from src.models.search import StockStatus

        assert StockStatus.IN_STOCK.value == "IN_STOCK"
        assert StockStatus.OUT_OF_STOCK.value == "OUT_OF_STOCK"
        assert StockStatus.UNKNOWN.value == "UNKNOWN"


class TestSearchResult:
    """SearchResult 모델 테스트"""

    def test_search_result_생성_필수_필드(self):
        """필수 필드로 SearchResult 생성 가능"""
        from src.models.search import SearchResult, StockStatus

        result = SearchResult(
            shop_id="test-shop-id",
            shop_name="테스트 상점",
            product_name="무선 마우스 M100",
            stock_status=StockStatus.IN_STOCK,
        )

        assert result.shop_id == "test-shop-id"
        assert result.shop_name == "테스트 상점"
        assert result.product_name == "무선 마우스 M100"
        assert result.stock_status == StockStatus.IN_STOCK
        assert result.price is None
        assert result.crawled_at is not None

    def test_search_result_가격_정보(self):
        """가격 정보 포함 SearchResult 생성"""
        from src.models.search import SearchResult, StockStatus

        result = SearchResult(
            shop_id="test-shop-id",
            shop_name="테스트 상점",
            product_name="무선 마우스 M100",
            price=25000,
            price_text="₩25,000",
            stock_status=StockStatus.IN_STOCK,
        )

        assert result.price == 25000
        assert result.price_text == "₩25,000"

    def test_search_result_가격_양수_검증(self):
        """price는 0 이상이어야 함"""
        from src.models.search import SearchResult, StockStatus
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            SearchResult(
                shop_id="test-shop-id",
                shop_name="테스트 상점",
                product_name="테스트 상품",
                price=-1000,
                stock_status=StockStatus.IN_STOCK,
            )

    def test_search_result_product_name_비어있지_않음(self):
        """product_name은 비어있지 않아야 함"""
        from src.models.search import SearchResult, StockStatus
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            SearchResult(
                shop_id="test-shop-id",
                shop_name="테스트 상점",
                product_name="",
                stock_status=StockStatus.IN_STOCK,
            )

    def test_search_result_crawled_at_자동생성(self):
        """crawled_at 자동 생성"""
        from src.models.search import SearchResult, StockStatus

        result = SearchResult(
            shop_id="test-shop-id",
            shop_name="테스트 상점",
            product_name="테스트 상품",
            stock_status=StockStatus.IN_STOCK,
        )

        assert result.crawled_at is not None
        assert isinstance(result.crawled_at, datetime)


class TestSearchQuery:
    """SearchQuery 모델 테스트"""

    def test_search_query_단일_상점(self):
        """단일 상점 검색 쿼리 생성"""
        from src.models.search import SearchQuery

        query = SearchQuery(
            keyword="무선 마우스",
            shop_ids=["shop-1"],
        )

        assert query.keyword == "무선 마우스"
        assert query.shop_ids == ["shop-1"]

    def test_search_query_다중_상점(self):
        """다중 상점 검색 쿼리 생성"""
        from src.models.search import SearchQuery

        query = SearchQuery(
            keyword="키보드",
            shop_ids=["shop-1", "shop-2", "shop-3"],
        )

        assert len(query.shop_ids) == 3

    def test_search_query_모든_상점(self):
        """shop_ids가 비어있으면 모든 활성 상점 대상"""
        from src.models.search import SearchQuery

        query = SearchQuery(keyword="마우스")

        assert query.shop_ids is None or query.shop_ids == []

    def test_search_query_keyword_비어있지_않음(self):
        """keyword는 비어있지 않아야 함"""
        from src.models.search import SearchQuery
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            SearchQuery(keyword="")

    def test_search_query_keyword_공백_제거(self):
        """keyword 앞뒤 공백 자동 제거"""
        from src.models.search import SearchQuery

        query = SearchQuery(keyword="  마우스  ")

        assert query.keyword == "마우스"
