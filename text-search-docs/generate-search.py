import json
import itertools
import pymupdf
from thefuzz import fuzz
from path import Path


TARGET_SCORE = 80


def main():
    docs = Path('../assets/docs/pdf')
    text_folder = Path('./extracted-text')
    output = Path('./docs-by-indicator.json')

    strings = json.loads(Path('../assets/data/str.json').read_text())
    labels = json.loads(Path('../assets/data/labels.json').read_text())
    indicators = get_indicators(strings, labels)

    extract_text(docs, text_folder)
    search_texts(text_folder, output, indicators)


def get_indicators(strings, labels):
    indicator_keys = list(itertools.chain.from_iterable(ind['i'] for ind in strings.values()))
    indicator_map = {i: labels[i]['short'] for i in indicator_keys}
    return indicator_map


def extract_text(doc_folder: Path, text_folder: Path):
    text_folder.rmtree_p()
    text_folder.mkdir_p()

    file_amount = len(doc_folder.files())

    for i, doc_path in enumerate(doc_folder.files()):
        print(f"\r[{i:>3}/{file_amount:>3}] Extract {doc_path.name}", end='')
        output = text_folder / '.'.join(doc_path.name.split('.')[:-1] + ['txt'])
        doc = pymupdf.open(doc_path)
        with open(output, 'wb') as f:
            for page in doc:
                text = page.get_text().encode('utf-8')
                f.write(text)

    print(f"\r[{file_amount:>3}/{file_amount:>3}] Finished extracting text from PDFs")


def search_texts(text_folder: Path, output: Path, indicators: dict[str: str]):
    output_file = {}
    ind_amount = len(indicators)
    for i, (key, name) in enumerate(indicators.items()):
        print(f"\r[{i:>3}/{ind_amount:>3}] Search for \"{name}\"", end='')
        for text in text_folder.files():
            if fuzz.partial_ratio(name, text.read_text()) > TARGET_SCORE:
                # if f"{text.stripext().name}" not in output_file:
                #     output_file[f"{text.stripext().name}"] = []
                # output_file[f"{text.stripext().name}"].append(key)
                if key not in output_file:
                    output_file[key] = []
                output_file[key].append(f"{text.stripext().name}.pdf")

    print(f"\r[{ind_amount:>3}/{ind_amount:>3}] Finished searching text")

    with open(output, 'w') as f:
        json.dump(output_file, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()