import pandas as pd
from fpdf import FPDF


class FileExporter:
    def export(self, data: pd.DataFrame, file_path: str) -> str:
        raise NotImplementedError("Export method must be implemented.")


class ExcelExporter(FileExporter):
    def export(self, data: pd.DataFrame, file_path: str) -> str:
        data.to_excel(file_path, index=False, engine="xlsxwriter")
        return file_path


class PDFExporter(FileExporter):
    def export(self, data: pd.DataFrame, file_path: str) -> str:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        for _, row in data.iterrows():
            pdf.cell(200, 10, txt=", ".join(map(str, row.values)), ln=True)

        pdf.output(file_path)
        return file_path


class ExporterFactory:
    exporters: dict[str, FileExporter] = {"xls": ExcelExporter(), "pdf": PDFExporter()}

    @staticmethod
    def get_exporter(file_type: str) -> FileExporter:
        exporter = ExporterFactory.exporters.get(file_type)
        if not exporter:
            raise ValueError(f"Unsupported file type: {file_type}")
        return exporter
