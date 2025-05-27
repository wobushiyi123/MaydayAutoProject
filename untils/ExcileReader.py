import openpyxl
from log.logger import logger


class ExcelReader:
    def __init__(self, file_path):
        self.file_path = file_path

    def get_data(self, sheet_name):
        try:
            workbook = openpyxl.load_workbook(self.file_path)
            sheet = workbook[sheet_name]

            # 获取标题行
            headers = [cell.value for cell in sheet[1]]

            data = []
            for row in sheet.iter_rows(min_row=2, values_only=True):
                row_data = dict(zip(headers, row))
                # 确保所有字段都是字符串且不为None
                for key in row_data:
                    if row_data[key] is None:
                        row_data[key] = ""
                    row_data[key] = str(row_data[key])
                data.append(row_data)

            logger.debug(f"从Excel读取到{len(data)}条测试数据")
            return data
        except Exception as e:
            logger.error(f"读取Excel文件失败: {str(e)}")
            raise