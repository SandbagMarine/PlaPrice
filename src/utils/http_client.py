"""
HTTP 클라이언트 - requests 기반 HTTP 요청 처리

크롤링을 위한 HTTP 요청을 담당합니다.
"""

import warnings
from typing import Optional

import requests
from requests.exceptions import ConnectionError, HTTPError, Timeout


class HttpClientError(Exception):
    """HTTP 클라이언트 오류"""

    pass


class HttpClient:
    """
    HTTP 클라이언트

    크롤링을 위한 HTTP GET 요청을 수행합니다.
    """

    DEFAULT_TIMEOUT = 30
    DEFAULT_USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )

    def __init__(self, timeout: int = DEFAULT_TIMEOUT, verify_ssl: bool = True):
        """
        HTTP 클라이언트 초기화

        Args:
            timeout: 요청 타임아웃 (초)
            verify_ssl: SSL 인증서 검증 여부 (기본: True)
        """
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": self.DEFAULT_USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        })

    def get(
        self,
        url: str,
        headers: Optional[dict[str, str]] = None,
    ) -> requests.Response:
        """
        GET 요청 수행

        Args:
            url: 요청 URL
            headers: 추가 헤더

        Returns:
            응답 객체

        Raises:
            HttpClientError: 요청 실패 시
        """
        try:
            # SSL 검증 비활성화 시 경고 억제
            if not self.verify_ssl:
                warnings.filterwarnings('ignore', category=requests.packages.urllib3.exceptions.InsecureRequestWarning)
            
            response = self.session.get(
                url,
                headers=headers,
                timeout=self.timeout,
                verify=self.verify_ssl,
            )
            response.raise_for_status()
            return response

        except Timeout as e:
            raise HttpClientError(f"요청 타임아웃: {url} - {e}") from e

        except ConnectionError as e:
            raise HttpClientError(f"연결 오류: {url} - {e}") from e

        except HTTPError as e:
            raise HttpClientError(f"HTTP 오류 {e.response.status_code}: {url}") from e

        except requests.RequestException as e:
            raise HttpClientError(f"요청 실패: {url} - {e}") from e

    def get_html(
        self,
        url: str,
        headers: Optional[dict[str, str]] = None,
        encoding: Optional[str] = None,
    ) -> str:
        """
        HTML 컨텐츠 가져오기

        Args:
            url: 요청 URL
            headers: 추가 헤더
            encoding: 응답 인코딩 (예: 'euc-kr')

        Returns:
            HTML 문자열

        Raises:
            HttpClientError: 요청 실패 시
        """
        response = self.get(url, headers)
        if encoding:
            response.encoding = encoding
        return response.text
