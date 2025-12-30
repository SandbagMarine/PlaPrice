<!--
Sync Impact Report
- Version change: (신규) → 1.0.0
- Modified principles: N/A (최초 생성)
- Added sections:
    - 핵심 원칙 (Core Principles): 테스트 우선 개발, 한국어 사용
    - 아키텍처 제약 및 표준 (Architectural Constraints & Standards)
    - 언어 및 문서화 정책 (Language and Documentation Policy)
    - 전달 워크플로우 및 품질 게이트 (Delivery Workflow & Quality Gates)
    - 거버넌스 (Governance)
- Removed sections: none
- Templates requiring updates:
    - ✅ .specify/templates/plan-template.md (기본 템플릿, 정합적)
    - ✅ .specify/templates/spec-template.md (기본 템플릿, 정합적)
    - ✅ .specify/templates/tasks-template.md (기본 템플릿, 정합적)
- Deferred TODOs: none
-->

# PlaPrice 헌법 (PlaPrice Constitution)

## 핵심 원칙 (Core Principles)

### I. 테스트 우선 개발 (Test-First Development, 변경 불가 원칙)

PlaPrice의 모든 기능은 테스트 우선(Test-First) 방식으로 개발해야 한다.
새로운 기능을 구현하기 전에 해당 기능의 테스트를 먼저 작성하고, 테스트가
실패하는 상태를 확인한 뒤, 테스트를 통과시키는 최소한의 코드를 구현한다.
Red-Green-Refactor 사이클을 엄격히 준수하며, 테스트 없이 프로덕션 코드를
작성하지 않는다.

**이유(Rationale)**: 테스트 우선 개발은 요구사항에 집중한 구현을 강제하고,
회귀(regression) 버그를 방지하며, 리팩토링 시 안전망을 제공한다. 크롤링
로직과 데이터 처리 파이프라인의 정확성을 보장하는 데 필수적이다.

### II. 한국어 사용 (Korean Language First)

PlaPrice 프로젝트의 모든 문서, 명세서, 설명, 코드 주석은 한국어를 기본
언어로 사용한다. 기술 용어는 필요에 따라 영어를 괄호로 병기할 수 있다.
사용자 인터페이스(UI)는 한국어로 작성하며, 프로젝트 내 의사소통(이슈,
PR, 회의 노트)도 한국어를 기본으로 한다.

**이유(Rationale)**: 프로젝트 참여자 및 사용자가 한국어 사용자이므로,
한국어로 문서화하면 의사소통의 명확성과 접근성이 향상된다. 코드
식별자(변수명, 함수명 등)는 국제 표준과 도구 호환성을 위해 영어를 사용한다.

## 아키텍처 제약 및 표준 (Architectural Constraints & Standards)

PlaPrice의 각 기능 구현은 플랜에서 다음 항목을 명시해야 한다.

- 사용 기술 스택(technology stack)
- 프로젝트 타입(project type)
- 성능 목표(performance goals)
- 제약(constraints), 스케일(scale), 스토리지(storage)

### 기본 기술 스택

- **언어**: Python 3.10 이상
- **플랫폼**: Windows 데스크탑 애플리케이션
- **주요 도메인**: 웹 크롤링, 데이터 처리, 데이터 가시화
- **배포 형태**: 개인 사용 기본, 필요 시 exe 파일로 외부 배포 가능
- **테스트 프레임워크**: pytest

### 프로젝트 구조

기본 프로젝트 구조는 단일 프로젝트(single project) 형태를 따른다.

```text
src/
├── crawlers/      # 웹 크롤링 모듈
├── processors/    # 데이터 처리/변환 모듈
├── visualizers/   # 데이터 가시화 모듈
├── ui/            # 사용자 인터페이스
├── models/        # 데이터 모델
└── utils/         # 공통 유틸리티

tests/
├── unit/          # 단위 테스트
├── integration/   # 통합 테스트
└── fixtures/      # 테스트 데이터/픽스처
```

플랜에서 선택한 프로젝트 구조는 실제 코드 레이아웃과 일치해야 한다.
권장 구조에서 벗어나는 경우, 그 이유는 반드시 플랜의 "복잡도 추적
(Complexity Tracking)" 섹션에 정당성을 포함하여 기록해야 한다.

스펙(specifications)은 사용자 스토리를 독립적으로 테스트 가능한 여정으로
정의해야 하며, 명확한 인수 시나리오(acceptance scenarios)와 측정 가능한
성공 기준(measurable success criteria)을 포함해야 한다. 요구사항은 모두
테스트 가능한 문장으로 작성해야 하고, 모호한 요구사항은 "명확화 필요
(NEEDS CLARIFICATION)"로 표시해야 한다.

태스크(tasks)는 사용자 스토리와 단계(Phase)를 기준으로 구성해야 한다.
최소한 다음 단계를 구분한다.

- 초기 설정(Setup)
- 기초(Foundational)
- 스토리별 구현(Per Story)
- 마무리/폴리싱(Polish)

## 언어 및 문서화 정책 (Language and Documentation Policy)

PlaPrice 프로젝트 전반에서 사용하는 언어와 문서화 방식은 다음 규칙을 따른다.

1. **문서/명세/설명**: 모든 문서, 명세서, 설명 문서는 기본적으로 한국어로
    작성한다. 필요한 경우 기술 용어의 영어 표기를 괄호로 병기한다.
