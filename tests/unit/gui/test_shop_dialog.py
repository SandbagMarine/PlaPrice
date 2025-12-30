# -*- coding: utf-8 -*-
"""
ShopEditDialog 테스트

상점 추가/수정 대화상자 테스트.
"""

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLineEdit, QPushButton, QDialogButtonBox


class TestShopEditDialog:
    """ShopEditDialog 클래스 테스트"""

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

    def test_has_input_fields(self, qtbot):
        """입력 필드 존재 테스트"""
        from src.gui.shop_dialog import ShopEditDialog
        
        dialog = ShopEditDialog()
        qtbot.addWidget(dialog)
        
        assert hasattr(dialog, 'name_input')
        assert hasattr(dialog, 'url_input')
        assert hasattr(dialog, 'search_template_input')
        
        assert isinstance(dialog.name_input, QLineEdit)
        assert isinstance(dialog.url_input, QLineEdit)
        assert isinstance(dialog.search_template_input, QLineEdit)

    def test_has_selector_fields(self, qtbot):
        """셀렉터 입력 필드 존재 테스트"""
        from src.gui.shop_dialog import ShopEditDialog
        
        dialog = ShopEditDialog()
        qtbot.addWidget(dialog)
        
        assert hasattr(dialog, 'product_container_selector_input')
        assert hasattr(dialog, 'name_selector_input')
        assert hasattr(dialog, 'price_selector_input')

    def test_dialog_title_new(self, qtbot):
        """새 상점 추가 시 대화상자 제목"""
        from src.gui.shop_dialog import ShopEditDialog
        
        dialog = ShopEditDialog()
        qtbot.addWidget(dialog)
        
        assert "추가" in dialog.windowTitle() or "새" in dialog.windowTitle()

    def test_dialog_title_edit(self, qtbot, sample_shop):
        """상점 수정 시 대화상자 제목"""
        from src.gui.shop_dialog import ShopEditDialog
        
        dialog = ShopEditDialog(shop=sample_shop)
        qtbot.addWidget(dialog)
        
        assert "수정" in dialog.windowTitle() or "편집" in dialog.windowTitle()

    def test_prefill_on_edit(self, qtbot, sample_shop):
        """수정 시 기존 값 채우기"""
        from src.gui.shop_dialog import ShopEditDialog
        
        dialog = ShopEditDialog(shop=sample_shop)
        qtbot.addWidget(dialog)
        
        assert dialog.name_input.text() == "테스트 상점"
        assert dialog.url_input.text() == "https://test.com"
        assert "{keyword}" in dialog.search_template_input.text()

    def test_validate_empty_name(self, qtbot):
        """빈 이름 검증 실패"""
        from src.gui.shop_dialog import ShopEditDialog
        
        dialog = ShopEditDialog()
        qtbot.addWidget(dialog)
        
        dialog.name_input.setText("")
        dialog.url_input.setText("https://test.com")
        dialog.search_template_input.setText("https://test.com/search?q={keyword}")
        
        is_valid, error = dialog.validate()
        assert not is_valid
        assert "이름" in error or "상점명" in error

    def test_validate_empty_url(self, qtbot):
        """빈 URL 검증 실패"""
        from src.gui.shop_dialog import ShopEditDialog
        
        dialog = ShopEditDialog()
        qtbot.addWidget(dialog)
        
        dialog.name_input.setText("테스트")
        dialog.url_input.setText("")
        dialog.search_template_input.setText("https://test.com/search?q={keyword}")
        
        is_valid, error = dialog.validate()
        assert not is_valid
        assert "URL" in error

    def test_validate_missing_keyword_placeholder(self, qtbot):
        """검색 템플릿에 {keyword} 없으면 검증 실패"""
        from src.gui.shop_dialog import ShopEditDialog
        
        dialog = ShopEditDialog()
        qtbot.addWidget(dialog)
        
        dialog.name_input.setText("테스트")
        dialog.url_input.setText("https://test.com")
        dialog.search_template_input.setText("https://test.com/search")  # {keyword} 없음
        
        is_valid, error = dialog.validate()
        assert not is_valid
        assert "{keyword}" in error

    def test_validate_success(self, qtbot):
        """유효한 입력 검증 성공"""
        from src.gui.shop_dialog import ShopEditDialog
        
        dialog = ShopEditDialog()
        qtbot.addWidget(dialog)
        
        dialog.name_input.setText("테스트 상점")
        dialog.url_input.setText("https://test.com")
        dialog.search_template_input.setText("https://test.com/search?q={keyword}")
        dialog.product_container_selector_input.setText(".products")
        dialog.name_selector_input.setText(".name")
        dialog.price_selector_input.setText(".price")
        
        is_valid, error = dialog.validate()
        assert is_valid
        assert error == ""

    def test_get_shop_data(self, qtbot):
        """상점 데이터 추출 테스트"""
        from src.gui.shop_dialog import ShopEditDialog
        
        dialog = ShopEditDialog()
        qtbot.addWidget(dialog)
        
        dialog.name_input.setText("테스트 상점")
        dialog.url_input.setText("https://test.com")
        dialog.search_template_input.setText("https://test.com/search?q={keyword}")
        dialog.product_container_selector_input.setText(".products")
        dialog.name_selector_input.setText(".name")
        dialog.price_selector_input.setText(".price")
        
        data = dialog.get_shop_data()
        
        assert data["name"] == "테스트 상점"
        assert data["base_url"] == "https://test.com"
        assert data["search_url_template"] == "https://test.com/search?q={keyword}"
        assert data["selectors"]["product_container"] == ".products"
        assert data["selectors"]["product_name"] == ".name"
        assert data["selectors"]["product_price"] == ".price"
