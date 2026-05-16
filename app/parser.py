from PyPDF2 import PdfReader
from docx import Document


def parse_pdf(path):

    reader = PdfReader(path)

    text = ""

    for page in reader.pages:

        extracted = page.extract_text()

        if extracted:
            text += extracted + "\n"

    return text


def parse_docx(path):

    doc = Document(path)

    return "\n".join(
        [p.text for p in doc.paragraphs]
    )
