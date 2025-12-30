"""
TableRenderer - 검색 결과 테이블 렌더러

rich 라이브러리를 사용하여 검색 결과를 테이블로 표시합니다.
"""

from typing import Optional

from rich.console import Console
from rich.table import Table

from src.models.search import SearchResult, StockStatus


class TableRenderer:
    """
    검색 결과 테이블 렌더러

    rich 라이브러리를 사용하여 터미널에 테이블을 출력합니다.
    """

    # 재고 상태별 한국어 텍스트 및 스타일
    STOCK_STATUS_MAP = {
        StockStatus.IN_STOCK: ("✓ 재고 있음", "green"),
        StockStatus.OUT_OF_STOCK: ("✗ 품절", "red"),
        StockStatus.PRE_ORDER: ("⏰ 예약상품", "cyan"),
        StockStatus.UNKNOWN: ("? 알 수 없음", "yellow"),
    }

    def format_price(self, price: Optional[int]) -> str:
        """
        가격을 한국 원화 형식으로 포맷팅

        Args:
            price: 가격 (원) 또는 None

        Returns:
            포맷팅된 가격 문자열
        """
        if price is None:
            return "-"
        return f"₩{price:,}"

    def format_stock_status(self, status: StockStatus) -> str:
        """
        재고 상태를 한국어로 포맷팅

        Args:
            status: 재고 상태

        Returns:
            한국어 재고 상태 문자열
        """
        text, _ = self.STOCK_STATUS_MAP.get(status, ("?", "white"))
        return text

    def render_results(
        self,
        results: list[SearchResult],
        keyword: str,
    ) -> str:
        """
        검색 결과를 테이블 문자열로 렌더링

        Args:
            results: 검색 결과 리스트
            keyword: 검색 키워드

        Returns:
            렌더링된 테이블 문자열
        """
        console = Console(force_terminal=True, width=120)

        if not results:
            return f"'{keyword}'에 대한 검색 결과가 없습니다."

        table = self._create_table(keyword)

        for result in results:
            self._add_row(table, result)

        # 문자열로 캡처
        with console.capture() as capture:
            console.print(table)

        return capture.get()

    def print_results(
        self,
        results: list[SearchResult],
        keyword: str,
        console: Optional[Console] = None,
    ) -> None:
        """
        검색 결과를 콘솔에 출력

        Args:
            results: 검색 결과 리스트
            keyword: 검색 키워드
            console: Rich Console (없으면 기본 콘솔 사용)
        """
        if console is None:
            console = Console()

        if not results:
            console.print(f"[yellow]'{keyword}'에 대한 검색 결과가 없습니다.[/yellow]")
            return

        table = self._create_table(keyword)

        for result in results:
            self._add_row(table, result)

        console.print(table)
        console.print(f"\n[dim]총 {len(results)}개 상품[/dim]")

    def _create_table(self, keyword: str) -> Table:
        """
        테이블 생성

        Args:
            keyword: 검색 키워드

        Returns:
            Rich Table 객체
        """
        table = Table(
            title=f"🔍 '{keyword}' 검색 결과",
            show_header=True,
            header_style="bold cyan",
        )

        table.add_column("상점", style="blue", width=15)
        table.add_column("상품명", style="white", width=40)
        table.add_column("가격", style="green", justify="right", width=12)
        table.add_column("재고", style="white", width=12)

        return table

    def _add_row(self, table: Table, result: SearchResult, is_lowest: bool = False) -> None:
        """
        테이블에 행 추가

        Args:
            table: Rich Table 객체
            result: 검색 결과
            is_lowest: 최저가 여부
        """
        stock_text, stock_style = self.STOCK_STATUS_MAP.get(
            result.stock_status,
            ("?", "white"),
        )

        price_str = self.format_price(result.price)
        if is_lowest and result.price is not None:
            price_str = f"[bold green]★ {price_str}[/bold green]"

        table.add_row(
            result.shop_name,
            result.product_name,
            price_str,
            f"[{stock_style}]{stock_text}[/{stock_style}]",
        )

    def render_comparison(
        self,
        results: list[SearchResult],
        keyword: str,
    ) -> str:
        """
        다중 상점 비교 결과를 테이블 문자열로 렌더링

        Args:
            results: 검색 결과 리스트
            keyword: 검색 키워드

        Returns:
            렌더링된 테이블 문자열
        """
        console = Console(force_terminal=True, width=120)

        if not results:
            return f"'{keyword}'에 대한 검색 결과가 없습니다."

        table = self._create_comparison_table(keyword)
        lowest = self.find_lowest_price(results, exclude_out_of_stock=True)

        for result in results:
            is_lowest = (
                lowest is not None
                and result.shop_id == lowest.shop_id
                and result.price == lowest.price
            )
            self._add_row(table, result, is_lowest=is_lowest)

        with console.capture() as capture:
            console.print(table)
            if lowest:
                console.print(
                    f"\n[bold green]★ 최저가: {lowest.shop_name} - {self.format_price(lowest.price)}[/bold green]"
                )

        return capture.get()

    def print_comparison(
        self,
        results: list[SearchResult],
        keyword: str,
        console: Optional[Console] = None,
    ) -> None:
        """
        다중 상점 비교 결과를 콘솔에 출력

        Args:
            results: 검색 결과 리스트
            keyword: 검색 키워드
            console: Rich Console
        """
        if console is None:
            console = Console()

        if not results:
            console.print(f"[yellow]'{keyword}'에 대한 검색 결과가 없습니다.[/yellow]")
            return

        table = self._create_comparison_table(keyword)
        lowest = self.find_lowest_price(results, exclude_out_of_stock=True)

        for result in results:
            is_lowest = (
                lowest is not None
                and result.shop_id == lowest.shop_id
                and result.price == lowest.price
            )
            self._add_row(table, result, is_lowest=is_lowest)

        console.print(table)
        console.print(f"\n[dim]총 {len(results)}개 상품[/dim]")

        if lowest:
            console.print(
                f"[bold green]★ 최저가: {lowest.shop_name} - {self.format_price(lowest.price)}[/bold green]"
            )

    def _create_comparison_table(self, keyword: str) -> Table:
        """
        비교 테이블 생성

        Args:
            keyword: 검색 키워드

        Returns:
            Rich Table 객체
        """
        table = Table(
            title=f"🛒 '{keyword}' 다중 상점 비교",
            show_header=True,
            header_style="bold magenta",
        )

        table.add_column("상점", style="blue", width=15)
        table.add_column("상품명", style="white", width=40)
        table.add_column("가격", justify="right", width=15)
        table.add_column("재고", style="white", width=12)

        return table

    def find_lowest_price(
        self,
        results: list[SearchResult],
        exclude_out_of_stock: bool = False,
    ) -> Optional[SearchResult]:
        """
        최저가 상품 찾기

        Args:
            results: 검색 결과 리스트
            exclude_out_of_stock: 품절 상품 제외 여부

        Returns:
            최저가 SearchResult 또는 None
        """
        candidates = [r for r in results if r.price is not None]

        if exclude_out_of_stock:
            candidates = [
                r for r in candidates if r.stock_status != StockStatus.OUT_OF_STOCK
            ]

        if not candidates:
            return None

        return min(candidates, key=lambda r: r.price)
