import openpyxl
from openpyxl.utils import get_column_letter
from src.safwanbuddy.core import logger
import os

class ExcelGenerator:
    def __init__(self):
        self.output_dir = "output/spreadsheets"
        os.makedirs(self.output_dir, exist_ok=True)

    def create_spreadsheet(self, data: list, filename: str = "spreadsheet.xlsx", sheet_name: str = "Sheet1"):
        """
        Creates an Excel spreadsheet.
        data is a list of lists (rows).
        """
        try:
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = sheet_name

            for row in data:
                ws.append(row)

            # Auto-adjust column widths
            for column_cells in ws.columns:
                length = max(len(str(cell.value)) for cell in column_cells)
                ws.column_dimensions[get_column_letter(column_cells[0].column)].width = length + 2

            path = os.path.join(self.output_dir, filename)
            wb.save(path)
            logger.info(f"Excel spreadsheet saved to {path}")
            return path
        except Exception as e:
            logger.error(f"Error creating Excel spreadsheet: {e}")
            return None

excel_generator = ExcelGenerator()
