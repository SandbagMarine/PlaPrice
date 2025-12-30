"""
테스트: CLI 인터페이스

TDD에 따라 구현 전 테스트 먼저 작성.
"""

import pytest
from unittest.mock import MagicMock, patch
from io import StringIO
import sys


class TestCLIParsing:
    """CLI 명령어 파싱 테스트"""

    def test_search_명령어_파싱(self):
        """search 명령어 파싱"""
        from src.cli.main import parse_args

        args = parse_args(["search", "마우스"])
        
        assert args.command == "search"
        assert args.keyword == "마우스"

    def test_search_상점_지정(self):
        """search 명령어에 상점 ID 지정"""
        from src.cli.main import parse_args

        args = parse_args(["search", "키보드", "--shop", "shop-1"])
        
        assert args.command == "search"
        assert args.keyword == "키보드"
        assert args.shop == "shop-1"

    def test_shop_list_명령어(self):
        """shop list 명령어 파싱"""
        from src.cli.main import parse_args

        args = parse_args(["shop", "list"])
        
        assert args.command == "shop"
        assert args.shop_command == "list"

    def test_shop_add_명령어(self):
        """shop add 명령어 파싱"""
        from src.cli.main import parse_args

        args = parse_args([
            "shop", "add",
            "--name", "테스트상점",
            "--url", "https://example.com",
            "--search-template", "https://example.com/search?q={keyword}",
            "--container", ".product",
            "--name-selector", ".title",
            "--price-selector", ".price",
        ])
        
        assert args.command == "shop"
        assert args.shop_command == "add"
        assert args.name == "테스트상점"

    def test_shop_remove_명령어(self):
        """shop remove 명령어 파싱"""
        from src.cli.main import parse_args

        args = parse_args(["shop", "remove", "shop-id-123"])
        
        assert args.command == "shop"
        assert args.shop_command == "remove"
        assert args.shop_id == "shop-id-123"

    def test_shop_show_명령어(self):
        """shop show 명령어 파싱"""
        from src.cli.main import parse_args

        args = parse_args(["shop", "show", "shop-id-123"])
        
        assert args.command == "shop"
        assert args.shop_command == "show"
        assert args.shop_id == "shop-id-123"

    def test_shop_enable_disable_명령어(self):
        """shop enable/disable 명령어 파싱"""
        from src.cli.main import parse_args

        args_enable = parse_args(["shop", "enable", "shop-id-123"])
        assert args_enable.shop_command == "enable"

        args_disable = parse_args(["shop", "disable", "shop-id-123"])
        assert args_disable.shop_command == "disable"

    def test_config_path_명령어(self):
        """config path 명령어 파싱"""
        from src.cli.main import parse_args

        args = parse_args(["config", "path"])
        
        assert args.command == "config"
        assert args.config_command == "path"

    def test_test_명령어(self):
        """test 명령어 파싱"""
        from src.cli.main import parse_args

        args = parse_args(["test", "shop-id-123"])
        
        assert args.command == "test"
        assert args.shop_id == "shop-id-123"

    def test_json_출력_옵션(self):
        """--json 전역 옵션"""
        from src.cli.main import parse_args

        args = parse_args(["--json", "shop", "list"])
        
        assert args.json is True

    def test_quiet_옵션(self):
        """--quiet 전역 옵션"""
        from src.cli.main import parse_args

        args = parse_args(["--quiet", "search", "마우스"])
        
        assert args.quiet is True


class TestCLIExecution:
    """CLI 실행 테스트"""

    def test_search_실행_빈_상점(self):
        """상점이 없을 때 search 실행"""
        from src.cli.main import run_search
        from src.storage.shop_store import ShopStore
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as temp_dir:
            store = ShopStore(config_dir=Path(temp_dir))
            result = run_search("마우스", store=store)
            
            assert result == 0 or result is None  # 정상 종료

    def test_shop_list_실행(self):
        """shop list 실행"""
        from src.cli.main import run_shop_list
        from src.storage.shop_store import ShopStore
        from src.models.shop import Shop, ShopSelectors
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as temp_dir:
            store = ShopStore(config_dir=Path(temp_dir))
            
            # 상점 추가
            selectors = ShopSelectors(
                product_container=".product",
                product_name=".name",
                product_price=".price",
            )
            shop = Shop(
                name="테스트",
                base_url="https://example.com",
                search_url_template="https://example.com/search?q={keyword}",
                selectors=selectors,
            )
            store.add(shop)
            
            result = run_shop_list(store=store)
            assert result == 0 or result is None

    def test_shop_add_실행(self):
        """shop add 실행"""
        from src.cli.main import run_shop_add
        from src.storage.shop_store import ShopStore
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as temp_dir:
            store = ShopStore(config_dir=Path(temp_dir))
            
            result = run_shop_add(
                name="새상점",
                url="https://newshop.com",
                search_template="https://newshop.com/search?q={keyword}",
                container=".item",
                name_selector=".title",
                price_selector=".cost",
                store=store,
            )
            
            assert result == 0 or result is None
            assert len(store.list_all()) == 1

    def test_shop_remove_실행(self):
        """shop remove 실행"""
        from src.cli.main import run_shop_remove
        from src.storage.shop_store import ShopStore
        from src.models.shop import Shop, ShopSelectors
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as temp_dir:
            store = ShopStore(config_dir=Path(temp_dir))
            
            # 상점 추가
            selectors = ShopSelectors(
                product_container=".product",
                product_name=".name",
                product_price=".price",
            )
            shop = Shop(
                name="삭제할상점",
                base_url="https://example.com",
                search_url_template="https://example.com/search?q={keyword}",
                selectors=selectors,
            )
            store.add(shop)
            
            result = run_shop_remove(shop.id, store=store)
            
            assert result == 0 or result is None
            assert len(store.list_all()) == 0
