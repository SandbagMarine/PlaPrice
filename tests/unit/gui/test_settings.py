# -*- coding: utf-8 -*-
"""
GuiSettings 테스트

GUI 설정 저장/복원 기능을 테스트한다.
"""

import json
import pytest
from pathlib import Path


class TestGuiSettings:
    """GuiSettings 클래스 테스트"""

    def test_default_values(self):
        """기본값으로 GuiSettings 생성"""
        from src.gui.settings import GuiSettings
        
        settings = GuiSettings()
        
        # 기본 창 크기
        assert settings.window.width == 1000
        assert settings.window.height == 700
        assert settings.window.x == 100
        assert settings.window.y == 100
        assert settings.window.is_maximized is False
        
        # 기본 스플리터 크기
        assert settings.splitter.sizes == [250, 750]
        
        # 기본 검색 상태
        assert settings.last_search_keyword == ""
        assert settings.selected_shop_ids == []

    def test_save_and_load(self, tmp_path: Path):
        """설정 저장 및 로드"""
        from src.gui.settings import GuiSettings, WindowGeometry, SplitterState
        
        settings_path = tmp_path / "gui_settings.json"
        
        # 설정 생성 및 수정
        settings = GuiSettings()
        settings.window.width = 1200
        settings.window.height = 800
        settings.window.x = 200
        settings.window.y = 150
        settings.splitter.sizes = [300, 900]
        settings.last_search_keyword = "테스트"
        settings.selected_shop_ids = ["shop1", "shop2"]
        
        # 저장
        settings.save(settings_path)
        
        # 파일 존재 확인
        assert settings_path.exists()
        
        # 로드
        loaded = GuiSettings.load(settings_path)
        
        # 값 확인
        assert loaded.window.width == 1200
        assert loaded.window.height == 800
        assert loaded.window.x == 200
        assert loaded.window.y == 150
        assert loaded.splitter.sizes == [300, 900]
        assert loaded.last_search_keyword == "테스트"
        assert loaded.selected_shop_ids == ["shop1", "shop2"]

    def test_load_nonexistent_file(self, tmp_path: Path):
        """존재하지 않는 파일 로드 시 기본값 반환"""
        from src.gui.settings import GuiSettings
        
        nonexistent_path = tmp_path / "nonexistent.json"
        
        settings = GuiSettings.load(nonexistent_path)
        
        # 기본값 확인
        assert settings.window.width == 1000
        assert settings.window.height == 700

    def test_load_corrupted_file(self, tmp_path: Path):
        """손상된 파일 로드 시 기본값 반환"""
        from src.gui.settings import GuiSettings
        
        corrupted_path = tmp_path / "corrupted.json"
        corrupted_path.write_text("{ invalid json }", encoding="utf-8")
        
        settings = GuiSettings.load(corrupted_path)
        
        # 기본값 확인
        assert settings.window.width == 1000
        assert settings.window.height == 700

    def test_window_geometry_validation(self):
        """창 크기 최소값 검증"""
        from src.gui.settings import WindowGeometry
        
        # 최소값 이하로 설정해도 유효
        geometry = WindowGeometry(width=400, height=300)
        assert geometry.width == 400
        assert geometry.height == 300

    def test_splitter_state_validation(self):
        """스플리터 상태 검증"""
        from src.gui.settings import SplitterState
        
        state = SplitterState(sizes=[200, 600])
        assert state.sizes == [200, 600]


class TestWindowGeometry:
    """WindowGeometry 모델 테스트"""

    def test_create_with_defaults(self):
        """기본값으로 생성"""
        from src.gui.settings import WindowGeometry
        
        geometry = WindowGeometry()
        
        assert geometry.x == 100
        assert geometry.y == 100
        assert geometry.width == 1000
        assert geometry.height == 700
        assert geometry.is_maximized is False

    def test_create_with_custom_values(self):
        """커스텀 값으로 생성"""
        from src.gui.settings import WindowGeometry
        
        geometry = WindowGeometry(
            x=50, y=50, width=1200, height=800, is_maximized=True
        )
        
        assert geometry.x == 50
        assert geometry.y == 50
        assert geometry.width == 1200
        assert geometry.height == 800
        assert geometry.is_maximized is True


class TestSplitterState:
    """SplitterState 모델 테스트"""

    def test_create_with_defaults(self):
        """기본값으로 생성"""
        from src.gui.settings import SplitterState
        
        state = SplitterState()
        
        assert state.sizes == [250, 750]

    def test_create_with_custom_values(self):
        """커스텀 값으로 생성"""
        from src.gui.settings import SplitterState
        
        state = SplitterState(sizes=[300, 700])
        
        assert state.sizes == [300, 700]
