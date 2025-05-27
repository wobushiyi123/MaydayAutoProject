import requests
from allure import step


class RequestUtil:
    _session = requests.Session()
    _base_headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mayday-API-Test"
    }

    @classmethod
    def send_request(cls, method, url, headers=None, params=None, json=None, data=None):
        """发送HTTP请求"""
        merged_headers = {**cls._base_headers, **(headers or {})}

        with step(f"请求 {method} {url}"):
            response = cls._session.request(
                method=method.upper(),
                url=url,
                headers=merged_headers,
                params=params,
                json=json,
                data=data
            )

        with step(f"响应状态码: {response.status_code}"):
            return response

    @classmethod
    def update_headers(cls, new_headers):
        """更新全局请求头"""
        cls._base_headers.update(new_headers)