"""
HtmlCrawler - HTML 정적 크롤러

BeautifulSoup을 사용하여 HTML에서 상품 정보를 추출합니다.
"""

import re
from typing import Optional
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from src.crawlers.base import BaseCrawler
from src.models.search import SearchResult, StockStatus
from src.models.shop import Shop
from src.utils.http_client import HttpClient, HttpClientError


class CrawlError(Exception):
    """크롤링 오류"""

    pass


class HtmlCrawler(BaseCrawler):
    """
    HTML 정적 크롤러

    BeautifulSoup을 사용하여 정적 HTML 페이지에서 상품 정보를 추출합니다.
    """

    # 가격 추출을 위한 정규식 (숫자만 추출)
    PRICE_PATTERN = re.compile(r"[\d,]+")

    def __init__(self, shop: Shop, http_client: Optional[HttpClient] = None):
        """
        HtmlCrawler 초기화

        Args:
            shop: 상점 설정
            http_client: HTTP 클라이언트 (없으면 새로 생성)
        """
        self.shop = shop
        self.http_client = http_client or HttpClient(verify_ssl=shop.verify_ssl)

    def search(self, keyword: str) -> list[SearchResult]:
        """
        키워드로 상품 검색

        Args:
            keyword: 검색 키워드

        Returns:
            검색 결과 리스트

        Raises:
            CrawlError: 크롤링 실패 시
        """
        try:
            url = self.shop.get_search_url(keyword)
            html = self.http_client.get_html(url, encoding=self.shop.keyword_encoding)
            return self.parse_html(html)
        except HttpClientError as e:
            raise CrawlError(f"크롤링 실패: {self.shop.name} - {e}") from e

    def parse_html(self, html: str) -> list[SearchResult]:
        """
        HTML을 파싱하여 상품 정보 추출

        Args:
            html: HTML 문자열

        Returns:
            검색 결과 리스트
        """
        soup = BeautifulSoup(html, "lxml")
        selectors = self.shop.selectors

        # 상품 컨테이너 찾기
        containers = soup.select(selectors.product_container)
        results = []

        for container in containers:
            result = self._parse_product(container)
            if result:
                results.append(result)

        return results

    def _parse_product(self, container) -> Optional[SearchResult]:
        """
        개별 상품 컨테이너에서 정보 추출

        Args:
            container: BeautifulSoup 요소

        Returns:
            SearchResult 또는 None (파싱 실패 시)
        """
        selectors = self.shop.selectors

        # 상품명 추출 (필수)
        # "." 셀렉터는 컨테이너 자체를 참조
        if selectors.product_name == '.':
            name_elem = container
        else:
            name_elem = container.select_one(selectors.product_name)
        if not name_elem:
            return None

        product_name = name_elem.get_text(strip=True)
        if not product_name:
            return None

        # 가격 추출 (여러 개 있으면 마지막 유효한 가격 = 할인가)
        price = None
        price_text = None
        price_selector = selectors.product_price
        
        # 형제 셀렉터 지원 (+ 또는 ~ 로 시작하는 경우)
        if price_selector.startswith('+') or price_selector.startswith('~'):
            # 컨테이너가 a 태그인 경우, 부모 td의 형제에서 찾기
            search_base = container
            if container.name == 'a':
                parent_td = container.find_parent('td')
                if parent_td:
                    search_base = parent_td
            
            # 형제 요소에서 찾기
            # 예: "+ td + td + td" -> 3번째 다음 형제에서 가격
            siblings = search_base.find_next_siblings()
            sibling_count = price_selector.count('+') + price_selector.count('~')
            if len(siblings) >= sibling_count:
                price_elem = siblings[sibling_count - 1]
                if price_elem:
                    text = price_elem.get_text(strip=True)
                    if text:
                        parsed = self.parse_price(text)
                        if parsed is not None:
                            price = parsed
                            price_text = text
        else:
            # 컨테이너 내부에서 찾기 (기존 방식)
            price_elems = container.select(price_selector)
            for price_elem in price_elems:
                text = price_elem.get_text(strip=True)
                if text:  # 비어있지 않은 경우만
                    parsed = self.parse_price(text)
                    if parsed is not None:
                        price = parsed
                        price_text = text

        # 재고 상태 추출
        stock_status = StockStatus.UNKNOWN
        
        # 1. 명시적 stock_selector가 있으면 사용
        if selectors.stock_status:
            stock_elem = container.select_one(selectors.stock_status)
            if stock_elem:
                stock_text = stock_elem.get_text(strip=True)
                stock_status = self._determine_stock_status(stock_text)
        
        # 2. stock_selector가 없으면 자동 감지
        if stock_status == StockStatus.UNKNOWN:
            # 품절 이미지 감지 (alt 속성에 '품절' 포함 또는 src에 soldout 포함)
            soldout_img = container.find('img', alt=lambda x: x and '품절' in x)
            if not soldout_img:
                soldout_img = container.find('img', src=lambda x: x and 'soldout' in x.lower())
            
            if soldout_img:
                stock_status = StockStatus.OUT_OF_STOCK
            else:
                # 예약상품 감지 (상품명에 예약/발매예정/입고예정 포함)
                preorder_keywords = ['예약', '발매예정', '입고예정', '예정']
                if any(kw in product_name for kw in preorder_keywords):
                    stock_status = StockStatus.PRE_ORDER
                else:
                    # 품절/예약이 아니면 재고 있음으로 간주
                    stock_status = StockStatus.IN_STOCK

        # 상품 링크 추출
        product_url = None
        if selectors.product_link:
            # "." 셀렉터는 컨테이너 자체를 참조
            if selectors.product_link == '.':
                link_elem = container
            else:
                link_elem = container.select_one(selectors.product_link)
            if link_elem:
                href = link_elem.get("href")
                if href:
                    product_url = urljoin(self.shop.base_url, href)

        return SearchResult(
            shop_id=self.shop.id,
            shop_name=self.shop.name,
            product_name=product_name,
            price=price,
            price_text=price_text,
            stock_status=stock_status,
            product_url=product_url,
        )

    def parse_price(self, price_text: str) -> Optional[int]:
        """
        가격 문자열에서 숫자 추출

        Args:
            price_text: 가격 문자열 (예: "₩25,000", "15,000원")

        Returns:
            정수 가격 또는 None
        """
        if not price_text:
            return None

        # 숫자와 쉼표만 추출
        match = self.PRICE_PATTERN.search(price_text)
        if not match:
            return None

        # 쉼표 제거 후 정수 변환
        try:
            price_str = match.group().replace(",", "")
            return int(price_str)
        except ValueError:
            return None

    def _determine_stock_status(self, stock_text: str) -> StockStatus:
        """
        재고 상태 텍스트로 상태 판별

        Args:
            stock_text: 재고 상태 텍스트

        Returns:
            StockStatus
        """
        if not stock_text:
            return StockStatus.UNKNOWN

        stock_text_lower = stock_text.lower()

        # 상점별 패턴 사용
        if self.shop.stock_patterns:
            for pattern in self.shop.stock_patterns.out_of_stock:
                if pattern.lower() in stock_text_lower:
                    return StockStatus.OUT_OF_STOCK

            for pattern in self.shop.stock_patterns.in_stock:
                if pattern.lower() in stock_text_lower:
                    return StockStatus.IN_STOCK

        # 기본 한국어 패턴
        out_of_stock_keywords = ["품절", "재고 없음", "일시품절", "sold out"]
        in_stock_keywords = ["재고 있음", "구매 가능", "바로 구매", "in stock"]

        for keyword in out_of_stock_keywords:
            if keyword.lower() in stock_text_lower:
                return StockStatus.OUT_OF_STOCK

        for keyword in in_stock_keywords:
            if keyword.lower() in stock_text_lower:
                return StockStatus.IN_STOCK

        return StockStatus.UNKNOWN
