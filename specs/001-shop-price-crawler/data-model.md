# 데이터 모델: 다중 상점 가격 크롤러

**생성일**: 2025-12-30  
**목적**: Phase 1 핵심 엔티티 정의

## 엔티티 관계도

```
┌─────────────────┐     1:N     ┌─────────────────┐
│      Shop       │─────────────│  SearchResult   │
│  (상점 설정)    │             │  (검색 결과)    │
└─────────────────┘             └─────────────────┘
         │                               │
         │                               │
         │                               │
         └───────────┬───────────────────┘
                     │
                     ▼
              ┌─────────────────┐
              │  SearchQuery    │
              │  (검색 요청)    │
              └─────────────────┘
```

---

## 1. Shop (상점)

크롤링 대상 웹사이트 설정 정보.

### 속성

| 속성명 | 타입 | 필수 | 설명 |
|--------|------|------|------|
| `id` | string (UUID) | ✅ | 고유 식별자 |
| `name` | string | ✅ | 상점 표시 이름 (예: "쿠팡", "11번가") |
| `base_url` | string (URL) | ✅ | 상점 기본 URL |
| `search_url_template` | string | ✅ | 검색 URL 템플릿 (예: `https://example.com/search?q={keyword}`) |
| `selectors` | ShopSelectors | ✅ | CSS 선택자 설정 |
| `stock_patterns` | StockPatterns | ❌ | 재고 상태 판별 패턴 |
| `enabled` | boolean | ✅ | 활성화 여부 (기본값: true) |
| `created_at` | datetime | ✅ | 생성 시각 |
| `updated_at` | datetime | ✅ | 수정 시각 |

### ShopSelectors (하위 객체)

| 속성명 | 타입 | 필수 | 설명 |
|--------|------|------|------|
| `product_container` | string | ✅ | 상품 컨테이너 CSS 선택자 |
| `product_name` | string | ✅ | 상품명 CSS 선택자 |
| `product_price` | string | ✅ | 가격 CSS 선택자 |
| `product_link` | string | ❌ | 상품 상세 링크 선택자 |
| `stock_status` | string | ❌ | 재고 상태 선택자 |

### StockPatterns (하위 객체)

| 속성명 | 타입 | 필수 | 설명 |
|--------|------|------|------|
| `in_stock` | list[string] | ❌ | 재고 있음 텍스트 패턴 |
| `out_of_stock` | list[string] | ❌ | 품절 텍스트 패턴 |

### 검증 규칙

- `name`: 1~50자
- `base_url`: 유효한 HTTP/HTTPS URL
- `search_url_template`: `{keyword}` 플레이스홀더 포함 필수
- `selectors.product_container`: 비어 있지 않은 문자열

