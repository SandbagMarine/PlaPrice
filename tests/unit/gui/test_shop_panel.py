# -*- coding: utf-8 -*-
"""
ShopListView 테스트

상점 목록 사이드바 패널 테스트.
"""

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTableWidget, QPushButton, QCheckBox


class TestShopListView:
    """ShopListView 클래스 테스트"""

    @pytest.fixture
    def mock_shop_store(self, mocker, tmp_path):
        """Mock ShopStore 생성"""
        from src.storage.shop_store import ShopStore
        store = ShopStore(config_dir=tmp_path)
        return store

    @pytest.fixture
    def sample_shop(self):
        """샘플 상점 데이터"""
        from src.models.shop import Shop, ShopSelectors
        return Shop(
            name="테스트 상점",
            base_url="https://test.com",
            search_url_template="https://test.com/search?q={keyword}",
            selectors=ShopSelectors(
                product_container=".products",
                product_name=".name",
                product_price=".price"
            )
        )

    def test_has_table(self, qtbot, mock_shop_store):
        """테이블 위젯 존재 테스트"""
        from src.gui.shop_panel import ShopListView
        
        panel = ShopListView(mock_shop_store)
        qtbot.addWidget(panel)
        
        assert hasattr(panel, 'table')
        assert isinstance(panel.table, QTableWidget)

    def test_table_columns(self, qtbot, mock_shop_store):
        """테이블 컬럼 테스트"""
        from src.gui.shop_panel import ShopListView
        
        panel = ShopListView(mock_shop_store)
        qtbot.addWidget(panel)
        
        # 컬럼: 선택, 상점명, URL
        assert panel.table.columnCount() == 3
        
        headers = [
            panel.table.horizontalHeaderItem(i).text()
            for i in range(panel.table.columnCount())
        ]
        assert "선택" in headers
        assert "상점명" in headers
        assert "URL" in headers

    def test_has_buttons(self, qtbot, mock_shop_store):
        """버튼 존재 테스트"""
        from src.gui.shop_panel import ShopListView
        
        panel = ShopListView(mock_shop_store)
        qtbot.addWidget(panel)
        
        assert hasattr(panel, 'add_button')
        assert hasattr(panel, 'edit_button')
        assert hasattr(panel, 'delete_button')
        assert hasattr(panel, 'select_all_button')
        
        assert isinstance(panel.add_button, QPushButton)
        assert isinstance(panel.edit_button, QPushButton)
        assert isinstance(panel.delete_button, QPushButton)
        assert isinstance(panel.select_all_button, QPushButton)

    def test_display_shops(self, qtbot, mock_shop_store, sample_shop):
        """상점 목록 표시 테스트"""
        from src.gui.shop_panel import ShopListView
        
        # 상점 추가
        mock_shop_store.add(sample_shop)
        
        panel = ShopListView(mock_shop_store)
        qtbot.addWidget(panel)
        
        # 테이블에 1개 행 있어야 함
        assert panel.table.rowCount() == 1
        
        # 상점명 확인
        name_item = panel.table.item(0, 1)
        assert name_item.text() == "테스트 상점"

    def test_checkbox_in_first_column(self, qtbot, mock_shop_store, sample_shop):
        """첫 번째 컬럼에 체크박스 존재 테스트"""
        from src.gui.shop_panel import ShopListView
        
        mock_shop_store.add(sample_shop)
        
        panel = ShopListView(mock_shop_store)
        qtbot.addWidget(panel)
        
        # 첫 번째 컬럼에 체크박스 위젯
        checkbox_widget = panel.table.cellWidget(0, 0)
        assert checkbox_widget is not None
        # 체크박스 찾기
        checkbox = checkbox_widget.findChild(QCheckBox)
        assert checkbox is not None
        assert checkbox.isChecked()  # 기본값은 선택됨

    def test_get_selected_shops(self, qtbot, mock_shop_store, sample_shop):
        """선택된 상점 목록 반환 테스트"""
        from src.gui.shop_panel import ShopListView
        
        mock_shop_store.add(sample_shop)
        
        panel = ShopListView(mock_shop_store)
        qtbot.addWidget(panel)
        
        # 기본적으로 모두 선택됨
        selected = panel.get_selected_shops()
        assert len(selected) == 1
        assert selected[0].name == "테스트 상점"

    def test_select_all(self, qtbot, mock_shop_store, sample_shop):
        """전체 선택 테스트"""
        from src.gui.shop_panel import ShopListView
        from src.models.shop import Shop, ShopSelectors
        
        # 여러 상점 추가
        mock_shop_store.add(sample_shop)
        shop2 = Shop(
            name="상점2",
            base_url="https://test2.com",
            search_url_template="https://test2.com/search?q={keyword}",
            selectors=ShopSelectors(
                product_container=".products",
                product_name=".name",
                product_price=".price"
            )
        )
        mock_shop_store.add(shop2)
        
        panel = ShopListView(mock_shop_store)
        qtbot.addWidget(panel)
        
        # 전체 선택
        panel.select_all()
        
        selected = panel.get_selected_shops()
        assert len(selected) == 2

    def test_deselect_all(self, qtbot, mock_shop_store, sample_shop):
        """전체 선택 해제 테스트"""
        from src.gui.shop_panel import ShopListView
        
        mock_shop_store.add(sample_shop)
        
        panel = ShopListView(mock_shop_store)
        qtbot.addWidget(panel)
        
        # 전체 선택 해제
        panel.deselect_all()
        
        selected = panel.get_selected_shops()
        assert len(selected) == 0

    def test_refresh(self, qtbot, mock_shop_store, sample_shop):
        """목록 새로고침 테스트"""
        from src.gui.shop_panel import ShopListView
        from src.models.shop import Shop, ShopSelectors
        
        panel = ShopListView(mock_shop_store)
        qtbot.addWidget(panel)
        
        # 초기: 0개
        assert panel.table.rowCount() == 0
        
        # 상점 추가 후 새로고침
        mock_shop_store.add(sample_shop)
        panel.refresh()
        
        # 1개 표시
        assert panel.table.rowCount() == 1
