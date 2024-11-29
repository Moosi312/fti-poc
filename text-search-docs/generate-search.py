import pymupdf
import re
from path import Path

def main():
    docs = Path('../assets/docs/pdf')
    text_folder = Path('./extracted-text')
    output = Path('./docs-by-indicator.json')

    text_folder.rmtree_p()
    text_folder.mkdir_p()

    file_amount = len(docs.files())

    for i, doc in enumerate(docs.files()):
        print(f"\r[{i:>3}/{file_amount:>3}] Extract {doc.name}", end='')
        extract_text(doc, text_folder / '.'.join(doc.name.split('.')[:-1] + ['txt']))

    print(f"\r[{file_amount:>3}/{file_amount:>3}] Finished extracting text from PDFs")

def extract_text(doc_path: Path, text_path: Path):
    doc = pymupdf.open(doc_path)
    with open(text_path, 'wb') as f:
        for page in doc:
            text = page.get_text().encode('utf-8')
            f.write(text)


if __name__ == "__main__":
    main()