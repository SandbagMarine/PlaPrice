"""
Search 모델 - 검색 결과 및 검색 요청

크롤링 결과와 검색 쿼리를 정의합니다.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class StockStatus(str, Enum):
    """재고 상태"""

    IN_STOCK = "IN_STOCK"
    OUT_OF_STOCK = "OUT_OF_STOCK"
    PRE_ORDER = "PRE_ORDER"
    UNKNOWN = "UNKNOWN"


class SearchResult(BaseModel):
    """
    검색 결과 모델

    크롤링으로 얻은 개별 상품 정보를 담습니다.
    """

    shop_id: str = Field(
        ...,
        description="상점 ID 참조",
    )
    shop_name: str = Field(
        ...,
        description="상점 이름 (조회 편의용)",
    )
    product_name: str = Field(
        ...,
        min_length=1,
        description="상품명",
    )
    price: Optional[int] = Field(
        default=None,
        ge=0,
        description="가격 (원, null이면 가격 정보 없음)",
    )
    price_text: Optional[str] = Field(
        default=None,
        description="원본 가격 문자열",
    )
    stock_status: StockStatus = Field(
        ...,
        description="재고 상태",
    )
    product_url: Optional[str] = Field(
        default=None,
        description="상품 상세 페이지 URL",
    )
    crawled_at: datetime = Field(
        default_factory=datetime.now,
        description="크롤링 시각",
    )


class SearchQuery(BaseModel):
    """
    검색 요청 모델

    사용자가 입력한 검색 조건을 담습니다.
    """

    keyword: str = Field(
        ...,
        min_length=1,
        description="검색 키워드",
    )
    shop_ids: Optional[list[str]] = Field(
        default=None,
        description="대상 상점 ID 목록 (None이면 모든 활성 상점)",
    )

    @field_validator("keyword")
    @classmethod
    def strip_keyword(cls, v: str) -> str:
        """키워드 앞뒤 공백 제거"""
        stripped = v.strip()
        if not stripped:
            raise ValueError("keyword는 비어있을 수 없습니다")
        return stripped
