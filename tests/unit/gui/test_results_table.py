# -*- coding: utf-8 -*-
"""
ResultsTable 테스트

검색 결과 테이블, 최저가 강조, URL 열기 테스트.
"""

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTableWidget
from PySide6.QtGui import QColor

from src.models.search import SearchResult, StockStatus


class TestResultsTable:
    """ResultsTable 클래스 테스트"""

    @pytest.fixture
    def sample_results(self):
        """샘플 검색 결과"""
        return [
            SearchResult(
                shop_id="shop-a",
                shop_name="상점A",
                product_name="테스트 상품 1",
                price=10000,
                stock_status=StockStatus.IN_STOCK,
                product_url="https://shop-a.com/product1"
            ),
            SearchResult(
                shop_id="shop-b",
                shop_name="상점B",
                product_name="테스트 상품 1",
                price=9000,  # 최저가
                stock_status=StockStatus.IN_STOCK,
                product_url="https://shop-b.com/product1"
            ),
            SearchResult(
                shop_id="shop-c",
                shop_name="상점C",
                product_name="테스트 상품 1",
                price=11000,
                stock_status=StockStatus.OUT_OF_STOCK,
                product_url="https://shop-c.com/product1"
            ),
        ]

    def test_has_table(self, qtbot):
        """테이블 위젯 존재 테스트"""
        from src.gui.results_table import ResultsTable
        
        table = ResultsTable()
        qtbot.addWidget(table)
        
        assert hasattr(table, 'table')
        assert isinstance(table.table, QTableWidget)

    def test_table_columns(self, qtbot):
        """테이블 컬럼 구조 테스트"""
        from src.gui.results_table import ResultsTable
        
        table = ResultsTable()
        qtbot.addWidget(table)
        
        # 상점명, 상품명, 가격, 재고 상태, URL
        assert table.table.columnCount() >= 4
        
        headers = [table.table.horizontalHeaderItem(i).text() 
                   for i in range(table.table.columnCount())]
        
        assert any("상점" in h for h in headers)
        assert any("상품" in h or "이름" in h for h in headers)
        assert any("가격" in h for h in headers)
        assert any("재고" in h for h in headers)

    def test_display_results(self, qtbot, sample_results):
        """결과 표시 테스트"""
        from src.gui.results_table import ResultsTable
        
        table = ResultsTable()
        qtbot.addWidget(table)
        
        table.set_results(sample_results)
        
        assert table.table.rowCount() == 3

    def test_clear_results(self, qtbot, sample_results):
        """결과 초기화 테스트"""
        from src.gui.results_table import ResultsTable
        
        table = ResultsTable()
        qtbot.addWidget(table)
        
        table.set_results(sample_results)
        table.clear()
        
        assert table.table.rowCount() == 0

    def test_lowest_price_highlighted(self, qtbot, sample_results):
        """최저가 행 녹색 강조 테스트"""
        from src.gui.results_table import ResultsTable
        
        table = ResultsTable()
        qtbot.addWidget(table)
        
        table.set_results(sample_results)
        
        # 최저가는 상점B (9000원) - 인덱스 1
        lowest_row = 1
        
        # 셀의 배경색 확인 (녹색 계열)
        cell_item = table.table.item(lowest_row, 0)
        if cell_item:
            bg_color = cell_item.background().color()
            # 녹색 계열 확인 (G 채널이 높고, R/B가 상대적으로 낮음)
            assert bg_color.green() > bg_color.red()
            assert bg_color.green() > bg_color.blue()

    def test_non_lowest_price_no_highlight(self, qtbot, sample_results):
        """최저가 아닌 행은 강조 없음"""
        from src.gui.results_table import ResultsTable
        
        table = ResultsTable()
        qtbot.addWidget(table)
        
        table.set_results(sample_results)
        
        # 최저가 아닌 행 (상점A, 10000원) - 인덱스 0
        non_lowest_row = 0
        
        cell_item = table.table.item(non_lowest_row, 0)
        if cell_item:
            bg_color = cell_item.background().color()
            # 기본 배경색이거나 녹색이 아님
            is_green = bg_color.green() > bg_color.red() and bg_color.green() > bg_color.blue()
            # 기본색(무효 색상)이거나 녹색 아니어야 함
            assert not is_green or not bg_color.isValid()

    def test_get_results(self, qtbot, sample_results):
        """현재 결과 목록 가져오기"""
        from src.gui.results_table import ResultsTable
        
        table = ResultsTable()
        qtbot.addWidget(table)
        
        table.set_results(sample_results)
        
        results = table.get_results()
        assert len(results) == 3

    def test_has_result_count_label(self, qtbot, sample_results):
        """결과 개수 레이블 테스트"""
        from src.gui.results_table import ResultsTable
        
        table = ResultsTable()
        qtbot.addWidget(table)
        
        table.set_results(sample_results)
        
        # 결과 개수 표시 확인
        assert hasattr(table, 'count_label') or hasattr(table, 'status_label')

    def test_double_click_signal(self, qtbot, sample_results):
        """더블클릭 시 URL 열기 시그널"""
        from src.gui.results_table import ResultsTable
        
        table = ResultsTable()
        qtbot.addWidget(table)
        
        table.set_results(sample_results)
        
        assert hasattr(table, 'url_open_requested')

    def test_empty_results_shows_message(self, qtbot):
        """빈 결과 시 메시지 표시"""
        from src.gui.results_table import ResultsTable
        
        table = ResultsTable()
        qtbot.addWidget(table)
        
        table.set_results([])
        
        # 빈 상태 확인
        assert table.table.rowCount() == 0

    def test_max_5_results_per_shop(self, qtbot):
        """상점당 최대 5개 결과 표시"""
        from src.gui.results_table import ResultsTable
        
        table = ResultsTable()
        qtbot.addWidget(table)
        
        # 한 상점에서 10개 결과 생성
        results = [
            SearchResult(
                shop_id="shop-a",
                shop_name="상점A",
                product_name=f"상품 {i}",
                price=10000 + i * 100,
                stock_status=StockStatus.IN_STOCK,
                product_url=f"https://shop-a.com/product{i}"
            )
            for i in range(10)
        ]
        
        table.set_results(results, max_per_shop=5)
        
        # 최대 5개만 표시
        assert table.table.rowCount() == 5

    def test_sorting_by_price(self, qtbot, sample_results):
        """가격순 정렬 테스트"""
        from src.gui.results_table import ResultsTable
        
        table = ResultsTable()
        qtbot.addWidget(table)
        
        table.set_results(sample_results)
        
        # 테이블 정렬 활성화 확인
        assert table.table.isSortingEnabled()
    def test_has_export_csv_button(self, qtbot):
        """CSV 저장 버튼 존재 테스트"""
        from src.gui.results_table import ResultsTable
        
        table = ResultsTable()
        qtbot.addWidget(table)
        
        assert hasattr(table, 'export_csv_button')
        # 결과 없을 때 비활성화
        assert not table.export_csv_button.isEnabled()

    def test_has_copy_button(self, qtbot):
        """클립보드 복사 버튼 존재 테스트"""
        from src.gui.results_table import ResultsTable
        
        table = ResultsTable()
        qtbot.addWidget(table)
        
        assert hasattr(table, 'copy_button')
        # 결과 없을 때 비활성화
        assert not table.copy_button.isEnabled()

    def test_export_buttons_enabled_with_results(self, qtbot, sample_results):
        """결과 있을 때 내보내기 버튼 활성화"""
        from src.gui.results_table import ResultsTable
        
        table = ResultsTable()
        qtbot.addWidget(table)
        
        table.set_results(sample_results)
        
        assert table.export_csv_button.isEnabled()
        assert table.copy_button.isEnabled()

    def test_export_csv_saves_file(self, qtbot, sample_results, mocker, tmp_path):
        """CSV 내보내기 파일 저장 테스트"""
        from src.gui.results_table import ResultsTable
        
        table = ResultsTable()
        qtbot.addWidget(table)
        table.set_results(sample_results)
        
        # 파일 대화상자 모킹
        csv_path = tmp_path / "test_export.csv"
        mocker.patch(
            'src.gui.results_table.QFileDialog.getSaveFileName',
            return_value=(str(csv_path), "CSV 파일 (*.csv)")
        )
        
        # 성공 메시지 모킹
        mock_info = mocker.patch('src.gui.results_table.QMessageBox.information')
        
        # CSV 저장 버튼 클릭
        table.export_csv_button.click()
        
        # 파일 생성 확인
        assert csv_path.exists()
        
        # 파일 내용 확인
        content = csv_path.read_text(encoding='utf-8-sig')
        assert "상점" in content
        assert "상품명" in content
        assert "가격" in content
        assert "상점A" in content
        assert "상점B" in content
        
        # 성공 메시지 표시 확인
        mock_info.assert_called_once()

    def test_copy_to_clipboard(self, qtbot, sample_results, mocker):
        """클립보드 복사 테스트"""
        from src.gui.results_table import ResultsTable
        from PySide6.QtWidgets import QApplication
        
        table = ResultsTable()
        qtbot.addWidget(table)
        table.set_results(sample_results)
        
        # 성공 메시지 모킹
        mock_info = mocker.patch('src.gui.results_table.QMessageBox.information')
        
        # 복사 버튼 클릭
        table.copy_button.click()
        
        # 클립보드 내용 확인
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        
        assert "상점" in text
        assert "상품명" in text
        assert "상점A" in text
        assert "상점B" in text
        
        # 탭 구분 확인
        assert "\t" in text
        
        # 성공 메시지 표시 확인
        mock_info.assert_called_once()

    def test_export_csv_cancel_does_nothing(self, qtbot, sample_results, mocker):
        """CSV 내보내기 취소 시 아무것도 하지 않음"""
        from src.gui.results_table import ResultsTable
        
        table = ResultsTable()
        qtbot.addWidget(table)
        table.set_results(sample_results)
        
        # 파일 대화상자 취소 모킹
        mocker.patch(
            'src.gui.results_table.QFileDialog.getSaveFileName',
            return_value=("", "")
        )
        
        # CSV 저장 버튼 클릭 - 예외 없이 완료되어야 함
        table.export_csv_button.click()