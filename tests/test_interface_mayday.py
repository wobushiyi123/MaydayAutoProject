import pytest
import allure
from untils.request_utils import RequestUtil
from untils.test_data_loader import get_test_data


@allure.feature("登录模块")
class TestLogin:

    @allure.story("用户登录")
    @pytest.mark.parametrize("test_data", get_test_data("login"))
    def test_login(self, test_data):
        """测试登录接口"""
        with allure.step("准备测试数据"):
            url = test_data['URL'] + test_data['API']
            headers = test_data.get('Headers', {})
            body = test_data.get('Body', {})
            expected_status = test_data['ExpectedStatus']
            expected_response = test_data.get('ExpectedResponse', {})

        with allure.step("发送登录请求"):
            response = RequestUtil.send_request(
                method=test_data['Method'],
                url=url,
                headers=headers,
                json=body
            )

        with allure.step("验证响应"):
            assert response.status_code == expected_status
            if expected_response:
                response_json = response.json()
                for key, value in expected_response.items():
                    assert response_json.get(key) == value

        with allure.step("获取并存储token"):
            if response.status_code == 200:
                token = response.json().get('data', {}).get('token')
                if token:
                    RequestUtil.update_headers({'Authorization': f'Bearer {token}'})