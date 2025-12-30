"""
PlaPrice CLI/GUI 엔트리포인트

`python -m src` 명령으로 CLI 실행
`python -m src --gui` 명령으로 GUI 실행
"""

import sys


def main():
    """메인 엔트리포인트: CLI 또는 GUI 분기"""
    # --gui 옵션 확인
    if "--gui" in sys.argv:
        # GUI 모드
        sys.argv.remove("--gui")
        from src.gui import run_gui
        sys.exit(run_gui())
    else:
        # CLI 모드
        from src.cli.main import main as cli_main
        cli_main()


if __name__ == "__main__":
    main()
