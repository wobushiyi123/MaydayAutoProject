import openpyxl
import json
from pathlib import Path


def load_test_data_from_excel(file_path, sheet_name):
    """从Excel加载测试数据"""
    workbook = openpyxl.load_workbook(file_path)
    sheet = workbook[sheet_name]

    headers = [cell.value for cell in sheet[1]]
    test_cases = []

    for row in sheet.iter_rows(min_row=2, values_only=True):
        test_case = dict(zip(headers, row))
        # 转换JSON字符串为字典
        for field in ['Headers', 'Params', 'Body', 'ExpectedResponse']:
            if test_case[field] and isinstance(test_case[field], str):
                test_case[field] = json.loads(test_case[field])
        test_cases.append(test_case)

    return test_cases


def get_test_data(module_name):
    """获取指定模块的测试数据"""
    excel_path = Path(__file__).parent / 'mayday_test_cases.xlsx'
    all_data = load_test_data_from_excel(excel_path, 'TestCases')
    return [data for data in all_data if data['Module'] == module_name]