2. **코드 주석(comment)**: 코드 주석은 한국어로 작성한다. 기술 용어는
    필요에 따라 한국어-영어 병행 표기를 사용한다.
3. **기술 용어(Technical Terms)**: 핵심 기술 용어는 한국어와 영어를
    함께 표기할 수 있다. 예: "크롤러(crawler)", "파서(parser)",
    "데이터프레임(DataFrame)".
4. **에러 메시지 및 로그(Error/Log Messages)**: 런타임 에러 메시지,
    로그 문자열 등 실제 코드에 포함된 메시지는 원본 언어(주로 영어)를
    유지한다. 다만, 해당 메시지의 의미와 대응 방법을 설명하는 문서와
    주석은 한국어로 작성한다.
5. **사용자 인터페이스(UI)**: 사용자가 직접 보는 UI 텍스트는 기본적으로
    한국어로 작성한다. 다국어 지원이 필요한 경우 별도의 현지화 정책을
    스펙/플랜에서 정의한다.
6. **프로젝트 내 의사소통**: 이 프로젝트와 관련된 이슈, PR 설명, 회의
    노트, 내부 문서는 기본적으로 한국어로 작성한다. 외부 이해관계자나
    도구 요구에 따라 영어가 필요한 경우, 한국어 설명을 우선 제공하고
    필요에 따라 영어를 병기한다.
7. **단계별 문서화**: 스펙 작성, 플랜 수립, 태스크 정의, 구현 및 테스트,
    리뷰/회고 등 각 단계에서 최소한의 문서화 항목을 남겨야 한다. 각
    단계별 필수 문서화 항목은 `.specify/templates/` 하위 템플릿에 따라
    작성한다.

다음 항목은 예외로 한다.

1. **코드 자체**: 변수명, 함수명, 클래스명, 모듈명 등 코드 식별자는 영어로
    작성한다.
2. **공식 문서 및 명령어**: 외부 공식 문서, 명령어, CLI 옵션 이름 등은
    원본 언어(주로 영어)를 유지한다.
3. **외부 라이브러리 API**: Python 라이브러리(requests, BeautifulSoup,
    pandas, matplotlib 등) API 및 메서드 이름은 원본 표기를 유지한다.
4. **명시적 요청**: 사용자가 특정 산출물에 대해 다른 언어 사용을 명시적으로
    요청하는 경우, 해당 요청을 플랜 또는 PR 설명에 기록하고 합의된 범위
    내에서 다른 언어를 사용한다.

## 전달 워크플로우 및 품질 게이트 (Delivery Workflow & Quality Gates)

PlaPrice 기능에 대한 기본 전달(workflow) 흐름은 다음과 같다.

1. `spec.md`를 생성하거나 갱신하여 사용자 시나리오, 요구사항, 성공 기준을
    정의한다.
2. `plan.md`를 생성·정제한다. 이때 기술 컨텍스트(Technical Context),
    헌법 체크(Constitution Check), 프로젝트 구조(Project Structure)를 포함한다.
3. 단계(Phase)와 사용자 스토리 기준으로 정리된 `tasks.md`를 생성한다.
    각 태스크에는 고유 ID, 스토리 라벨, 파일 경로를 명시한다.
4. 태스크를 다음 순서로 수행한다: 초기 설정 → 기초 → 사용자 스토리(우선순위
    순) → 마무리/폴리싱. 병렬 수행 규칙을 준수한다.
5. 각 사용자 스토리에 대해, 테스트를 먼저 작성하고 실패를 확인한 뒤,
    구현하여 테스트를 통과시키며, 다른 스토리와 독립적으로 해당 스토리를
    검증한 뒤 다음 스토리로 이동한다.

`plan.md` 안의 헌법 체크(Constitution Check) 항목은 리서치를 시작하기 전
명시적으로 검토해야 하며, 설계 이후에 다시 확인해야 한다. 위반 사항이
있는 경우 해당 사실과 정당성을 기록해야 한다.

## 거버넌스 (Governance)

이 헌법은 PlaPrice의 모든 기능 스펙(specifications), 플랜(plans), 태스크
목록(task lists)에 적용된다. 충돌이 발생하는 경우, 이 헌법이
애드혹(ad-hoc) 방식보다 우선한다.

이 헌법의 개정(amendment)은 다음 조건을 만족해야 한다.

- `.specify/memory/constitution.md` 파일의 버전을
    시맨틱 버전(semantic versioning, MAJOR.MINOR.PATCH)에 따라 증가시킨다.
    - MAJOR: 핵심 원칙의 제거 또는 근본적 재정의
    - MINOR: 새 원칙/섹션 추가 또는 기존 지침의 실질적 확장
    - PATCH: 명확화, 문구 수정, 오타 교정 등 비의미적 개선
- `.specify/templates/` 하위의 관련 템플릿을 업데이트하여, 여기서 정의한
    원칙과 워크플로우와의 정합성을 유지한다.
- 이 헌법의 최상단 주석에 Sync Impact Report를 포함하여, 버전 변경과
    변경 범위를 간단히 설명한다.

리뷰어는 새로운 기능, 플랜, 태스크가 이 헌법에서 정의한 핵심 원칙,
아키텍처 제약, 전달 워크플로우, 언어/문서화 정책을 준수하는지 확인할
책임이 있다.

**Version**: 1.0.0 | **Ratified**: 2025-12-30 | **Last Amended**: 2025-12-30
