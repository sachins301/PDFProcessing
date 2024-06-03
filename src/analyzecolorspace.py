import fitz  # PyMuPDF

# Mapping of color space numbers to names based on PyMuPDF's internal representation
COLOR_SPACE_NAMES = {
    0: "DeviceGray",
    1: "DeviceRGB",
    2: "DeviceCMYK",
    3: "CalGray",
    4: "CalRGB",
    5: "Lab",
    6: "ICCBased",
    7: "Separation",
    8: "DeviceN",
    9: "Indexed",
    10: "Pattern",
}


def analyze_pdf_color_spaces(pdf_path):
    doc = fitz.open(pdf_path)
    color_spaces = set()

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        for img in page.get_images(full=True):
            xref = img[0]
            image = doc.extract_image(xref)
            if image:
                color_space = image.get("colorspace")
                if color_space is not None:
                    color_spaces.add(color_space)

    return color_spaces


pdf_path = "../resources/test.pdf"
color_spaces = analyze_pdf_color_spaces(pdf_path)

if not color_spaces:
    print("No images or color information found in the PDF.")
else:
    print("Color spaces used in the PDF:")
    for space in color_spaces:
        color_space_name = COLOR_SPACE_NAMES.get(space, f"Unknown ({space})")
        print(color_space_name)
