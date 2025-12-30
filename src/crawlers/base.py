"""
BaseCrawler - 크롤러 기본 추상 클래스

모든 크롤러가 구현해야 하는 인터페이스를 정의합니다.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.shop import Shop
    from src.models.search import SearchResult


class BaseCrawler(ABC):
    """
    크롤러 기본 추상 클래스

    모든 크롤러는 이 클래스를 상속받아 search 메서드를 구현해야 합니다.
    """

    @abstractmethod
    def search(self, keyword: str) -> list["SearchResult"]:
        """
        키워드로 상품 검색

        Args:
            keyword: 검색 키워드

        Returns:
            검색 결과 리스트
        """
        pass