### JSON 예시

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "예제 상점",
  "base_url": "https://example.com",
  "search_url_template": "https://example.com/search?q={keyword}",
  "selectors": {
    "product_container": ".product-item",
    "product_name": ".product-title",
    "product_price": ".product-price",
    "product_link": ".product-link",
    "stock_status": ".stock-status"
  },
  "stock_patterns": {
    "in_stock": ["재고 있음", "구매 가능", "바로 구매"],
    "out_of_stock": ["품절", "재고 없음", "일시 품절"]
  },
  "enabled": true,
  "created_at": "2025-12-30T10:00:00Z",
  "updated_at": "2025-12-30T10:00:00Z"
}
```

---

## 2. SearchResult (검색 결과)

크롤링으로 얻은 개별 상품 정보.

### 속성

| 속성명 | 타입 | 필수 | 설명 |
|--------|------|------|------|
| `shop_id` | string (UUID) | ✅ | 상점 ID 참조 |
| `shop_name` | string | ✅ | 상점 이름 (조회 편의용) |
| `product_name` | string | ✅ | 상품명 |
| `price` | integer | ❌ | 가격 (원, null이면 가격 정보 없음) |
| `price_text` | string | ❌ | 원본 가격 문자열 (예: "₩15,000") |
| `stock_status` | StockStatus | ✅ | 재고 상태 |
| `product_url` | string (URL) | ❌ | 상품 상세 페이지 URL |
| `crawled_at` | datetime | ✅ | 크롤링 시각 |

### StockStatus (Enum)

| 값 | 설명 |
|----|------|
| `IN_STOCK` | 재고 있음 |
| `OUT_OF_STOCK` | 품절 |
| `UNKNOWN` | 판별 불가 |

### 검증 규칙

- `product_name`: 비어 있지 않은 문자열
- `price`: 0 이상의 정수 또는 null
- `stock_status`: 유효한 StockStatus 값

### JSON 예시

```json
{
  "shop_id": "550e8400-e29b-41d4-a716-446655440000",
  "shop_name": "예제 상점",
  "product_name": "무선 마우스 M100",
  "price": 25000,
  "price_text": "₩25,000",
  "stock_status": "IN_STOCK",
  "product_url": "https://example.com/product/12345",
  "crawled_at": "2025-12-30T10:05:00Z"
}
```

---

## 3. SearchQuery (검색 요청)

사용자가 입력한 검색 조건.

### 속성

| 속성명 | 타입 | 필수 | 설명 |
|--------|------|------|------|
| `keyword` | string | ✅ | 검색 키워드 |
| `shop_ids` | list[string] | ❌ | 대상 상점 ID 목록 (비어 있으면 모든 활성 상점) |
| `created_at` | datetime | ✅ | 요청 시각 |

### 검증 규칙

- `keyword`: 1~100자, 공백만으로 구성 불가

### JSON 예시

```json
{
  "keyword": "무선 마우스",
  "shop_ids": [
    "550e8400-e29b-41d4-a716-446655440000",
    "550e8400-e29b-41d4-a716-446655440001"
  ],
  "created_at": "2025-12-30T10:05:00Z"
}
```

---

## 4. CrawlError (크롤링 오류)

크롤링 실패 시 오류 정보.

### 속성

| 속성명 | 타입 | 필수 | 설명 |
|--------|------|------|------|
| `shop_id` | string (UUID) | ✅ | 상점 ID |
| `shop_name` | string | ✅ | 상점 이름 |
| `error_type` | ErrorType | ✅ | 오류 유형 |
| `message` | string | ✅ | 사용자 친화적 메시지 |
| `details` | string | ❌ | 기술적 상세 (로깅용) |
| `occurred_at` | datetime | ✅ | 발생 시각 |

### ErrorType (Enum)

| 값 | 설명 |
|----|------|
| `NETWORK_TIMEOUT` | 네트워크 타임아웃 |
| `HTTP_ERROR` | HTTP 4xx/5xx 응답 |
| `PARSE_ERROR` | HTML 파싱 실패 |
| `NO_RESULTS` | 검색 결과 없음 (정상 케이스) |
| `UNKNOWN` | 알 수 없는 오류 |

---

## 5. ShopStore (저장소 파일 구조)

상점 설정을 저장하는 JSON 파일 구조.

### 파일 위치

- Windows: `%USERPROFILE%\.plaprice\shops.json`
- 예: `C:\Users\username\.plaprice\shops.json`

### 파일 구조

```json
{
  "version": "1.0.0",
  "shops": [
    { /* Shop 객체 */ },
    { /* Shop 객체 */ }
  ],
  "last_updated": "2025-12-30T10:00:00Z"
}
```

---

## 상태 다이어그램: 크롤링 흐름

```
┌─────────────┐
│   IDLE      │
└──────┬──────┘
       │ search(keyword)
       ▼
┌─────────────┐
│  CRAWLING   │──────────────────┐
└──────┬──────┘                  │
       │                         │ timeout/error
       │ success                 ▼
       ▼                  ┌─────────────┐
┌─────────────┐           │   ERROR     │
│  PARSING    │           └─────────────┘
└──────┬──────┘
       │ success
       ▼
┌─────────────┐
│  COMPLETE   │
└─────────────┘
```
