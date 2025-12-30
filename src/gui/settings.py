# -*- coding: utf-8 -*-
"""
GUI 설정 모델

창 크기, 위치, 스플리터 상태 등 GUI 설정을 저장/복원한다.
"""

import json
from pathlib import Path
from typing import ClassVar

from pydantic import BaseModel


class WindowGeometry(BaseModel):
    """창 크기 및 위치"""
    
    x: int = 100
    y: int = 100
    width: int = 1000
    height: int = 700
    is_maximized: bool = False


class SplitterState(BaseModel):
    """스플리터 상태"""
    
    sizes: list[int] = [250, 750]


class GuiSettings(BaseModel):
    """GUI 전체 설정"""
    
    window: WindowGeometry = WindowGeometry()
    splitter: SplitterState = SplitterState()
    last_search_keyword: str = ""
    selected_shop_ids: list[str] = []
    
    # 기본 저장 경로
    DEFAULT_PATH: ClassVar[Path] = Path.home() / ".plaprice" / "gui_settings.json"
    
    @classmethod
    def load(cls, path: Path | None = None) -> "GuiSettings":
        """
        설정 파일 로드
        
        파일이 없거나 손상된 경우 기본값 반환.
        
        Args:
            path: 설정 파일 경로 (None이면 기본 경로)
            
        Returns:
            GuiSettings 인스턴스
        """
        settings_path = path or cls.DEFAULT_PATH
        
        if not settings_path.exists():
            return cls()
        
        try:
            data = json.loads(settings_path.read_text(encoding="utf-8"))
            return cls.model_validate(data)
        except (json.JSONDecodeError, ValueError):
            # 손상된 파일인 경우 기본값 반환
            return cls()
    
    def save(self, path: Path | None = None) -> None:
        """
        설정 파일 저장
        
        Args:
            path: 설정 파일 경로 (None이면 기본 경로)
        """
        settings_path = path or self.DEFAULT_PATH
        
        # 디렉토리 생성
        settings_path.parent.mkdir(parents=True, exist_ok=True)
        
        # JSON으로 저장
        data = self.model_dump()
        settings_path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
