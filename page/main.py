import configparser
import os

import pytest
#启动，从page开始执行
if __name__ == "__main__":
    pytest.main(["-s","-v","--alluredir=./reports",os.path.join(os.path.dirname(__file__),"page")])