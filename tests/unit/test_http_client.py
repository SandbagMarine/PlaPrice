"""
테스트: HTTP 클라이언트

TDD에 따라 구현 전 테스트 먼저 작성.
"""

import pytest
import responses
from responses import matchers


class TestHttpClient:
    """HttpClient 테스트"""

    @responses.activate
    def test_get_요청_성공(self):
        """GET 요청이 성공적으로 수행됨"""
        from src.utils.http_client import HttpClient

        responses.add(
            responses.GET,
            "https://example.com/page",
            body="<html><body>Hello</body></html>",
            status=200,
        )

        client = HttpClient()
        response = client.get("https://example.com/page")

        assert response.status_code == 200
        assert "Hello" in response.text

    @responses.activate
    def test_get_요청_타임아웃(self):
        """타임아웃 발생 시 예외 처리"""
        from src.utils.http_client import HttpClient, HttpClientError
        from requests.exceptions import Timeout

        responses.add(
            responses.GET,
            "https://example.com/slow",
            body=Timeout("Connection timed out"),
        )

        client = HttpClient(timeout=5)

        with pytest.raises(HttpClientError) as exc_info:
            client.get("https://example.com/slow")

        assert "타임아웃" in str(exc_info.value) or "timeout" in str(exc_info.value).lower()

    @responses.activate
    def test_get_요청_http_오류(self):
        """HTTP 오류 응답 처리 (4xx, 5xx)"""
        from src.utils.http_client import HttpClient, HttpClientError

        responses.add(
            responses.GET,
            "https://example.com/notfound",
            status=404,
        )

        client = HttpClient()

        with pytest.raises(HttpClientError) as exc_info:
            client.get("https://example.com/notfound")

        assert "404" in str(exc_info.value)

    @responses.activate
    def test_user_agent_설정(self):
        """User-Agent 헤더가 적절히 설정됨"""
        from src.utils.http_client import HttpClient

        responses.add(
            responses.GET,
            "https://example.com/check-ua",
            body="OK",
            status=200,
        )

        client = HttpClient()
        response = client.get("https://example.com/check-ua")

        assert response.status_code == 200
        # 요청에 User-Agent가 포함되었는지 확인
        assert len(responses.calls) == 1
        assert "User-Agent" in responses.calls[0].request.headers

    @responses.activate
    def test_커스텀_헤더_추가(self):
        """커스텀 헤더 추가 가능"""
        from src.utils.http_client import HttpClient

        responses.add(
            responses.GET,
            "https://example.com/custom",
            body="OK",
            status=200,
        )

        client = HttpClient()
        response = client.get(
            "https://example.com/custom",
            headers={"X-Custom-Header": "test-value"},
        )

        assert response.status_code == 200

    @responses.activate
    def test_연결_오류_처리(self):
        """네트워크 연결 오류 처리"""
        from src.utils.http_client import HttpClient, HttpClientError
        from requests.exceptions import ConnectionError

        responses.add(
            responses.GET,
            "https://example.com/unreachable",
            body=ConnectionError("Connection refused"),
        )

        client = HttpClient()

        with pytest.raises(HttpClientError) as exc_info:
            client.get("https://example.com/unreachable")

        assert "연결" in str(exc_info.value) or "connection" in str(exc_info.value).lower()

    def test_기본_타임아웃_설정(self):
        """기본 타임아웃 값 설정"""
        from src.utils.http_client import HttpClient

        client = HttpClient()
        assert client.timeout == 30  # 기본 30초

        client_custom = HttpClient(timeout=10)
        assert client_custom.timeout == 10

    @responses.activate
    def test_html_가져오기(self):
        """HTML 컨텐츠 가져오기"""
        from src.utils.http_client import HttpClient

        html_content = """
        <!DOCTYPE html>
        <html>
        <head><title>테스트</title></head>
        <body>
            <div class="product">상품1</div>
        </body>
        </html>
        """

        responses.add(
            responses.GET,
            "https://example.com/products",
            body=html_content,
            status=200,
            content_type="text/html; charset=utf-8",
        )

        client = HttpClient()
        html = client.get_html("https://example.com/products")

        assert "상품1" in html
        assert "<!DOCTYPE html>" in html
