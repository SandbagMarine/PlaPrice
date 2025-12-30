"""
테스트: ShopStore (상점 저장소)

TDD에 따라 구현 전 테스트 먼저 작성.
"""

import json
import pytest
from pathlib import Path
import tempfile
import shutil


# 테스트 픽스처 경로
FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


class TestShopStore:
    """ShopStore 테스트"""

    @pytest.fixture
    def temp_dir(self):
        """임시 디렉토리 생성"""
        temp = tempfile.mkdtemp()
        yield Path(temp)
        shutil.rmtree(temp)

    @pytest.fixture
    def sample_shop_data(self):
        """테스트용 상점 데이터"""
        from src.models.shop import Shop, ShopSelectors

        selectors = ShopSelectors(
            product_container=".product",
            product_name=".name",
            product_price=".price",
        )

        return Shop(
            name="테스트 상점",
            base_url="https://example.com",
            search_url_template="https://example.com/search?q={keyword}",
            selectors=selectors,
        )

    def test_shop_store_생성(self, temp_dir):
        """ShopStore 인스턴스 생성"""
        from src.storage.shop_store import ShopStore

        store = ShopStore(config_dir=temp_dir)
        assert store is not None
        assert store.config_dir == temp_dir

    def test_shop_store_기본_경로(self):
        """설정 디렉토리 미지정 시 기본 경로 사용"""
        from src.storage.shop_store import ShopStore

        store = ShopStore()
        assert ".plaprice" in str(store.config_dir)

    def test_shop_추가(self, temp_dir, sample_shop_data):
        """상점 추가"""
        from src.storage.shop_store import ShopStore

        store = ShopStore(config_dir=temp_dir)
        store.add(sample_shop_data)

        assert len(store.list_all()) == 1
        assert store.list_all()[0].name == "테스트 상점"

    def test_shop_조회_by_id(self, temp_dir, sample_shop_data):
        """ID로 상점 조회"""
        from src.storage.shop_store import ShopStore

        store = ShopStore(config_dir=temp_dir)
        store.add(sample_shop_data)

        shop = store.get(sample_shop_data.id)
        assert shop is not None
        assert shop.name == "테스트 상점"

    def test_shop_조회_없는_id(self, temp_dir):
        """존재하지 않는 ID 조회 시 None 반환"""
        from src.storage.shop_store import ShopStore

        store = ShopStore(config_dir=temp_dir)
        shop = store.get("non-existent-id")
        assert shop is None

    def test_shop_삭제(self, temp_dir, sample_shop_data):
        """상점 삭제"""
        from src.storage.shop_store import ShopStore

        store = ShopStore(config_dir=temp_dir)
        store.add(sample_shop_data)
        
        result = store.remove(sample_shop_data.id)
        
        assert result is True
        assert len(store.list_all()) == 0

    def test_shop_삭제_없는_id(self, temp_dir):
        """존재하지 않는 상점 삭제 시 False 반환"""
        from src.storage.shop_store import ShopStore

        store = ShopStore(config_dir=temp_dir)
        result = store.remove("non-existent-id")
        assert result is False

    def test_shop_활성화_목록(self, temp_dir, sample_shop_data):
        """활성화된 상점만 조회"""
        from src.storage.shop_store import ShopStore
        from src.models.shop import Shop, ShopSelectors

        store = ShopStore(config_dir=temp_dir)
        
        # 활성 상점 추가
        store.add(sample_shop_data)
        
        # 비활성 상점 추가
        selectors = ShopSelectors(
            product_container=".item",
            product_name=".title",
            product_price=".cost",
        )
        disabled_shop = Shop(
            name="비활성 상점",
            base_url="https://disabled.com",
            search_url_template="https://disabled.com/search?q={keyword}",
            selectors=selectors,
            enabled=False,
        )
        store.add(disabled_shop)

        active_shops = store.list_active()
        
        assert len(active_shops) == 1
        assert active_shops[0].name == "테스트 상점"

    def test_shop_활성화_토글(self, temp_dir, sample_shop_data):
        """상점 활성화/비활성화 토글"""
        from src.storage.shop_store import ShopStore

        store = ShopStore(config_dir=temp_dir)
        store.add(sample_shop_data)

        # 비활성화
        store.set_enabled(sample_shop_data.id, False)
        shop = store.get(sample_shop_data.id)
        assert shop.enabled is False

        # 다시 활성화
        store.set_enabled(sample_shop_data.id, True)
        shop = store.get(sample_shop_data.id)
        assert shop.enabled is True

    def test_json_저장(self, temp_dir, sample_shop_data):
        """상점 목록을 JSON 파일로 저장"""
        from src.storage.shop_store import ShopStore

        store = ShopStore(config_dir=temp_dir)
        store.add(sample_shop_data)
        store.save()

        # 파일 존재 확인
        json_path = temp_dir / "shops.json"
        assert json_path.exists()

        # 내용 확인
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        assert "shops" in data
        assert len(data["shops"]) == 1

    def test_json_로드(self, temp_dir):
        """JSON 파일에서 상점 목록 로드"""
        from src.storage.shop_store import ShopStore

        # 샘플 JSON 복사
        sample_path = FIXTURES_DIR / "sample_shop.json"
        target_path = temp_dir / "shops.json"
        shutil.copy(sample_path, target_path)

        store = ShopStore(config_dir=temp_dir)
        store.load()

        assert len(store.list_all()) == 2
        assert store.get("test-shop-001") is not None
        assert store.get("test-shop-001").name == "테스트 상점 1"

    def test_자동_저장(self, temp_dir, sample_shop_data):
        """add/remove 시 자동 저장"""
        from src.storage.shop_store import ShopStore

        store = ShopStore(config_dir=temp_dir, auto_save=True)
        store.add(sample_shop_data)

        # 파일이 자동 저장되었는지 확인
        json_path = temp_dir / "shops.json"
        assert json_path.exists()

    def test_설정_디렉토리_자동_생성(self):
        """설정 디렉토리가 없으면 자동 생성"""
        from src.storage.shop_store import ShopStore
        import tempfile

        # 존재하지 않는 디렉토리 경로
        non_existent = Path(tempfile.gettempdir()) / "plaprice_test_new_dir"
        if non_existent.exists():
            shutil.rmtree(non_existent)

        try:
            store = ShopStore(config_dir=non_existent)
            assert non_existent.exists()
        finally:
            if non_existent.exists():
                shutil.rmtree(non_existent)

    def test_중복_id_추가_방지(self, temp_dir, sample_shop_data):
        """동일 ID 상점 중복 추가 방지"""
        from src.storage.shop_store import ShopStore, ShopStoreError

        store = ShopStore(config_dir=temp_dir)
        store.add(sample_shop_data)

        with pytest.raises(ShopStoreError):
            store.add(sample_shop_data)

    def test_상점_업데이트(self, temp_dir, sample_shop_data):
        """상점 정보 업데이트"""
        from src.storage.shop_store import ShopStore

        store = ShopStore(config_dir=temp_dir)
        store.add(sample_shop_data)

        # 이름 변경
        sample_shop_data.name = "수정된 상점"
        store.update(sample_shop_data)

        shop = store.get(sample_shop_data.id)
        assert shop.name == "수정된 상점"
