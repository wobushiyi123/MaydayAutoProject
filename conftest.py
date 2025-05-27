import os
import subprocess
import time
import webbrowser
import shutil
from datetime import datetime

import allure
import pytest
from driver.driverUntil import DriverUtil
from page.publish import Publish
from untils.ExcileReader import ExcelReader
from page.login import LoginPage
from config.config import url
from log.logger import logger, log_test_start, log_test_end
from config.config import PROJECT_ROOT
from pathlib import Path


# 必须的 pytest 钩子
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)


@pytest.fixture
def test_data(request):
    """专门用于接收参数化数据的fixture"""
    return request.param


@pytest.fixture(scope="function")
def setup(request):
    """为每条测试数据创建独立的截图文件夹"""
    # 获取测试数据
    test_data = getattr(request, "param", None)

    # 生成唯一的测试用例标识
    if test_data:
        # 使用topic作为主要标识，如果没有则使用id或哈希值
        topic = test_data.get('topic', '').strip()
        case_id = test_data.get('id', '').strip()

        if topic:
            folder_name = f"{topic}_{datetime.now().strftime('%m%d_%H%M%S')}"
        elif case_id:
            folder_name = f"case_{case_id}_{datetime.now().strftime('%m%d_%H%M%S')}"
        else:
            folder_name = f"test_{abs(hash(str(test_data)))}_{datetime.now().strftime('%m%d_%H%M%S')}"
    else:
        folder_name = f"default_{datetime.now().strftime('%m%d_%H%M%S')}"

    # 创建截图目录（在项目根目录下）
    screenshot_base_dir = Path(PROJECT_ROOT) / "screenshots"
    screenshot_dir = screenshot_base_dir / folder_name
    screenshot_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"为测试用例创建截图目录: {screenshot_dir}")

    # 存储到测试类实例
    request.cls.screenshot_dir = screenshot_dir
    request.cls.current_data = test_data
    request.cls.test_case_name = folder_name

    # 初始化浏览器
    driver = DriverUtil.get_driver("chrome")
    request.cls.driver = driver

    # 在测试开始时创建一个测试信息文件
    info_file = screenshot_dir / "test_info.txt"
    with open(info_file, "w", encoding="utf-8") as f:
        f.write(f"测试用例信息\n")
        f.write(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"测试数据: {test_data}\n")
        f.write(f"截图目录: {screenshot_dir}\n")
        f.write("-" * 50 + "\n")

    yield

    # 测试后清理
    try:
        # 在测试结束时更新测试信息
        with open(info_file, "a", encoding="utf-8") as f:
            f.write(f"测试结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            # 获取测试结果
            if hasattr(request.node, 'rep_call'):
                result = "通过" if request.node.rep_call.passed else "失败"
                f.write(f"测试结果: {result}\n")

        driver.quit()
    except Exception as e:
        logger.error(f"清理过程中出现错误: {str(e)}")
        try:
            driver.quit()
        except:
            pass


@pytest.mark.usefixtures("setup")
class TestMayday:
    TEST_DATA_PATH = Path(PROJECT_ROOT) / "test_data" / "test.xlsx"

    @allure.title('文章发布测试 - {data.get("topic", "默认标题")}')
    @allure.feature("内容管理")
    @pytest.mark.parametrize("setup", ExcelReader(TEST_DATA_PATH).get_data("TEST1"), indirect=True)
    def test_process(self, request):
        """处理单条测试数据"""
        # 从fixture获取数据
        data = request.cls.current_data
        test_name = f"文章发布测试[{data.get('topic', '未命名')}]"

        log_test_start(test_name)

        # 添加测试用例信息到Allure报告
        with allure.step("测试用例信息"):
            allure.attach(str(data), name="测试数据", attachment_type=allure.attachment_type.JSON)
            allure.attach(str(self.screenshot_dir), name="截图目录", attachment_type=allure.attachment_type.TEXT)

        try:
            # 数据验证
            self._validate_test_data(data)
            logger.debug(f"测试数据详情: {data}")

            # 浏览器操作
            self.driver.maximize_window()
            self.driver.get(url)
            self._take_screenshot("01_打开页面")

            # 登录流程
            self._login()

            # 发布文章
            self._publish_article(data)

            log_test_end(test_name, "通过")
            logger.info(f"测试用例 [{self.test_case_name}] 执行完成")

        except Exception as e:
            # 失败处理
            self._handle_test_failure(e, test_name)
            raise

    def _validate_test_data(self, data):
        """验证测试数据格式"""
        required_fields = ['topic', 'content']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            error_msg = f"测试数据缺少必要字段: {missing_fields}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        for field in required_fields:
            if not str(data[field]).strip():
                error_msg = f"字段'{field}'不能为空"
                logger.error(error_msg)
                raise ValueError(error_msg)

    def _login(self):
        """登录流程"""
        with allure.step("登录系统"):
            self._take_screenshot("02_登录前页面")
            LoginPage(self.driver).login_process()
            self._take_screenshot("03_登录完成")
            logger.info("登录步骤完成")

    def _publish_article(self, data):
        """发布文章流程"""
        with allure.step("发布文章"):
            self._take_screenshot("04_发布前页面")
            Publish(self.driver).click_write_article(data)
            self._take_screenshot("05_发布完成")
            logger.info("文章发布步骤完成")

    def _take_screenshot(self, step_name):
        """通用截图方法 - 带序号和描述的截图"""
        timestamp = datetime.now().strftime("%H%M%S")
        screenshot_filename = f"{step_name}_{timestamp}.png"
        screenshot_path = self.screenshot_dir / screenshot_filename

        try:
            # 保存截图
            self.driver.save_screenshot(str(screenshot_path))

            # 添加到Allure报告
            allure.attach.file(
                str(screenshot_path),
                name=step_name,
                attachment_type=allure.attachment_type.PNG
            )

            logger.info(f"截图已保存: {screenshot_filename}")
            return screenshot_path

        except Exception as e:
            logger.error(f"截图保存失败: {str(e)}")
            return None

    def _handle_test_failure(self, exception, test_name):
        """处理测试失败"""
        failure_time = datetime.now().strftime("%H%M%S")

        # 失败截图
        screenshot_path = self._take_screenshot(f"99_测试失败_{failure_time}")

        # 保存页面源码
        source_filename = f"99_页面源码_{failure_time}.html"
        source_path = self.screenshot_dir / source_filename
        try:
            with open(source_path, "w", encoding="utf-8") as f:
                f.write(self.driver.page_source)
            logger.info(f"页面源码已保存: {source_filename}")
        except Exception as e:
            logger.error(f"页面源码保存失败: {str(e)}")

        # 保存错误信息
        error_filename = f"99_错误信息_{failure_time}.txt"
        error_path = self.screenshot_dir / error_filename
        try:
            with open(error_path, "w", encoding="utf-8") as f:
                f.write(f"错误时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"错误信息: {str(exception)}\n")
                f.write(f"测试数据: {self.current_data}\n")
                f.write(f"当前URL: {self.driver.current_url}\n")
            logger.info(f"错误信息已保存: {error_filename}")
        except Exception as e:
            logger.error(f"错误信息保存失败: {str(e)}")

        # 记录日志
        logger.error(f"测试用例 [{self.test_case_name}] 执行失败: {str(exception)}")
        if screenshot_path:
            logger.error(f"失败截图: {screenshot_path}")

        # 附加到Allure
        try:
            allure.attach(
                self.driver.page_source,
                name="失败时页面源码",
                attachment_type=allure.attachment_type.HTML
            )
            allure.attach(
                str(exception),
                name="错误信息",
                attachment_type=allure.attachment_type.TEXT
            )
        except Exception as e:
            logger.error(f"Allure附件添加失败: {str(e)}")

        log_test_end(test_name, "失败")


def cleanup_old_results():
    """清理旧的测试结果"""
    try:
        # 清理Allure结果目录
        allure_results_dir = Path(PROJECT_ROOT) / "allure-results"
        if allure_results_dir.exists():
            shutil.rmtree(allure_results_dir)
            logger.info("已清理旧的Allure结果目录")

        # 清理Allure报告目录
        allure_report_dir = Path(PROJECT_ROOT) / "allure-report"
        if allure_report_dir.exists():
            shutil.rmtree(allure_report_dir)
            logger.info("已清理旧的Allure报告目录")

        # 注意：不清理screenshots目录，保留历史截图
        logger.info("清理完成，截图目录已保留")

    except Exception as e:
        logger.error(f"清理过程中出现错误: {str(e)}")


def generate_test_summary():
    """生成测试总结报告"""
    try:
        screenshots_dir = Path(PROJECT_ROOT) / "screenshots"
        if not screenshots_dir.exists():
            return

        summary_file = Path(PROJECT_ROOT) / f"test_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

        with open(summary_file, "w", encoding="utf-8") as f:
            f.write("=" * 60 + "\n")
            f.write("UI自动化测试执行总结\n")
            f.write("=" * 60 + "\n")
            f.write(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"项目根目录: {PROJECT_ROOT}\n")
            f.write(f"截图根目录: {screenshots_dir}\n")
            f.write("-" * 60 + "\n")

            # 统计测试用例数量
            test_dirs = [d for d in screenshots_dir.iterdir() if d.is_dir()]
            f.write(f"执行的测试用例数量: {len(test_dirs)}\n")
            f.write("-" * 60 + "\n")

            # 列出每个测试用例的详情
            f.write("测试用例详情:\n")
            for i, test_dir in enumerate(test_dirs, 1):
                f.write(f"{i}. {test_dir.name}\n")

                # 统计截图数量
                screenshots = list(test_dir.glob("*.png"))
                f.write(f"   截图数量: {len(screenshots)}\n")

                # 读取测试信息
                info_file = test_dir / "test_info.txt"
                if info_file.exists():
                    try:
                        with open(info_file, "r", encoding="utf-8") as info_f:
                            info_content = info_f.read()
                            # 提取关键信息
                            lines = info_content.split('\n')
                            for line in lines:
                                if '测试结果:' in line or '测试数据:' in line:
                                    f.write(f"   {line}\n")
                    except:
                        pass
                f.write("\n")

        logger.info(f"测试总结报告已生成: {summary_file}")

    except Exception as e:
        logger.error(f"生成测试总结时出现错误: {str(e)}")


def run_tests():
    """执行测试的主函数"""
    logger.info("开始执行UI自动化测试")

    # 1. 清理旧的结果
    cleanup_old_results()

    # 2. 准备目录
    allure_results_dir = Path(PROJECT_ROOT) / "allure-results"
    allure_report_dir = Path(PROJECT_ROOT) / "allure-report"

    allure_results_dir.mkdir(exist_ok=True)

    # 3. 执行 pytest 测试
    logger.info("开始执行pytest测试")
    exit_code = subprocess.call([
        "pytest",
        __file__,  # 使用当前文件
        "--alluredir", str(allure_results_dir),
        "-v",
        "--clean-alluredir",
        "--tb=short"  # 简化错误信息显示
    ])

    # 4. 生成测试总结
    generate_test_summary()

    # 5. 生成并打开 Allure 报告
    if exit_code in (0, 1):  # 0=成功, 1=部分失败
        try:
            logger.info("生成Allure报告")
            subprocess.call([
                "allure", "generate",
                str(allure_results_dir),
                "--output", str(allure_report_dir),
                "--clean"
            ])

            # 自动打开浏览器
            report_index = allure_report_dir / "index.html"
            if report_index.exists():
                webbrowser.open(f"file://{report_index.absolute()}")
                logger.info(f"Allure报告已生成并打开: {report_index}")
            else:
                logger.warning("Allure报告生成失败")

        except Exception as e:
            logger.error(f"生成Allure报告时出现错误: {str(e)}")
    else:
        logger.error("❌ 测试执行异常！")

    logger.info("测试执行完成")
    return exit_code


if __name__ == "__main__":
    run_tests()