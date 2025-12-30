# PlaPrice - 다중 상점 가격 크롤러

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

여러 상점 웹페이지에서 상품 가격을 검색하고 비교하는 CLI 도구입니다.

## 기능

- 🔍 **키워드 검색**: 등록된 상점에서 상품 검색
- 🏪 **다중 상점 지원**: 여러 상점을 등록하고 한 번에 검색
- 💰 **가격 비교**: 상점별 가격을 테이블로 비교, 최저가 하이라이트
- 📦 **재고 상태**: 재고 있음/품절 상태 표시
- 💾 **영구 저장**: 상점 설정을 JSON 파일로 저장
- 🖥️ **GUI 인터페이스**: 그래픽 사용자 인터페이스로 편리하게 사용

## 설치

### 요구사항

- Python 3.10 이상
- Windows 10/11

### 설치 방법

```bash
# 저장소 클론
git clone https://github.com/your-repo/plaprice.git
cd plaprice

# 가상환경 생성 및 활성화
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # Windows PowerShell

# 의존성 설치
pip install -r requirements.txt

# 개발 의존성 (테스트 포함)
pip install -r requirements-dev.txt
```

## 사용법

### GUI 모드 (그래픽 인터페이스)

가장 간편한 방법으로, GUI 모드를 사용하면 마우스 클릭만으로 가격을 비교할 수 있습니다.

```bash
# GUI 실행
python -m src --gui
```

**GUI 주요 기능:**

- **상점 관리 (좌측 패널)**
  - 상점 추가/수정/삭제
  - 체크박스로 검색 대상 상점 선택
  - 전체 선택/해제

- **검색 및 결과 (우측 패널)**
  - 검색어 입력 후 검색 버튼 클릭
  - 진행률 바로 검색 상태 확인
  - 최저가 상품 녹색 강조 표시
  - 결과 행 더블클릭 시 상품 페이지 열기

- **결과 내보내기**
  - CSV 파일로 저장
  - 클립보드에 복사 (Excel 등에 붙여넣기 가능)

### CLI 모드 (명령줄 인터페이스)

#### 기본 명령어

```bash
# 도움말
python -m src.cli.main --help

# 상품 검색 (등록된 모든 상점에서)
python -m src.cli.main search "무선 마우스"

# 특정 상점에서만 검색
python -m src.cli.main search "키보드" --shop SHOP_ID
```

### 상점 관리

```bash
# 등록된 상점 목록
python -m src.cli.main shop list

# 새 상점 추가
python -m src.cli.main shop add \
  --name "예제 상점" \
  --url "https://example.com" \
  --search-template "https://example.com/search?q={keyword}" \
  --container ".product-item" \
  --name-selector ".product-title" \
  --price-selector ".product-price"

# 상점 상세 정보
python -m src.cli.main shop show SHOP_ID

# 상점 삭제
python -m src.cli.main shop remove SHOP_ID

# 상점 활성화/비활성화
python -m src.cli.main shop enable SHOP_ID
python -m src.cli.main shop disable SHOP_ID
```

### 상점 설정 테스트

```bash
# 상점 크롤링 테스트
python -m src.cli.main test SHOP_ID --keyword "테스트"
```

### 설정 관리

```bash
# 설정 디렉토리 경로 확인
python -m src.cli.main config path
```

### 출력 옵션

```bash
# JSON 형식 출력
python -m src.cli.main --json shop list

# 조용한 모드 (최소 출력)
python -m src.cli.main --quiet search "마우스"
```

## 상점 설정 가이드

상점을 추가할 때 다음 CSS 선택자를 지정해야 합니다:

| 옵션 | 필수 | 설명 |
|------|------|------|
| `--container` | ✅ | 상품 목록의 각 상품을 감싸는 요소 선택자 |
| `--name-selector` | ✅ | 상품명 요소 선택자 (컨테이너 기준 상대 경로) |
| `--price-selector` | ✅ | 가격 요소 선택자 |
| `--link-selector` | ❌ | 상품 상세 링크 선택자 |
| `--stock-selector` | ❌ | 재고 상태 요소 선택자 |

### 예시

웹페이지 HTML이 다음과 같다면:

```html
<div class="product-list">
  <div class="product-item">
    <a href="/product/123" class="product-link">
      <h3 class="product-title">무선 마우스</h3>
    </a>
    <span class="product-price">₩25,000</span>
    <span class="stock-status">재고 있음</span>
  </div>
</div>
```

다음과 같이 상점을 추가합니다:

```bash
python -m src.cli.main shop add \
  --name "예제 상점" \
  --url "https://example.com" \
  --search-template "https://example.com/search?q={keyword}" \
  --container ".product-item" \
  --name-selector ".product-title" \
  --price-selector ".product-price" \
  --link-selector ".product-link" \
  --stock-selector ".stock-status"
```

## 설정 파일

상점 설정은 다음 경로에 JSON 파일로 저장됩니다:

- Windows: `C:\Users\<사용자>\.plaprice\shops.json`

## 개발

### 테스트 실행

```bash
# 전체 테스트
pytest tests/ -v

# 커버리지 포함
pytest tests/ --cov=src --cov-report=html

# 특정 테스트
pytest tests/unit/test_models.py -v
```

### 프로젝트 구조

```
src/
├── models/          # 데이터 모델 (Shop, SearchResult)
├── crawlers/        # 크롤링 로직 (HtmlCrawler, MultiShopCrawler)
├── storage/         # 데이터 저장 (ShopStore)
├── display/         # 결과 표시 (TableRenderer)
├── cli/             # CLI 인터페이스
├── gui/             # GUI 인터페이스 (PySide6)
│   ├── main_window.py   # 메인 윈도우
│   ├── shop_panel.py    # 상점 목록 패널
│   ├── search_panel.py  # 검색 패널
│   ├── results_table.py # 결과 테이블
│   └── settings.py      # GUI 설정
└── utils/           # 공통 유틸리티 (HttpClient)

tests/
├── unit/            # 단위 테스트
├── integration/     # 통합 테스트
└── fixtures/        # 테스트 데이터
```

## 제한사항

- **정적 HTML만 지원**: JavaScript로 렌더링되는 페이지는 크롤링 불가
- **상점별 설정 필요**: 각 상점의 HTML 구조에 맞는 CSS 선택자 지정 필요
- **크롤링 정책 준수**: 대상 웹사이트의 robots.txt 및 이용약관 준수 필요

## 라이선스

MIT License
