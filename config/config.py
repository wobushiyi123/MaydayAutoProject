import os
from configparser import ConfigParser

import self

# 使用相对目录确定文件位置
_config_dir = os.path.dirname(__file__)
_config_file = os.path.join(_config_dir, "config.ini")


# 继承configparser,写一个将结果转为dict
class MyParser(ConfigParser):
    def as_dict(self):
        d = dict(self._sections)
        for k in d:
            d[k] = dict(d[k])
        return d

def _get_all_conf():
        # 创建管理对象
        _config = MyParser()
        result = {}
        if os.path.isfile(_config_file):
            try:
                _config.read(_config_file, encoding="UTF-8")
                result = _config.as_dict()
            except OSError:
                raise ValueError("Read config file failed:%s" % OSError)
        return result

        # 将个配置读取出来，放在变量中
config = _get_all_conf()
sys_config = config["sys"]
url = sys_config['base_url']
username = sys_config['user']
password = sys_config['pwd']
log_cfg = config['log']
smtp_cfg = config['smtp']
email_cfg = config['email']
wait_config = config['wait']
IMPLICIT_WAIT = wait_config['implicit_wait']
EXPLICIT_WAIT = wait_config['explicit_wait']
browser_config = config['browserconfig']
BROWSER_TYPE= browser_config['browsertype']
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))  # 向上回两级到根目录
DRIVER_DIR = os.path.join(PROJECT_ROOT, "driverFile", "chromedriver.exe")
HEADLESS_MODE = browser_config['headless_mode']
        # print(url)

if __name__ == '__main__':
    config = _get_all_conf()
    sys_config = config["sys"]
    url = sys_config['base_url']
    print(url)
    # dsddddds89376339
