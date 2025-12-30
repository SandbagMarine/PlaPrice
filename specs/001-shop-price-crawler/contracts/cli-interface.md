# CLI 인터페이스 계약: PlaPrice

**생성일**: 2025-12-30  
**목적**: Phase 1 CLI 명령어 및 옵션 정의

## 개요

PlaPrice는 명령줄 인터페이스(CLI)를 통해 상점 관리 및 가격 검색 기능을 제공한다.
모든 명령은 `plaprice` 또는 `python -m plaprice` 형태로 실행 가능하다.

---

## 명령어 구조

```
plaprice <command> [options] [arguments]
```

### 전역 옵션

| 옵션 | 단축 | 설명 |
|------|------|------|
| `--help` | `-h` | 도움말 표시 |
| `--version` | `-v` | 버전 정보 표시 |
| `--config <path>` | `-c` | 설정 파일 경로 지정 (기본: ~/.plaprice/) |
| `--quiet` | `-q` | 최소 출력 모드 |
| `--json` | | 출력을 JSON 형식으로 |

---

## 1. 검색 명령어: `search`

키워드로 상품을 검색하고 결과를 표 형태로 출력한다.

### 사용법

```bash
plaprice search <keyword> [options]
```

### 인자

| 인자 | 필수 | 설명 |
|------|------|------|
| `<keyword>` | ✅ | 검색할 키워드 또는 제품명 |

### 옵션

| 옵션 | 단축 | 설명 |
|------|------|------|
| `--shops <ids>` | `-s` | 검색할 상점 ID 목록 (쉼표 구분) |
| `--all` | `-a` | 모든 활성 상점에서 검색 (기본값) |
| `--timeout <sec>` | `-t` | 상점별 타임아웃 초 (기본: 30) |
| `--sort <field>` | | 정렬 기준: price, name, shop (기본: price) |
| `--limit <n>` | `-n` | 상점별 최대 결과 수 (기본: 10) |

### 출력 예시

```
┏━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━┓
┃ 상점      ┃ 상품명               ┃ 가격     ┃ 상태    ┃
┡━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━┩
│ 쿠팡      │ 로지텍 무선 마우스   │ ₩25,000  │ 재고있음│
│ 11번가    │ 로지텍 M100 무선     │ ₩27,500  │ 재고있음│
│ G마켓     │ 무선마우스 M100      │ ₩26,000  │ 품절    │
└───────────┴──────────────────────┴──────────┴─────────┘

검색 완료: 3개 상점, 3개 결과 (1.2초)
```

### 종료 코드

| 코드 | 의미 |
|------|------|
| 0 | 성공 (결과 있음) |
| 0 | 성공 (결과 없음) |
| 1 | 부분 실패 (일부 상점 오류) |
| 2 | 전체 실패 (모든 상점 오류) |
| 3 | 입력 오류 (잘못된 옵션 등) |

---

## 2. 상점 관리 명령어: `shop`

등록된 상점을 관리한다.

### 2.1 상점 목록 조회: `shop list`

```bash
plaprice shop list [options]
```

#### 옵션

| 옵션 | 설명 |
|------|------|
| `--all` | 비활성 상점 포함 |

#### 출력 예시

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━┓
┃ ID                                   ┃ 이름     ┃ 상태    ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━┩
│ 550e8400-e29b-41d4-a716-446655440000 │ 쿠팡     │ 활성    │
│ 550e8400-e29b-41d4-a716-446655440001 │ 11번가   │ 활성    │
│ 550e8400-e29b-41d4-a716-446655440002 │ G마켓    │ 비활성  │
└──────────────────────────────────────┴──────────┴─────────┘

등록된 상점: 3개 (활성: 2개)
```

### 2.2 상점 추가: `shop add`

```bash
plaprice shop add <name> <search_url_template> [options]
```

#### 인자

| 인자 | 필수 | 설명 |
|------|------|------|
| `<name>` | ✅ | 상점 이름 |
| `<search_url_template>` | ✅ | 검색 URL 템플릿 ({keyword} 포함) |

#### 옵션

| 옵션 | 설명 |
|------|------|
| `--container <selector>` | 상품 컨테이너 CSS 선택자 |
| `--name-selector <sel>` | 상품명 CSS 선택자 |
| `--price-selector <sel>` | 가격 CSS 선택자 |
| `--from-file <path>` | JSON 설정 파일에서 읽기 |

#### 예시

```bash
# 기본 추가
plaprice shop add "쿠팡" "https://www.coupang.com/np/search?q={keyword}" \
  --container ".search-product" \
  --name-selector ".name" \
  --price-selector ".price-value"

# 파일에서 추가
plaprice shop add --from-file shop-config.json
```

### 2.3 상점 삭제: `shop remove`

```bash
plaprice shop remove <shop_id>
```

#### 인자

| 인자 | 필수 | 설명 |
|------|------|------|
| `<shop_id>` | ✅ | 삭제할 상점 ID 또는 이름 |

#### 옵션

| 옵션 | 설명 |
|------|------|
| `--force` | 확인 없이 삭제 |

### 2.4 상점 상세 조회: `shop show`

```bash
plaprice shop show <shop_id>
```

상점의 상세 설정 정보를 표시한다.

### 2.5 상점 활성화/비활성화: `shop enable` / `shop disable`

```bash
plaprice shop enable <shop_id>
plaprice shop disable <shop_id>
```

---

## 3. 설정 명령어: `config`

### 3.1 설정 경로 표시: `config path`

```bash
plaprice config path
```

출력: `/home/user/.plaprice/`

### 3.2 설정 초기화: `config init`

```bash
plaprice config init [--force]
```

설정 디렉토리 및 기본 파일 생성.

---

## 4. 테스트 명령어: `test`

상점 설정을 테스트한다.

```bash
plaprice test <shop_id> [keyword]
```

#### 인자

| 인자 | 필수 | 설명 |
|------|------|------|
| `<shop_id>` | ✅ | 테스트할 상점 ID |
| `[keyword]` | ❌ | 테스트 검색어 (기본: "test") |

#### 출력

- 연결 성공 여부
- 선택자 매칭 결과
- 샘플 파싱 결과 (있는 경우)

---

## JSON 출력 모드

`--json` 옵션 사용 시 모든 출력이 JSON 형식으로 변환된다.

### search 명령 JSON 출력 예시

```json
{
  "success": true,
  "query": {
    "keyword": "무선 마우스",
    "shop_ids": null
  },
  "results": [
    {
      "shop_id": "550e8400-e29b-41d4-a716-446655440000",
      "shop_name": "쿠팡",
      "product_name": "로지텍 무선 마우스",
      "price": 25000,
      "price_text": "₩25,000",
      "stock_status": "IN_STOCK",
      "product_url": "https://...",
      "crawled_at": "2025-12-30T10:05:00Z"
    }
  ],
  "errors": [],
  "stats": {
    "total_shops": 3,
    "success_shops": 3,
    "total_results": 5,
    "elapsed_seconds": 1.2
  }
}
```

---

## 에러 메시지 형식

모든 에러 메시지는 한국어로 표시되며, 다음 형식을 따른다:

```
[오류] {오류 유형}: {상세 메시지}

예시:
[오류] 네트워크 오류: 쿠팡 접속 시간 초과 (30초)
[오류] 설정 오류: 상점 ID를 찾을 수 없습니다: abc123
[오류] 파싱 오류: 11번가 페이지 구조가 변경되었습니다
```
