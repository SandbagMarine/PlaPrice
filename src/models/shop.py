"""
Shop 모델 - 크롤링 대상 웹사이트 설정 정보

상점의 기본 URL, 검색 URL 템플릿, CSS 선택자 등을 정의합니다.
"""

from datetime import datetime
from typing import Optional
from urllib.parse import quote
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator, model_validator


class ShopSelectors(BaseModel):
    """
    상점의 HTML 요소 선택자 설정

    크롤링 시 상품 정보를 추출하기 위한 CSS 선택자를 정의합니다.
    """

    product_container: str = Field(
        ...,
        min_length=1,
        description="상품 컨테이너 CSS 선택자",
    )
    product_name: str = Field(
        ...,
        min_length=1,
        description="상품명 CSS 선택자",
    )
    product_price: str = Field(
        ...,
        min_length=1,
        description="가격 CSS 선택자",
    )
    product_link: Optional[str] = Field(
        default=None,
        description="상품 상세 링크 선택자",
    )
    stock_status: Optional[str] = Field(
        default=None,
        description="재고 상태 선택자",
    )


class StockPatterns(BaseModel):
    """
    재고 상태 판별 패턴

    텍스트 매칭으로 재고 상태를 판별하기 위한 패턴을 정의합니다.
    """

    in_stock: list[str] = Field(
        default_factory=list,
        description="재고 있음 텍스트 패턴",
    )
    out_of_stock: list[str] = Field(
        default_factory=list,
        description="품절 텍스트 패턴",
    )


class Shop(BaseModel):
    """
    상점 설정 모델

    크롤링 대상 웹사이트의 설정 정보를 담습니다.
    """

    id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="고유 식별자 (UUID)",
    )
    name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="상점 표시 이름",
    )
    base_url: str = Field(
        ...,
        description="상점 기본 URL",
    )
    search_url_template: str = Field(
        ...,
        description="검색 URL 템플릿 ({keyword} 플레이스홀더 필수)",
    )
    selectors: ShopSelectors = Field(
        ...,
        description="CSS 선택자 설정",
    )
    stock_patterns: Optional[StockPatterns] = Field(
        default=None,
        description="재고 상태 판별 패턴",
    )
    enabled: bool = Field(
        default=True,
        description="활성화 여부",
    )
    verify_ssl: bool = Field(
        default=True,
        description="SSL 인증서 검증 여부 (인증서 문제 있는 사이트는 False)",
    )
    keyword_encoding: Optional[str] = Field(
        default=None,
        description="검색 키워드 인코딩 (예: euc-kr). None이면 UTF-8 URL 인코딩 사용",
    )
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="생성 시각",
    )
    updated_at: datetime = Field(
        default_factory=datetime.now,
        description="수정 시각",
    )

    @field_validator("base_url")
    @classmethod
    def validate_base_url(cls, v: str) -> str:
        """base_url이 유효한 HTTP/HTTPS URL인지 검증"""
        if not v.startswith(("http://", "https://")):
            raise ValueError("base_url은 http:// 또는 https://로 시작해야 합니다")
        return v

    @field_validator("search_url_template")
    @classmethod
    def validate_search_url_template(cls, v: str) -> str:
        """search_url_template에 {keyword} 플레이스홀더가 있는지 검증"""
        if "{keyword}" not in v:
            raise ValueError("search_url_template에 {keyword} 플레이스홀더가 필요합니다")
        return v

    def get_search_url(self, keyword: str) -> str:
        """
        키워드로 검색 URL 생성

        Args:
            keyword: 검색 키워드

        Returns:
            완성된 검색 URL
        """
        if self.keyword_encoding:
            # 지정된 인코딩으로 키워드 URL 인코딩
            encoded_keyword = quote(keyword.encode(self.keyword_encoding))
        else:
            # 기본 UTF-8 URL 인코딩
            encoded_keyword = quote(keyword)
        return self.search_url_template.replace("{keyword}", encoded_keyword)
