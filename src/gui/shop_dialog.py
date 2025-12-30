# -*- coding: utf-8 -*-
"""
상점 편집 대화상자

상점 추가/수정을 위한 입력 폼.
"""

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QDialogButtonBox,
    QGroupBox,
    QMessageBox,
)

from src.models.shop import Shop, ShopSelectors


class ShopEditDialog(QDialog):
    """상점 추가/수정 대화상자"""
    
    def __init__(self, shop: Shop | None = None, parent=None):
        """
        대화상자 초기화
        
        Args:
            shop: 수정할 상점 (None이면 새 상점 추가)
            parent: 부모 위젯
        """
        super().__init__(parent)
        
        self.shop = shop
        self.is_edit_mode = shop is not None
        
        self._setup_ui()
        
        if self.is_edit_mode:
            self._prefill_data()
    
    def _setup_ui(self) -> None:
        """UI 구성요소 설정"""
        # 제목 설정
        if self.is_edit_mode:
            self.setWindowTitle("상점 수정")
        else:
            self.setWindowTitle("새 상점 추가")
        
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout(self)
        
        # 기본 정보 그룹
        basic_group = QGroupBox("기본 정보")
        basic_layout = QFormLayout(basic_group)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("상점 이름 (필수)")
        basic_layout.addRow("상점명:", self.name_input)
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://example.com (필수)")
        basic_layout.addRow("기본 URL:", self.url_input)
        
        self.search_template_input = QLineEdit()
        self.search_template_input.setPlaceholderText("https://example.com/search?q={keyword}")
        basic_layout.addRow("검색 URL 템플릿:", self.search_template_input)
        
        layout.addWidget(basic_group)
        
        # CSS 셀렉터 그룹
        selector_group = QGroupBox("CSS 셀렉터")
        selector_layout = QFormLayout(selector_group)
        
        self.product_container_selector_input = QLineEdit()
        self.product_container_selector_input.setPlaceholderText(".product-item")
        selector_layout.addRow("상품 목록:", self.product_container_selector_input)
        
        self.name_selector_input = QLineEdit()
        self.name_selector_input.setPlaceholderText(".product-name")
        selector_layout.addRow("상품명:", self.name_selector_input)
        
        self.price_selector_input = QLineEdit()
        self.price_selector_input.setPlaceholderText(".product-price")
        selector_layout.addRow("가격:", self.price_selector_input)
        
        self.stock_selector_input = QLineEdit()
        self.stock_selector_input.setPlaceholderText(".stock-status (선택)")
        selector_layout.addRow("재고 상태:", self.stock_selector_input)
        
        self.link_selector_input = QLineEdit()
        self.link_selector_input.setPlaceholderText("a (선택)")
        selector_layout.addRow("상품 링크:", self.link_selector_input)
        
        layout.addWidget(selector_group)
        
        # 버튼
        button_box = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self._on_save)
        button_box.rejected.connect(self.reject)
        
        layout.addWidget(button_box)
    
    def _prefill_data(self) -> None:
        """수정 모드일 때 기존 데이터로 채우기"""
        if not self.shop:
            return
        
        self.name_input.setText(self.shop.name)
        self.url_input.setText(self.shop.base_url)
        self.search_template_input.setText(self.shop.search_url_template)
        
        selectors = self.shop.selectors
        self.product_container_selector_input.setText(selectors.product_container)
        self.name_selector_input.setText(selectors.product_name)
        self.price_selector_input.setText(selectors.product_price)
        
        if selectors.stock_status:
            self.stock_selector_input.setText(selectors.stock_status)
        if selectors.product_link:
            self.link_selector_input.setText(selectors.product_link)
    
    def validate(self) -> tuple[bool, str]:
        """
        입력값 검증
        
        Returns:
            (성공여부, 에러메시지)
        """
        name = self.name_input.text().strip()
        url = self.url_input.text().strip()
        search_template = self.search_template_input.text().strip()
        
        if not name:
            return False, "상점명을 입력하세요."
        
        if not url:
            return False, "URL을 입력하세요."
        
        if not search_template:
            return False, "검색 URL 템플릿을 입력하세요."
        
        if "{keyword}" not in search_template:
            return False, "검색 URL 템플릿에 {keyword}를 포함해야 합니다."
        
        return True, ""
    
    def get_shop_data(self) -> dict:
        """
        입력된 상점 데이터 반환
        
        Returns:
            상점 데이터 딕셔너리
        """
        selectors = {
            "product_container": self.product_container_selector_input.text().strip(),
            "product_name": self.name_selector_input.text().strip(),
            "product_price": self.price_selector_input.text().strip(),
        }
        
        stock_selector = self.stock_selector_input.text().strip()
        if stock_selector:
            selectors["stock_status"] = stock_selector
        
        link_selector = self.link_selector_input.text().strip()
        if link_selector:
            selectors["product_link"] = link_selector
        
        data = {
            "name": self.name_input.text().strip(),
            "base_url": self.url_input.text().strip(),
            "search_url_template": self.search_template_input.text().strip(),
            "selectors": selectors,
        }
        
        # 수정 모드일 때 ID 유지
        if self.shop:
            data["id"] = self.shop.id
        
        return data
    
    def _on_save(self) -> None:
        """저장 버튼 클릭"""
        is_valid, error = self.validate()
        
        if not is_valid:
            QMessageBox.warning(self, "입력 오류", error)
            return
        
        self.accept()
