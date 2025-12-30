# -*- coding: utf-8 -*-
"""
상점 목록 사이드바 패널

상점 목록 표시, 체크박스 선택, CRUD 버튼을 제공한다.
"""

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QCheckBox,
    QHeaderView,
    QMessageBox,
)

from src.models.shop import Shop
from src.storage.shop_store import ShopStore


class ShopListView(QWidget):
    """상점 목록 사이드바 패널"""
    
    # Qt 시그널
    shop_selected = Signal(object)  # Shop
    selection_changed = Signal(list)  # list[str] - shop_ids
    shop_added = Signal(object)  # Shop
    shop_updated = Signal(object)  # Shop
    shop_deleted = Signal(str)  # shop_id
    
    def __init__(self, shop_store: ShopStore, parent: QWidget | None = None):
        """
        상점 목록 패널 초기화
        
        Args:
            shop_store: 상점 저장소
            parent: 부모 위젯
        """
        super().__init__(parent)
        
        self.shop_store = shop_store
        self._checkboxes: dict[str, QCheckBox] = {}  # shop_id -> checkbox
        
        self._setup_ui()
        self._connect_signals()
        self.refresh()
    
    def _setup_ui(self) -> None:
        """UI 구성요소 설정"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # 테이블
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["선택", "상점명", "URL"])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # 컬럼 크기 조정
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.resizeSection(0, 40)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        
        layout.addWidget(self.table)
        
        # 버튼 레이아웃
        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton("추가")
        self.edit_button = QPushButton("수정")
        self.delete_button = QPushButton("삭제")
        self.select_all_button = QPushButton("전체 선택")
        
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.select_all_button)
        
        layout.addLayout(button_layout)
    
    def _connect_signals(self) -> None:
        """시그널 연결"""
        self.add_button.clicked.connect(self._on_add_clicked)
        self.edit_button.clicked.connect(self._on_edit_clicked)
        self.delete_button.clicked.connect(self._on_delete_clicked)
        self.select_all_button.clicked.connect(self._toggle_select_all)
        self.table.cellDoubleClicked.connect(self._on_row_double_clicked)
    
    def refresh(self) -> None:
        """상점 목록 새로고침"""
        self.table.setRowCount(0)
        self._checkboxes.clear()
        
        shops = self.shop_store.list_all()
        
        for shop in shops:
            self._add_shop_row(shop)
    
    def _add_shop_row(self, shop: Shop) -> None:
        """테이블에 상점 행 추가"""
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        # 체크박스 (가운데 정렬을 위한 컨테이너 위젯)
        checkbox_container = QWidget()
        checkbox_layout = QHBoxLayout(checkbox_container)
        checkbox_layout.setContentsMargins(0, 0, 0, 0)
        checkbox_layout.setAlignment(Qt.AlignCenter)
        
        checkbox = QCheckBox()
        checkbox.setChecked(True)  # 기본값: 선택됨
        checkbox.stateChanged.connect(lambda: self._on_checkbox_changed(shop.id))
        checkbox_layout.addWidget(checkbox)
        
        self.table.setCellWidget(row, 0, checkbox_container)
        self._checkboxes[shop.id] = checkbox
        
        # 상점명
        name_item = QTableWidgetItem(shop.name)
        name_item.setData(Qt.UserRole, shop.id)  # ID 저장
        self.table.setItem(row, 1, name_item)
        
        # URL
        url_item = QTableWidgetItem(shop.base_url)
        self.table.setItem(row, 2, url_item)
    
    def get_selected_shops(self) -> list[Shop]:
        """체크박스가 선택된 상점 목록 반환"""
        selected = []
        for shop_id, checkbox in self._checkboxes.items():
            if checkbox.isChecked():
                shop = self.shop_store.get(shop_id)
                if shop:
                    selected.append(shop)
        return selected
    
    def get_selected_shop_ids(self) -> list[str]:
        """체크박스가 선택된 상점 ID 목록 반환"""
        return [
            shop_id for shop_id, checkbox in self._checkboxes.items()
            if checkbox.isChecked()
        ]
    
    def select_all(self) -> None:
        """모든 상점 선택"""
        for checkbox in self._checkboxes.values():
            checkbox.setChecked(True)
    
    def deselect_all(self) -> None:
        """모든 상점 선택 해제"""
        for checkbox in self._checkboxes.values():
            checkbox.setChecked(False)
    
    def _toggle_select_all(self) -> None:
        """전체 선택/해제 토글"""
        # 모두 선택되어 있으면 해제, 아니면 선택
        all_selected = all(cb.isChecked() for cb in self._checkboxes.values())
        if all_selected:
            self.deselect_all()
            self.select_all_button.setText("전체 선택")
        else:
            self.select_all()
            self.select_all_button.setText("전체 해제")
    
    def _on_checkbox_changed(self, shop_id: str) -> None:
        """체크박스 상태 변경 시"""
        self.selection_changed.emit(self.get_selected_shop_ids())
    
    def _on_add_clicked(self) -> None:
        """추가 버튼 클릭"""
        from src.gui.shop_dialog import ShopEditDialog
        
        dialog = ShopEditDialog(parent=self)
        if dialog.exec():
            data = dialog.get_shop_data()
            shop = Shop(**data)
            self.shop_store.add(shop)
            self.refresh()
            self.shop_added.emit(shop)
    
    def _on_edit_clicked(self) -> None:
        """수정 버튼 클릭"""
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "알림", "수정할 상점을 선택하세요.")
            return
        
        shop_id = self.table.item(selected_row, 1).data(Qt.UserRole)
        shop = self.shop_store.get(shop_id)
        
        if not shop:
            return
        
        from src.gui.shop_dialog import ShopEditDialog
        
        dialog = ShopEditDialog(shop=shop, parent=self)
        if dialog.exec():
            data = dialog.get_shop_data()
            updated_shop = shop.model_copy(update=data)
            self.shop_store.update(updated_shop)
            self.refresh()
            self.shop_updated.emit(updated_shop)
    
    def _on_delete_clicked(self) -> None:
        """삭제 버튼 클릭"""
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "알림", "삭제할 상점을 선택하세요.")
            return
        
        shop_id = self.table.item(selected_row, 1).data(Qt.UserRole)
        shop = self.shop_store.get(shop_id)
        
        if not shop:
            return
        
        reply = QMessageBox.question(
            self,
            "삭제 확인",
            f"'{shop.name}' 상점을 삭제하시겠습니까?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.shop_store.delete(shop_id)
            self.refresh()
            self.shop_deleted.emit(shop_id)
    
    def _on_row_double_clicked(self, row: int, column: int) -> None:
        """행 더블클릭 시 수정 대화상자 열기"""
        if column > 0:  # 체크박스 컬럼 제외
            self._on_edit_clicked()
