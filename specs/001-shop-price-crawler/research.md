# 리서치: 다중 상점 가격 크롤러

**생성일**: 2025-12-30  
**목적**: Phase 0 기술 결정 사항 및 대안 분석

## 1. HTTP 클라이언트 라이브러리

### 결정: `requests`

**이유 (Rationale)**:
- Python 생태계에서 가장 널리 사용되는 HTTP 라이브러리
- 간단한 API, 풍부한 문서, 안정적인 유지보수
- 동기 방식이므로 초보자도 이해하기 쉬움
- 테스트 mocking이 용이 (`responses` 라이브러리 지원)

**대안 검토**:
- `httpx`: 비동기 지원이 장점이나, 현재 요구사항은 동기 크롤링으로 충분
- `aiohttp`: 비동기 전용으로, 다중 상점 동시 크롤링에 유리하나 복잡도 증가
- `urllib3`: 저수준 API로 직접 사용하기 불편

**향후 확장**: 다중 상점 동시 크롤링 성능 이슈 발생 시 `httpx` 비동기 모드로 마이그레이션 고려

---

## 2. HTML 파싱 라이브러리

### 결정: `beautifulsoup4` + `lxml`

**이유 (Rationale)**:
- BeautifulSoup은 관용적(lenient) 파싱으로 깨진 HTML도 처리 가능
- CSS 선택자와 XPath 모두 지원
- `lxml` 파서를 백엔드로 사용하면 성능 향상
- 풍부한 커뮤니티 자료 및 예제

**대안 검토**:
- `lxml` 직접 사용: 빠르지만 API가 덜 직관적
- `parsel`: Scrapy에서 사용하는 라이브러리, 단독 사용 시 장점 적음
- `selectolax`: 매우 빠르지만 문서가 부족하고 커뮤니티 작음

---

## 3. 데이터 저장 방식

### 결정: JSON 파일

**이유 (Rationale)**:
- 개인 사용 목적으로 복잡한 DB 불필요
- 사람이 읽고 수정 가능 (디버깅 용이)
- Python 표준 라이브러리 `json`으로 처리 가능
- 버전 관리(git)와 호환

**대안 검토**:
- SQLite: 쿼리 기능이 있지만 현재 요구사항에 과함
- YAML: 가독성은 좋으나 Python 표준 라이브러리 아님
- pickle: 보안 문제 및 사람이 읽기 어려움

**저장 위치**: `~/.plaprice/shops.json` (사용자 홈 디렉토리)

---

## 4. CLI 테이블 출력

### 결정: `rich`

**이유 (Rationale)**:
- 아름다운 테이블 렌더링 (색상, 정렬, 테두리)
- 프로그레스 바, 스피너 등 부가 기능 제공
- 단순한 API로 빠른 적용 가능
- Windows 터미널 호환성 우수

**대안 검토**:
- `tabulate`: 간단하지만 색상/스타일링 제한적
- `prettytable`: 기능은 충분하나 `rich`보다 덜 현대적
- `pandas` DataFrame 출력: 의존성이 무거움

---

## 5. 데이터 검증

### 결정: `pydantic`

**이유 (Rationale)**:
- 타입 힌트 기반 자동 검증
- JSON 직렬화/역직렬화 내장
- 명확한 에러 메시지
- 모델 정의가 문서 역할

**대안 검토**:
- `dataclasses`: 검증 기능 없음
- `attrs`: 좋은 대안이나 `pydantic`이 더 널리 사용됨
- `marshmallow`: 스키마 정의가 별도 필요

---

## 6. 테스트 프레임워크

### 결정: `pytest` + `pytest-mock` + `responses`

**이유 (Rationale)**:
- `pytest`: Python 표준 테스트 프레임워크, 헌법에 명시
- `pytest-mock`: mock 객체 관리 편의성
- `responses`: `requests` 라이브러리 HTTP 응답 mocking

**테스트 전략**:
- 단위 테스트: 각 모듈 독립 테스트 (모든 외부 의존성 mock)
- 통합 테스트: CLI 명령 end-to-end 테스트 (HTTP만 mock)

---

## 7. 상점 크롤링 설정 구조

### 결정: CSS 선택자 기반 설정

**구조**:
```json
{
  "name": "예제 상점",
  "base_url": "https://example.com",
  "search_url_template": "https://example.com/search?q={keyword}",
  "selectors": {
    "product_container": ".product-item",
    "product_name": ".product-title",
    "product_price": ".product-price",
    "stock_status": ".stock-status"
  },
  "stock_patterns": {
    "in_stock": ["재고 있음", "구매 가능"],
    "out_of_stock": ["품절", "재고 없음"]
  }
}
```

**이유 (Rationale)**:
- CSS 선택자는 직관적이고 개발자 도구로 쉽게 확인 가능
- 상점별 설정을 독립적으로 관리 가능
- 새 상점 추가 시 코드 수정 불필요

---

## 8. 에러 처리 전략

### 결정: 부분 실패 허용 (Partial Failure)

**원칙**:
- 하나의 상점 실패가 전체 검색을 중단시키지 않음
- 실패한 상점은 결과 표에 "오류: [원인]"으로 표시
- 상세 오류 로그는 별도 파일에 기록

**에러 유형 및 처리**:
| 에러 유형 | 사용자 메시지 | 복구 방법 |
|-----------|---------------|-----------|
| 네트워크 타임아웃 | "접속 시간 초과" | 재시도 안내 |
| HTTP 4xx | "페이지를 찾을 수 없음" | URL 확인 안내 |
| HTTP 5xx | "서버 오류" | 나중에 다시 시도 안내 |
| 파싱 실패 | "페이지 구조 변경" | 선택자 업데이트 안내 |
| 결과 없음 | "검색 결과 없음" | (정상 케이스) |

---

## 9. 의존성 요약

### requirements.txt
```
requests>=2.28.0
beautifulsoup4>=4.12.0
lxml>=4.9.0
rich>=13.0.0
pydantic>=2.0.0
```

### requirements-dev.txt
```
pytest>=7.0.0
pytest-mock>=3.10.0
responses>=0.23.0
```

---

## 10. 미결정 사항 (Deferred Decisions)

| 항목 | 현재 상태 | 결정 시점 |
|------|-----------|-----------|
| JavaScript 렌더링 | 미지원 | 사용자 피드백 후 |
| 자동 스케줄링 | 미지원 | 향후 기능으로 |
| exe 빌드 도구 | 미결정 (PyInstaller 유력) | 배포 시점 |
| 가격 히스토리 저장 | 미지원 | 향후 기능으로 |
