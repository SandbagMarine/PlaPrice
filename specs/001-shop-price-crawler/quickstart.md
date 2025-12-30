# 빠른 시작 가이드: PlaPrice

**생성일**: 2025-12-30  
**목적**: 개발자가 빠르게 프로젝트를 설정하고 실행할 수 있도록 안내

---

## 1. 사전 요구사항

- Python 3.10 이상
- pip (Python 패키지 관리자)
- Windows 10/11

### Python 버전 확인

```powershell
python --version
# Python 3.10.x 이상이어야 함
```

---

## 2. 프로젝트 설정

### 2.1 저장소 클론 및 가상환경 생성

```powershell
# 저장소 클론
git clone <repository-url>
cd PlaPrice

# 가상환경 생성
python -m venv .venv

# 가상환경 활성화 (Windows PowerShell)
.\.venv\Scripts\Activate.ps1
```

### 2.2 의존성 설치

```powershell
# 프로덕션 의존성
pip install -r requirements.txt

# 개발 의존성 (테스트 포함)
pip install -r requirements-dev.txt
```

---

## 3. 설정 초기화

```powershell
# 설정 디렉토리 초기화
python -m plaprice config init

# 설정 경로 확인
python -m plaprice config path
# 출력: C:\Users\<username>\.plaprice\
```

---

## 4. 상점 추가

### 4.1 예제 상점 추가

```powershell
# 간단한 상점 추가 예시
python -m plaprice shop add "예제상점" "https://example.com/search?q={keyword}" `
  --container ".product-item" `
  --name-selector ".product-name" `
  --price-selector ".product-price"
```

### 4.2 JSON 파일로 상점 추가

`shop-config.json` 파일 생성:

```json
{
  "name": "예제 상점",
  "base_url": "https://example.com",
  "search_url_template": "https://example.com/search?q={keyword}",
  "selectors": {
    "product_container": ".product-item",
    "product_name": ".product-title",
    "product_price": ".product-price"
  }
}
```

```powershell
python -m plaprice shop add --from-file shop-config.json
```

### 4.3 등록된 상점 확인

```powershell
python -m plaprice shop list
```

---

## 5. 검색 실행

```powershell
# 모든 상점에서 검색
python -m plaprice search "무선 마우스"

# 특정 상점에서만 검색
python -m plaprice search "키보드" --shops <shop-id>

# JSON 출력
python -m plaprice search "모니터" --json
```

---

## 6. 테스트 실행

### 6.1 전체 테스트

```powershell
pytest
```

### 6.2 특정 테스트 실행

```powershell
# 단위 테스트만
pytest tests/unit/

# 통합 테스트만
pytest tests/integration/

# 특정 파일
pytest tests/unit/test_models.py

# 특정 테스트 함수
pytest tests/unit/test_models.py::test_shop_creation
```

### 6.3 커버리지 리포트

```powershell
pytest --cov=src --cov-report=html
# htmlcov/index.html 열기
```

---

## 7. 개발 워크플로우

### TDD 사이클 (헌법 준수)

1. **Red**: 실패하는 테스트 작성
2. **Green**: 테스트를 통과시키는 최소한의 코드 작성
3. **Refactor**: 코드 개선

### 예시: 새 기능 추가

```powershell
# 1. 테스트 작성
# tests/unit/test_new_feature.py 생성

# 2. 테스트 실행 (실패 확인)
pytest tests/unit/test_new_feature.py
# FAILED (빨간색)

# 3. 구현
# src/new_feature.py 작성

# 4. 테스트 재실행 (통과 확인)
pytest tests/unit/test_new_feature.py
# PASSED (녹색)

# 5. 리팩토링 후 테스트 재실행
pytest tests/unit/test_new_feature.py
```

---

## 8. 디렉토리 구조 요약

```
PlaPrice/
├── src/                     # 소스 코드
│   ├── models/              # 데이터 모델
│   ├── crawlers/            # 크롤링 로직
│   ├── storage/             # 데이터 저장
│   ├── display/             # 결과 표시
│   ├── cli/                 # CLI 인터페이스
│   └── utils/               # 유틸리티
├── tests/                   # 테스트
│   ├── unit/                # 단위 테스트
│   ├── integration/         # 통합 테스트
│   └── fixtures/            # 테스트 데이터
├── specs/                   # 기능 명세
│   └── 001-shop-price-crawler/
├── requirements.txt         # 프로덕션 의존성
└── requirements-dev.txt     # 개발 의존성
```

---

## 9. 문제 해결

### 가상환경 활성화 실패 (PowerShell)

```powershell
# 실행 정책 변경 (관리자 권한 필요)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### lxml 설치 실패

```powershell
# Windows에서 미리 빌드된 wheel 사용
pip install lxml --only-binary :all:
```

### 테스트 실패 시 상세 출력

```powershell
pytest -v --tb=long
```

---

## 10. 유용한 명령어

```powershell
# 도움말
python -m plaprice --help
python -m plaprice search --help

# 버전 확인
python -m plaprice --version

# 상점 테스트
python -m plaprice test <shop-id> "테스트 키워드"
```
