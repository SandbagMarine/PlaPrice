"""
PlaPrice CLI 메인 모듈

명령줄 인터페이스를 제공합니다.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.table import Table

from src.crawlers.html_crawler import CrawlError, HtmlCrawler
from src.crawlers.multi_crawler import MultiShopCrawler
from src.display.table_renderer import TableRenderer
from src.models.shop import Shop, ShopSelectors, StockPatterns
from src.storage.shop_store import ShopStore, ShopStoreError


console = Console()


def parse_args(args: Optional[list[str]] = None) -> argparse.Namespace:
    """
    명령줄 인수 파싱

    Args:
        args: 명령줄 인수 리스트 (None이면 sys.argv 사용)

    Returns:
        파싱된 인수
    """
    parser = argparse.ArgumentParser(
        prog="plaprice",
        description="다중 상점 가격 크롤러 - 여러 상점에서 상품 가격을 비교합니다",
    )

    # 전역 옵션
    parser.add_argument(
        "--json",
        action="store_true",
        help="JSON 형식으로 출력",
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="최소한의 출력만 표시",
    )

    subparsers = parser.add_subparsers(dest="command", help="명령어")

    # search 명령어
    search_parser = subparsers.add_parser("search", help="상품 검색")
    search_parser.add_argument("keyword", help="검색 키워드")
    search_parser.add_argument(
        "--shop",
        "-s",
        help="특정 상점 ID로 검색 제한",
    )
    search_parser.add_argument(
        "--sort",
        action="store_true",
        help="가격순 정렬",
    )

    # shop 명령어
    shop_parser = subparsers.add_parser("shop", help="상점 관리")
    shop_subparsers = shop_parser.add_subparsers(dest="shop_command", help="상점 명령어")

    # shop list
    shop_subparsers.add_parser("list", help="상점 목록 표시")

    # shop add
    shop_add_parser = shop_subparsers.add_parser("add", help="상점 추가")
    shop_add_parser.add_argument("--name", "-n", required=True, help="상점 이름")
    shop_add_parser.add_argument("--url", "-u", required=True, help="기본 URL")
    shop_add_parser.add_argument(
        "--search-template",
        "-t",
        required=True,
        help="검색 URL 템플릿 ({keyword} 포함)",
    )
    shop_add_parser.add_argument("--container", "-c", required=True, help="상품 컨테이너 선택자")
    shop_add_parser.add_argument("--name-selector", required=True, help="상품명 선택자")
    shop_add_parser.add_argument("--price-selector", required=True, help="가격 선택자")
    shop_add_parser.add_argument("--link-selector", help="상품 링크 선택자")
    shop_add_parser.add_argument("--stock-selector", help="재고 상태 선택자")
    shop_add_parser.add_argument(
        "--no-ssl-verify",
        action="store_true",
        help="SSL 인증서 검증 비활성화 (인증서 문제 있는 사이트용)",
    )
    shop_add_parser.add_argument(
        "--keyword-encoding",
        help="검색 키워드 인코딩 (예: euc-kr). 기본값은 UTF-8",
    )

    # shop remove
    shop_remove_parser = shop_subparsers.add_parser("remove", help="상점 삭제")
    shop_remove_parser.add_argument("shop_id", help="삭제할 상점 ID")

    # shop show
    shop_show_parser = shop_subparsers.add_parser("show", help="상점 상세 정보")
    shop_show_parser.add_argument("shop_id", help="상점 ID")

    # shop enable
    shop_enable_parser = shop_subparsers.add_parser("enable", help="상점 활성화")
    shop_enable_parser.add_argument("shop_id", help="상점 ID")

    # shop disable
    shop_disable_parser = shop_subparsers.add_parser("disable", help="상점 비활성화")
    shop_disable_parser.add_argument("shop_id", help="상점 ID")

    # config 명령어
    config_parser = subparsers.add_parser("config", help="설정 관리")
    config_subparsers = config_parser.add_subparsers(dest="config_command", help="설정 명령어")

    # config path
    config_subparsers.add_parser("path", help="설정 디렉토리 경로 표시")

    # config init
    config_subparsers.add_parser("init", help="설정 초기화")

    # test 명령어
    test_parser = subparsers.add_parser("test", help="상점 설정 테스트")
    test_parser.add_argument("shop_id", help="테스트할 상점 ID")
    test_parser.add_argument("--keyword", "-k", default="테스트", help="테스트 검색 키워드")

    return parser.parse_args(args)


def run_search(
    keyword: str,
    shop_id: Optional[str] = None,
    sort_by_price: bool = False,
    store: Optional[ShopStore] = None,
    json_output: bool = False,
    quiet: bool = False,
) -> int:
    """
    검색 실행

    Args:
        keyword: 검색 키워드
        shop_id: 특정 상점 ID (없으면 모든 활성 상점)
        sort_by_price: 가격순 정렬
        store: ShopStore 인스턴스
        json_output: JSON 출력
        quiet: 조용한 모드

    Returns:
        종료 코드
    """
    if store is None:
        store = ShopStore()

    # 대상 상점 결정
    if shop_id:
        shop = store.get(shop_id)
        if not shop:
            console.print(f"[red]오류: 상점을 찾을 수 없습니다: {shop_id}[/red]")
            return 1
        shops = [shop]
    else:
        shops = store.list_active()

    if not shops:
        console.print("[yellow]등록된 상점이 없습니다. 'plaprice shop add'로 상점을 추가하세요.[/yellow]")
        return 0

    if not quiet:
        console.print(f"[dim]'{keyword}' 검색 중... ({len(shops)}개 상점)[/dim]")

    # 검색 실행
    crawler = MultiShopCrawler(shops)
    results, errors = crawler.search_with_errors(keyword)

    if sort_by_price:
        results = crawler._sort_by_price(results)

    # 결과 출력
    if json_output:
        import json
        output = [
            {
                "shop_id": r.shop_id,
                "shop_name": r.shop_name,
                "product_name": r.product_name,
                "price": r.price,
                "stock_status": r.stock_status.value,
                "product_url": r.product_url,
            }
            for r in results
        ]
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        renderer = TableRenderer()
        if len(shops) > 1:
            renderer.print_comparison(results, keyword)
        else:
            renderer.print_results(results, keyword)

    # 오류 표시
    for error in errors:
        console.print(f"[red]오류: {error}[/red]")

    return 0


def run_shop_list(
    store: Optional[ShopStore] = None,
    json_output: bool = False,
) -> int:
    """
    상점 목록 표시

    Args:
        store: ShopStore 인스턴스
        json_output: JSON 출력

    Returns:
        종료 코드
    """
    if store is None:
        store = ShopStore()

    shops = store.list_all()

    if json_output:
        import json
        output = [
            {
                "id": s.id,
                "name": s.name,
                "base_url": s.base_url,
                "enabled": s.enabled,
            }
            for s in shops
        ]
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return 0

    if not shops:
        console.print("[yellow]등록된 상점이 없습니다.[/yellow]")
        return 0

    table = Table(title="등록된 상점", show_header=True, header_style="bold cyan")
    table.add_column("ID", style="dim", width=36)
    table.add_column("이름", style="blue", width=20)
    table.add_column("URL", style="white", width=40)
    table.add_column("상태", width=10)

    for shop in shops:
        status = "[green]활성[/green]" if shop.enabled else "[red]비활성[/red]"
        table.add_row(shop.id, shop.name, shop.base_url, status)

    console.print(table)
    return 0


def run_shop_add(
    name: str,
    url: str,
    search_template: str,
    container: str,
    name_selector: str,
    price_selector: str,
    link_selector: Optional[str] = None,
    stock_selector: Optional[str] = None,
    verify_ssl: bool = True,
    keyword_encoding: Optional[str] = None,
    store: Optional[ShopStore] = None,
) -> int:
    """
    상점 추가

    Returns:
        종료 코드
    """
    if store is None:
        store = ShopStore()

    try:
        selectors = ShopSelectors(
            product_container=container,
            product_name=name_selector,
            product_price=price_selector,
            product_link=link_selector,
            stock_status=stock_selector,
        )

        shop = Shop(
            name=name,
            base_url=url,
            search_url_template=search_template,
            selectors=selectors,
            verify_ssl=verify_ssl,
            keyword_encoding=keyword_encoding,
        )

        store.add(shop)
        console.print(f"[green]상점이 추가되었습니다: {shop.name} (ID: {shop.id})[/green]")
        return 0

    except Exception as e:
        console.print(f"[red]오류: {e}[/red]")
        return 1


def run_shop_remove(
    shop_id: str,
    store: Optional[ShopStore] = None,
) -> int:
    """
    상점 삭제

    Returns:
        종료 코드
    """
    if store is None:
        store = ShopStore()

    shop = store.get(shop_id)
    if not shop:
        console.print(f"[red]오류: 상점을 찾을 수 없습니다: {shop_id}[/red]")
        return 1

    store.remove(shop_id)
    console.print(f"[green]상점이 삭제되었습니다: {shop.name}[/green]")
    return 0


def run_shop_show(
    shop_id: str,
    store: Optional[ShopStore] = None,
    json_output: bool = False,
) -> int:
    """
    상점 상세 정보 표시

    Returns:
        종료 코드
    """
    if store is None:
        store = ShopStore()

    shop = store.get(shop_id)
    if not shop:
        console.print(f"[red]오류: 상점을 찾을 수 없습니다: {shop_id}[/red]")
        return 1

    if json_output:
        import json
        print(shop.model_dump_json(indent=2))
        return 0

    console.print(f"\n[bold]{shop.name}[/bold]")
    console.print(f"  ID: {shop.id}")
    console.print(f"  URL: {shop.base_url}")
    console.print(f"  검색 템플릿: {shop.search_url_template}")
    console.print(f"  상태: {'활성' if shop.enabled else '비활성'}")
    console.print(f"\n  [dim]선택자:[/dim]")
    console.print(f"    컨테이너: {shop.selectors.product_container}")
    console.print(f"    상품명: {shop.selectors.product_name}")
    console.print(f"    가격: {shop.selectors.product_price}")
    if shop.selectors.product_link:
        console.print(f"    링크: {shop.selectors.product_link}")
    if shop.selectors.stock_status:
        console.print(f"    재고: {shop.selectors.stock_status}")

    return 0


def run_shop_enable(
    shop_id: str,
    enabled: bool,
    store: Optional[ShopStore] = None,
) -> int:
    """
    상점 활성화/비활성화

    Returns:
        종료 코드
    """
    if store is None:
        store = ShopStore()

    shop = store.get(shop_id)
    if not shop:
        console.print(f"[red]오류: 상점을 찾을 수 없습니다: {shop_id}[/red]")
        return 1

    store.set_enabled(shop_id, enabled)
    status = "활성화" if enabled else "비활성화"
    console.print(f"[green]상점이 {status}되었습니다: {shop.name}[/green]")
    return 0


def run_config_path(store: Optional[ShopStore] = None) -> int:
    """
    설정 디렉토리 경로 표시

    Returns:
        종료 코드
    """
    if store is None:
        store = ShopStore()

    console.print(f"설정 디렉토리: {store.config_dir}")
    return 0


def run_test(
    shop_id: str,
    keyword: str = "테스트",
    store: Optional[ShopStore] = None,
) -> int:
    """
    상점 설정 테스트

    Returns:
        종료 코드
    """
    if store is None:
        store = ShopStore()

    shop = store.get(shop_id)
    if not shop:
        console.print(f"[red]오류: 상점을 찾을 수 없습니다: {shop_id}[/red]")
        return 1

    console.print(f"[dim]'{keyword}'로 {shop.name} 테스트 중...[/dim]")

    try:
        crawler = HtmlCrawler(shop)
        results = crawler.search(keyword)

        console.print(f"[green]✓ 크롤링 성공! {len(results)}개 상품 발견[/green]")

        if results:
            renderer = TableRenderer()
            renderer.print_results(results[:5], keyword)  # 최대 5개만 표시

        return 0

    except CrawlError as e:
        console.print(f"[red]✗ 크롤링 실패: {e}[/red]")
        return 1


def main(args: Optional[list[str]] = None) -> int:
    """
    CLI 메인 진입점

    Args:
        args: 명령줄 인수

    Returns:
        종료 코드
    """
    parsed = parse_args(args)

    if parsed.command is None:
        parse_args(["--help"])
        return 0

    json_output = getattr(parsed, "json", False)
    quiet = getattr(parsed, "quiet", False)

    if parsed.command == "search":
        return run_search(
            keyword=parsed.keyword,
            shop_id=getattr(parsed, "shop", None),
            sort_by_price=getattr(parsed, "sort", False),
            json_output=json_output,
            quiet=quiet,
        )

    elif parsed.command == "shop":
        if parsed.shop_command == "list":
            return run_shop_list(json_output=json_output)
        elif parsed.shop_command == "add":
            return run_shop_add(
                name=parsed.name,
                url=parsed.url,
                search_template=parsed.search_template,
                container=parsed.container,
                name_selector=parsed.name_selector,
                price_selector=parsed.price_selector,
                link_selector=getattr(parsed, "link_selector", None),
                stock_selector=getattr(parsed, "stock_selector", None),
                verify_ssl=not getattr(parsed, "no_ssl_verify", False),
                keyword_encoding=getattr(parsed, "keyword_encoding", None),
            )
        elif parsed.shop_command == "remove":
            return run_shop_remove(parsed.shop_id)
        elif parsed.shop_command == "show":
            return run_shop_show(parsed.shop_id, json_output=json_output)
        elif parsed.shop_command == "enable":
            return run_shop_enable(parsed.shop_id, True)
        elif parsed.shop_command == "disable":
            return run_shop_enable(parsed.shop_id, False)

    elif parsed.command == "config":
        if parsed.config_command == "path":
            return run_config_path()
        elif parsed.config_command == "init":
            console.print("[green]설정이 초기화되었습니다.[/green]")
            return 0

    elif parsed.command == "test":
        return run_test(
            shop_id=parsed.shop_id,
            keyword=getattr(parsed, "keyword", "테스트"),
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
