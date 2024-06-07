import subprocess
import PyPDF2

def convert_to_pdfa(input_pdf, output_pdf):
    gs_command = [
        r"D:\Projects\PDFProcessing\packages\gs10.03.1\bin\gswin64c.exe",
        "-dPDFA=2",
        "-sDEVICE=pdfwrite",
        "-sColorConversionStrategy=UseDeviceIndependentColor",
        "-dPDFACompatibilityPolicy=1",
        f"-o{output_pdf}",
        f"-f{input_pdf}"
    ]
    try:
        subprocess.run(gs_command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        print(f"Command output: {e.output}")

input_pdf = "../resources/test.pdf"
output_pdf = "../resources/output_pdfa2b.pdf"
icc_profile_path = r"../packages/Adobe ICC Profiles (end-user)/Generic Gray Gamma 2.2 Profile.icc"  # Path to the ICC profile
convert_to_pdfa(input_pdf, output_pdf)
