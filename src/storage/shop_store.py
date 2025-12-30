"""
ShopStore - 상점 저장소

상점 설정을 JSON 파일로 저장하고 관리합니다.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from src.models.shop import Shop


class ShopStoreError(Exception):
    """상점 저장소 오류"""

    pass


class ShopStore:
    """
    상점 저장소

    상점 설정을 JSON 파일로 저장하고 CRUD 기능을 제공합니다.
    """

    DEFAULT_CONFIG_DIR = Path.home() / ".plaprice"
    SHOPS_FILENAME = "shops.json"

    def __init__(
        self,
        config_dir: Optional[Path] = None,
        auto_save: bool = True,
    ):
        """
        ShopStore 초기화

        Args:
            config_dir: 설정 디렉토리 경로 (없으면 기본 경로 사용)
            auto_save: 변경 시 자동 저장 여부
        """
        self.config_dir = config_dir or self.DEFAULT_CONFIG_DIR
        self.auto_save = auto_save
        self._shops: dict[str, Shop] = {}

        # 설정 디렉토리 생성
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # 기존 데이터 로드
        self.load()

    @property
    def _shops_file(self) -> Path:
        """상점 JSON 파일 경로"""
        return self.config_dir / self.SHOPS_FILENAME

    def load(self) -> None:
        """JSON 파일에서 상점 목록 로드"""
        if not self._shops_file.exists():
            self._shops = {}
            return

        try:
            with open(self._shops_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            self._shops = {}
            for shop_data in data.get("shops", []):
                shop = Shop.model_validate(shop_data)
                self._shops[shop.id] = shop

        except (json.JSONDecodeError, Exception) as e:
            # 파일이 손상된 경우 빈 상태로 시작
            self._shops = {}

    def save(self) -> None:
        """상점 목록을 JSON 파일로 저장"""
        data = {
            "shops": [
                json.loads(shop.model_dump_json())
                for shop in self._shops.values()
            ]
        }

        with open(self._shops_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def add(self, shop: Shop) -> None:
        """
        상점 추가

        Args:
            shop: 추가할 상점

        Raises:
            ShopStoreError: 동일 ID가 이미 존재하는 경우
        """
        if shop.id in self._shops:
            raise ShopStoreError(f"이미 존재하는 상점 ID: {shop.id}")

        self._shops[shop.id] = shop

        if self.auto_save:
            self.save()

    def get(self, shop_id: str) -> Optional[Shop]:
        """
        ID로 상점 조회

        Args:
            shop_id: 상점 ID

        Returns:
            Shop 또는 None
        """
        return self._shops.get(shop_id)

    def remove(self, shop_id: str) -> bool:
        """
        상점 삭제

        Args:
            shop_id: 삭제할 상점 ID

        Returns:
            삭제 성공 여부
        """
        if shop_id not in self._shops:
            return False

        del self._shops[shop_id]

        if self.auto_save:
            self.save()

        return True

    def update(self, shop: Shop) -> None:
        """
        상점 정보 업데이트

        Args:
            shop: 업데이트할 상점
        """
        if shop.id not in self._shops:
            raise ShopStoreError(f"존재하지 않는 상점 ID: {shop.id}")

        shop.updated_at = datetime.now()
        self._shops[shop.id] = shop

        if self.auto_save:
            self.save()

    def list_all(self) -> list[Shop]:
        """
        모든 상점 목록 반환

        Returns:
            상점 리스트
        """
        return list(self._shops.values())

    def list_active(self) -> list[Shop]:
        """
        활성화된 상점만 반환

        Returns:
            활성 상점 리스트
        """
        return [shop for shop in self._shops.values() if shop.enabled]

    def set_enabled(self, shop_id: str, enabled: bool) -> bool:
        """
        상점 활성화/비활성화

        Args:
            shop_id: 상점 ID
            enabled: 활성화 여부

        Returns:
            성공 여부
        """
        shop = self.get(shop_id)
        if not shop:
            return False

        shop.enabled = enabled
        shop.updated_at = datetime.now()

        if self.auto_save:
            self.save()

        return True
