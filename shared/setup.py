from path import Path
from pymupdf import pymupdf

USE_MODEL = "gpt-4o-mini"

def extract_text(extracted_text_folder: Path, pdf_folder: Path):
    extracted_text_folder.rmtree_p()
    extracted_text_folder.mkdir_p()

    file_amount = len(pdf_folder.files())

    for i, doc_path in enumerate(pdf_folder.files()):
        print(f"\r[{i:>3}/{file_amount:>3}] Extract {doc_path.name}", end='')
        output = extracted_text_folder / '.'.join(doc_path.name.split('.')[:-1] + ['txt'])
        doc = pymupdf.open(doc_path)
        with open(output, 'wb') as f:
            for page in doc:
                text = page.get_text().encode('utf-8')
                f.write(text)

    print(f"\r[{file_amount:>3}/{file_amount:>3}] Finished extracting text from PDFs")