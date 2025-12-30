# -*- coding: utf-8 -*-
"""
결과 테이블

검색 결과를 표시하는 테이블 위젯.
최저가 강조, URL 열기, CSV 내보내기 기능.
"""

import csv
import webbrowser
from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QLabel,
    QPushButton,
    QFileDialog,
    QApplication,
    QMessageBox,
)
from PySide6.QtGui import QColor, QBrush

from src.models.search import SearchResult, StockStatus


# 최저가 강조 색상 (녹색)
LOWEST_PRICE_COLOR = QColor(144, 238, 144)  # LightGreen


class ResultsTable(QWidget):
    """검색 결과 테이블"""
    
    # 시그널
    url_open_requested = Signal(str)  # url
    
    def __init__(self, parent=None):
        """ResultsTable 초기화"""
        super().__init__(parent)
        
        self._results: list[SearchResult] = []
        
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self) -> None:
        """UI 구성"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 상단 툴바
        toolbar = QHBoxLayout()
        
        self.count_label = QLabel("결과: 0개")
        toolbar.addWidget(self.count_label)
        
        toolbar.addStretch()
        
        # 내보내기 버튼들
        self.export_csv_button = QPushButton("CSV 저장")
        self.export_csv_button.setEnabled(False)
        toolbar.addWidget(self.export_csv_button)
        
        self.copy_button = QPushButton("복사")
        self.copy_button.setEnabled(False)
        toolbar.addWidget(self.copy_button)
        
        layout.addLayout(toolbar)
        
        # 결과 테이블
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "상점", "상품명", "가격", "재고", "URL"
        ])
        
        # 테이블 설정
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSortingEnabled(True)
        
        # 컬럼 크기 조정
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # 상점
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # 상품명
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # 가격
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # 재고
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # URL
        
        # URL 컬럼 숨김 (더블클릭으로 접근)
        self.table.setColumnHidden(4, True)
        
        layout.addWidget(self.table)
    
    def _connect_signals(self) -> None:
        """시그널 연결"""
        self.table.cellDoubleClicked.connect(self._on_cell_double_clicked)
        self.export_csv_button.clicked.connect(self._on_export_csv)
        self.copy_button.clicked.connect(self._on_copy_to_clipboard)
    
    def set_results(
        self,
        results: list[SearchResult],
        max_per_shop: Optional[int] = None
    ) -> None:
        """
        검색 결과 설정
        
        Args:
            results: 검색 결과 목록
            max_per_shop: 상점당 최대 표시 개수
        """
        self._results = results
        
        # 상점당 개수 제한
        if max_per_shop:
            results = self._limit_per_shop(results, max_per_shop)
        
        # 테이블 초기화
        self.table.setSortingEnabled(False)
        self.table.setRowCount(0)
        
        # 최저가 찾기
        lowest_price = self._find_lowest_price(results)
        
        # 결과 추가
        for result in results:
            self._add_result_row(result, lowest_price)
        
        # 정렬 활성화
        self.table.setSortingEnabled(True)
        
        # 상태 업데이트
        self._update_status(len(results))
    
    def _limit_per_shop(
        self,
        results: list[SearchResult],
        max_per_shop: int
    ) -> list[SearchResult]:
        """상점당 최대 개수 제한"""
        shop_counts: dict[str, int] = {}
        limited: list[SearchResult] = []
        
        for result in results:
            count = shop_counts.get(result.shop_name, 0)
            if count < max_per_shop:
                limited.append(result)
                shop_counts[result.shop_name] = count + 1
        
        return limited
    
    def _find_lowest_price(self, results: list[SearchResult]) -> Optional[int]:
        """재고 있는 상품 또는 예약상품 중 최저가 찾기"""
        available_prices = [
            r.price for r in results 
            if r.stock_status in (StockStatus.IN_STOCK, StockStatus.PRE_ORDER) and r.price is not None
        ]
        return min(available_prices) if available_prices else None
    
    def _add_result_row(
        self,
        result: SearchResult,
        lowest_price: Optional[int]
    ) -> None:
        """테이블에 결과 행 추가"""
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        # 재고 상태 확인 (재고있음 또는 예약상품은 구매 가능)
        is_available = result.stock_status in (StockStatus.IN_STOCK, StockStatus.PRE_ORDER)
        
        # 최저가 여부
        is_lowest = (
            lowest_price is not None 
            and result.price == lowest_price 
            and is_available
        )
        
        # 재고 상태 텍스트
        stock_text = {
            StockStatus.IN_STOCK: "재고있음",
            StockStatus.OUT_OF_STOCK: "품절",
            StockStatus.PRE_ORDER: "예약상품",
            StockStatus.UNKNOWN: "알수없음",
        }.get(result.stock_status, "알수없음")
        
        # 셀 생성
        items = [
            QTableWidgetItem(result.shop_name),
            QTableWidgetItem(result.product_name),
            QTableWidgetItem(self._format_price(result.price)),
            QTableWidgetItem(stock_text),
            QTableWidgetItem(result.product_url or ""),
        ]
        
        # 최저가 강조
        if is_lowest:
            for item in items:
                item.setBackground(QBrush(LOWEST_PRICE_COLOR))
        
        # 품절 상태 표시 (회색)
        if result.stock_status == StockStatus.OUT_OF_STOCK:
            for item in items:
                item.setForeground(QBrush(QColor(128, 128, 128)))  # Gray
        
        # 예약상품 표시 (파란색)
        elif result.stock_status == StockStatus.PRE_ORDER:
            for item in items:
                item.setForeground(QBrush(QColor(0, 128, 192)))  # Cyan
        
        # 셀 배치
        for col, item in enumerate(items):
            self.table.setItem(row, col, item)
    
    def _format_price(self, price: Optional[int]) -> str:
        """가격 포맷팅"""
        if price is None:
            return "-"
        return f"{price:,}원"
    
    def _update_status(self, count: int) -> None:
        """상태 업데이트"""
        self.count_label.setText(f"결과: {count}개")
        self.export_csv_button.setEnabled(count > 0)
        self.copy_button.setEnabled(count > 0)
    
    def clear(self) -> None:
        """결과 초기화"""
        self._results = []
        self.table.setRowCount(0)
        self._update_status(0)
    
    def get_results(self) -> list[SearchResult]:
        """현재 결과 목록 반환"""
        return self._results
    
    def _on_cell_double_clicked(self, row: int, col: int) -> None:
        """셀 더블클릭 처리 - URL 열기"""
        url_item = self.table.item(row, 4)  # URL 컬럼
        if url_item:
            url = url_item.text()
            if url:
                self.url_open_requested.emit(url)
                webbrowser.open(url)
    
    def _on_export_csv(self) -> None:
        """CSV 내보내기"""
        if not self._results:
            return
        
        # 파일 저장 대화상자
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "CSV 저장",
            "검색결과.csv",
            "CSV 파일 (*.csv)"
        )
        
        if not file_path:
            return
        
        try:
            self._save_to_csv(file_path)
            QMessageBox.information(
                self,
                "저장 완료",
                f"파일이 저장되었습니다:\n{file_path}"
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "저장 오류",
                f"파일 저장 중 오류가 발생했습니다:\n{e}"
            )
    
    def _save_to_csv(self, file_path: str) -> None:
        """CSV 파일로 저장"""
        stock_text_map = {
            StockStatus.IN_STOCK: "재고있음",
            StockStatus.OUT_OF_STOCK: "품절",
            StockStatus.UNKNOWN: "알수없음",
        }
        
        with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            
            # 헤더
            writer.writerow(["상점", "상품명", "가격", "재고", "URL"])
            
            # 데이터
            for result in self._results:
                writer.writerow([
                    result.shop_name,
                    result.product_name,
                    result.price or "",
                    stock_text_map.get(result.stock_status, "알수없음"),
                    result.product_url or ""
                ])
    
    def _on_copy_to_clipboard(self) -> None:
        """클립보드로 복사"""
        if not self._results:
            return
        
        stock_text_map = {
            StockStatus.IN_STOCK: "재고있음",
            StockStatus.OUT_OF_STOCK: "품절",
            StockStatus.UNKNOWN: "알수없음",
        }
        
        # 탭 구분 텍스트 생성
        lines = ["상점\t상품명\t가격\t재고\tURL"]
        
        for result in self._results:
            price_str = self._format_price(result.price)
            stock_str = stock_text_map.get(result.stock_status, "알수없음")
            lines.append(f"{result.shop_name}\t{result.product_name}\t{price_str}\t{stock_str}\t{result.product_url or ''}")
        
        text = "\n".join(lines)
        
        # 클립보드에 복사
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        
        QMessageBox.information(
            self,
            "복사 완료",
            f"{len(self._results)}개 항목이 클립보드에 복사되었습니다."
        )
