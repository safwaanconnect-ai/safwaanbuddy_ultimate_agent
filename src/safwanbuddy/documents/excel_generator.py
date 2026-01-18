import openpyxl
from src.safwanbuddy.core.logging import logger

class ExcelGenerator:
    def create_spreadsheet(self, data: list, save_path: str):
        """
        data: list of lists (rows)
        """
        wb = openpyxl.Workbook()
        ws = wb.active
        
        for row in data:
            ws.append(row)
            
        wb.save(save_path)
        logger.info(f"Excel spreadsheet saved to {save_path}")

excel_generator = ExcelGenerator()
