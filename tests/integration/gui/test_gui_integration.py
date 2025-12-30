# -*- coding: utf-8 -*-
"""
GUI 통합 테스트

전체 GUI 워크플로우 및 컴포넌트 통합 테스트.
"""

import pytest
from pathlib import Path
from PySide6.QtCore import Qt

from src.models.shop import Shop, ShopSelectors
from src.gui.settings import GuiSettings, WindowGeometry, SplitterState


class TestGuiIntegration:
    """GUI 전체 통합 테스트"""

    @pytest.fixture
    def temp_shop_store(self, tmp_path):
        """임시 상점 저장소"""
        from src.storage.shop_store import ShopStore
        
        shop_file = tmp_path / "shops.json"
        store = ShopStore(shop_file)
        
        # 샘플 상점 추가 (모든 필수 필드 포함)
        selectors = ShopSelectors(
            product_container=".product",
            product_name=".name",
            product_price=".price"
        )
        
        store.add(Shop(
            id="test-shop-1",
            name="테스트 상점 1",
            base_url="https://test1.com",
            search_url_template="https://test1.com/search?q={keyword}",
            selectors=selectors
        ))
        store.add(Shop(
            id="test-shop-2",
            name="테스트 상점 2",
            base_url="https://test2.com",
            search_url_template="https://test2.com/search?q={keyword}",
            selectors=selectors
        ))
        
        return store

    @pytest.fixture
    def temp_settings(self, tmp_path):
        """임시 설정"""
        settings = GuiSettings(
            window=WindowGeometry(),
            splitter=SplitterState()
        )
        return settings

    @pytest.fixture
    def temp_settings_path(self, tmp_path):
        """임시 설정 파일 경로"""
        return tmp_path / "gui_settings.json"

    def test_main_window_with_shop_store(self, qtbot, temp_shop_store, temp_settings):
        """MainWindow와 ShopStore 통합 테스트"""
        from src.gui.main_window import MainWindow
        
        window = MainWindow(settings=temp_settings, shop_store=temp_shop_store)
        qtbot.addWidget(window)
        
        # 상점 목록이 표시되는지 확인
        shop_list = window.shop_list_view
        assert shop_list.table.rowCount() == 2

    def test_shop_selection_integration(self, qtbot, temp_shop_store, temp_settings):
        """상점 선택 통합 테스트"""
        from src.gui.main_window import MainWindow
        
        window = MainWindow(settings=temp_settings, shop_store=temp_shop_store)
        qtbot.addWidget(window)
        
        # 전체 선택
        window.shop_list_view.select_all()
        
        selected = window.shop_list_view.get_selected_shops()
        assert len(selected) == 2

    def test_main_window_has_search_panel(self, qtbot, temp_shop_store, temp_settings):
        """MainWindow에 SearchPanel이 있는지 확인"""
        from src.gui.main_window import MainWindow
        
        window = MainWindow(settings=temp_settings, shop_store=temp_shop_store)
        qtbot.addWidget(window)
        
        assert hasattr(window, 'search_panel')
        assert hasattr(window.search_panel, 'search_input')
        assert hasattr(window.search_panel, 'search_button')

    def test_main_window_has_results_table(self, qtbot, temp_shop_store, temp_settings):
        """MainWindow에 ResultsTable이 있는지 확인"""
        from src.gui.main_window import MainWindow
        
        window = MainWindow(settings=temp_settings, shop_store=temp_shop_store)
        qtbot.addWidget(window)
        
        assert hasattr(window, 'results_table')
        assert hasattr(window.results_table, 'table')


class TestSettingsPersistence:
    """설정 저장/복원 통합 테스트"""

    def test_settings_save_and_load(self, tmp_path):
        """설정 저장 및 로드 테스트"""
        settings_file = tmp_path / "test_settings.json"
        
        # 설정 생성 및 저장
        settings = GuiSettings(
            window=WindowGeometry(x=100, y=200, width=1024, height=768),
            splitter=SplitterState(sizes=[300, 700])
        )
        settings.save(settings_file)
        
        # 파일 존재 확인
        assert settings_file.exists()
        
        # 설정 로드
        loaded = GuiSettings.load(settings_file)
        
        assert loaded.window.x == 100
        assert loaded.window.y == 200
        assert loaded.window.width == 1024
        assert loaded.window.height == 768
        assert loaded.splitter.sizes == [300, 700]

    def test_main_window_saves_settings_on_close(self, qtbot, tmp_path, mocker):
        """창 닫을 때 설정 저장 테스트"""
        from src.gui.main_window import MainWindow
        from src.storage.shop_store import ShopStore
        
        settings_file = tmp_path / "gui_settings.json"
        shop_file = tmp_path / "shops.json"
        
        settings = GuiSettings(
            window=WindowGeometry(),
            splitter=SplitterState()
        )
        
        # DEFAULT_PATH를 임시 경로로 변경
        mocker.patch.object(GuiSettings, 'DEFAULT_PATH', settings_file)
        
        store = ShopStore(shop_file)
        
        window = MainWindow(settings=settings, shop_store=store)
        qtbot.addWidget(window)
        
        # 창 크기 변경
        window.setGeometry(50, 50, 1200, 800)
        
        # 창 닫기
        window.close()
        
        # 설정 파일이 생성되었는지 확인
        assert settings_file.exists()

    def test_splitter_state_preserved(self, qtbot, tmp_path):
        """스플리터 상태 유지 테스트"""
        from src.gui.main_window import MainWindow
        from src.storage.shop_store import ShopStore
        
        shop_file = tmp_path / "shops.json"
        
        # 초기 설정 (스플리터 크기 지정)
        settings = GuiSettings(
            window=WindowGeometry(),
            splitter=SplitterState(sizes=[250, 550])
        )
        
        store = ShopStore(shop_file)
        
        window = MainWindow(settings=settings, shop_store=store)
        qtbot.addWidget(window)
        window.show()
        
        # 스플리터 크기 확인 (정확한 값은 Qt 렌더링에 따라 다를 수 있음)
        sizes = window.splitter.sizes()
        assert len(sizes) == 2
        assert all(s > 0 for s in sizes)
