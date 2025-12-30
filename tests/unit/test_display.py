"""
테스트: 결과 표시 (TableRenderer)

TDD에 따라 구현 전 테스트 먼저 작성.
"""

import pytest
from io import StringIO


class TestTableRenderer:
    """TableRenderer 테스트"""

    def test_table_renderer_생성(self):
        """TableRenderer 인스턴스 생성"""
        from src.display.table_renderer import TableRenderer

        renderer = TableRenderer()
        assert renderer is not None

    def test_단일_상점_결과_렌더링(self):
        """단일 상점 검색 결과를 테이블로 렌더링"""
        from src.display.table_renderer import TableRenderer
        from src.models.search import SearchResult, StockStatus

        results = [
            SearchResult(
                shop_id="shop-1",
                shop_name="테스트 상점",
                product_name="무선 마우스 M100",
                price=25000,
                price_text="₩25,000",
                stock_status=StockStatus.IN_STOCK,
            ),
            SearchResult(
                shop_id="shop-1",
                shop_name="테스트 상점",
                product_name="무선 마우스 M200",
                price=35000,
                price_text="₩35,000",
                stock_status=StockStatus.OUT_OF_STOCK,
            ),
        ]

        renderer = TableRenderer()
        output = renderer.render_results(results, keyword="마우스")

        # 테이블 문자열에 핵심 정보 포함 확인
        assert "무선 마우스 M100" in output
        assert "25,000" in output or "25000" in output
        assert "마우스" in output

    def test_빈_결과_메시지(self):
        """검색 결과가 없을 때 메시지 표시"""
        from src.display.table_renderer import TableRenderer

        renderer = TableRenderer()
        output = renderer.render_results([], keyword="없는상품")

        assert "없는상품" in output or "결과" in output

    def test_가격_포맷팅(self):
        """가격을 한국 원화 형식으로 포맷팅"""
        from src.display.table_renderer import TableRenderer

        renderer = TableRenderer()

        assert renderer.format_price(25000) == "₩25,000"
        assert renderer.format_price(1000000) == "₩1,000,000"
        assert renderer.format_price(None) == "-"

    def test_재고_상태_포맷팅(self):
        """재고 상태를 한국어로 표시"""
        from src.display.table_renderer import TableRenderer
        from src.models.search import StockStatus

        renderer = TableRenderer()

        assert "재고" in renderer.format_stock_status(StockStatus.IN_STOCK) or "있음" in renderer.format_stock_status(StockStatus.IN_STOCK)
        assert "품절" in renderer.format_stock_status(StockStatus.OUT_OF_STOCK)
        assert "알 수 없음" in renderer.format_stock_status(StockStatus.UNKNOWN) or "?" in renderer.format_stock_status(StockStatus.UNKNOWN)

    def test_console_출력(self):
        """Console에 직접 출력"""
        from src.display.table_renderer import TableRenderer
        from src.models.search import SearchResult, StockStatus
        from rich.console import Console

        results = [
            SearchResult(
                shop_id="shop-1",
                shop_name="테스트 상점",
                product_name="테스트 상품",
                price=10000,
                stock_status=StockStatus.IN_STOCK,
            ),
        ]

        renderer = TableRenderer()
        console = Console(file=StringIO())

        # 예외 없이 출력되어야 함
        renderer.print_results(results, keyword="테스트", console=console)


class TestComparisonTable:
    """다중 상점 비교 테이블 테스트"""

    def test_비교_테이블_렌더링(self):
        """다중 상점 결과를 비교 테이블로 렌더링"""
        from src.display.table_renderer import TableRenderer
        from src.models.search import SearchResult, StockStatus

        results = [
            SearchResult(
                shop_id="shop-1",
                shop_name="상점A",
                product_name="무선 마우스",
                price=20000,
                stock_status=StockStatus.IN_STOCK,
            ),
            SearchResult(
                shop_id="shop-2",
                shop_name="상점B",
                product_name="무선 마우스 Pro",
                price=18000,  # 최저가
                stock_status=StockStatus.IN_STOCK,
            ),
            SearchResult(
                shop_id="shop-3",
                shop_name="상점C",
                product_name="무선 마우스",
                price=25000,
                stock_status=StockStatus.OUT_OF_STOCK,
            ),
        ]

        renderer = TableRenderer()
        output = renderer.render_comparison(results, keyword="마우스")

        assert "상점A" in output
        assert "상점B" in output
        assert "상점C" in output
        assert "마우스" in output

    def test_최저가_하이라이트(self):
        """최저가 상품 하이라이트 표시"""
        from src.display.table_renderer import TableRenderer
        from src.models.search import SearchResult, StockStatus

        results = [
            SearchResult(
                shop_id="shop-1",
                shop_name="상점A",
                product_name="상품1",
                price=30000,
                stock_status=StockStatus.IN_STOCK,
            ),
            SearchResult(
                shop_id="shop-2",
                shop_name="상점B",
                product_name="상품2",
                price=15000,  # 최저가
                stock_status=StockStatus.IN_STOCK,
            ),
        ]

        renderer = TableRenderer()
        lowest = renderer.find_lowest_price(results)

        assert lowest is not None
        assert lowest.price == 15000
        assert lowest.shop_name == "상점B"

    def test_최저가_품절_제외(self):
        """품절 상품은 최저가 계산에서 제외"""
        from src.display.table_renderer import TableRenderer
        from src.models.search import SearchResult, StockStatus

        results = [
            SearchResult(
                shop_id="shop-1",
                shop_name="상점A",
                product_name="상품1",
                price=30000,
                stock_status=StockStatus.IN_STOCK,
            ),
            SearchResult(
                shop_id="shop-2",
                shop_name="상점B",
                product_name="상품2",
                price=10000,  # 최저가지만 품절
                stock_status=StockStatus.OUT_OF_STOCK,
            ),
        ]

        renderer = TableRenderer()
        lowest = renderer.find_lowest_price(results, exclude_out_of_stock=True)

        assert lowest is not None
        assert lowest.price == 30000  # 품절 제외 시 최저가
