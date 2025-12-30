"""
MultiShopCrawler - 다중 상점 크롤러

여러 상점에서 동시에 검색하고 결과를 통합합니다.
"""

from typing import Optional

from src.crawlers.html_crawler import CrawlError, HtmlCrawler
from src.models.search import SearchResult
from src.models.shop import Shop


class MultiShopCrawler:
    """
    다중 상점 크롤러

    여러 상점에서 순차적으로 검색하고 결과를 통합합니다.
    """

    def __init__(self, shops: list[Shop]):
        """
        MultiShopCrawler 초기화

        Args:
            shops: 검색 대상 상점 목록
        """
        self.shops = shops

    def search(
        self,
        keyword: str,
        sort_by_price: bool = False,
    ) -> list[SearchResult]:
        """
        모든 상점에서 검색

        실패한 상점은 건너뛰고 성공한 결과만 반환합니다.

        Args:
            keyword: 검색 키워드
            sort_by_price: 가격순 정렬 여부

        Returns:
            통합된 검색 결과 리스트
        """
        results, _ = self.search_with_errors(keyword)

        if sort_by_price:
            results = self._sort_by_price(results)

        return results

    def search_with_errors(
        self,
        keyword: str,
    ) -> tuple[list[SearchResult], list[CrawlError]]:
        """
        모든 상점에서 검색하고 오류 정보도 반환

        Args:
            keyword: 검색 키워드

        Returns:
            (성공한 결과 리스트, 발생한 오류 리스트)
        """
        all_results: list[SearchResult] = []
        errors: list[CrawlError] = []

        for shop in self.shops:
            try:
                crawler = HtmlCrawler(shop)
                results = crawler.search(keyword)
                all_results.extend(results)
            except CrawlError as e:
                errors.append(e)

        return all_results, errors

    def _sort_by_price(
        self,
        results: list[SearchResult],
    ) -> list[SearchResult]:
        """
        결과를 가격순으로 정렬

        가격이 None인 항목은 맨 뒤로 배치합니다.

        Args:
            results: 검색 결과 리스트

        Returns:
            정렬된 리스트
        """

        def price_key(result: SearchResult) -> tuple[int, int]:
            if result.price is None:
                return (1, 0)  # None은 맨 뒤로
            return (0, result.price)

        return sorted(results, key=price_key)
