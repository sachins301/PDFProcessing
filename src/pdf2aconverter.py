import subprocess
import PyPDF2

def convert_to_pdfa(input_pdf, output_pdf):
    gs_command = [
        r"D:\Projects\PDFProcessing\packages\gs10.03.1\bin\gswin64c.exe",
        "-dPDFA",
        "-dBATCH",
        "-dNOPAUSE",
        "-sProcessColorModel=DeviceCMYK",
        "-sDEVICE=pdfwrite",
        "-sPDFACompatibilityPolicy=1",
        f"-sOutputFile={output_pdf}",
        input_pdf
    ]

    subprocess.run(gs_command, check=True)

input_pdf = "../resources/test.pdf"
output_pdf = "../resources/output_pdfa2b.pdf"
convert_to_pdfa(input_pdf, output_pdf)
