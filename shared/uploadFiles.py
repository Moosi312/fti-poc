import json
import os

import openai
from dotenv import load_dotenv
from path import Path

FOLDER_PATH = './assets/docs/pdf'
OUTPUT_FILE = './shared/fileIds.json'
VECTOR_STORE_ID = 'vs_6803b9685da88191b65010bbced4bd51'


def upload_file(api_key: str, file: Path, purpose='fine-tune') -> str:
    openai.api_key = api_key
    with open(file, "rb") as f:
        response = openai.files.create(file=f, purpose=purpose)
    print(f"✅ Uploaded: {file.name} | File ID: {response.id}")
    return response.id

def upload_pdfs_in_folder(api_key: str, folder: Path, output: Path, purpose='assistants'):
    if not folder.is_dir():
        raise NotADirectoryError(f"{folder} is not a valid directory.")

    ids = []
    pdf_files = list(folder.glob("*.pdf"))
    if not pdf_files:
        print("No PDF files found in the specified folder.")
        return

    print(f"Found {len(pdf_files)} PDF(s) in {folder}:\n")

    for pdf_file in pdf_files:
        try:
            ids.append(upload_file(api_key, pdf_file, purpose))
        except Exception as e:
            print(f"❌ Failed to upload {pdf_file.name}: {e}")

    output.write_text(json.dumps(ids, indent=4))

def add_files_to_vector_store(api_key: str, output_file: Path):
    client = openai.OpenAI(api_key=api_key)
    for file_id in json.loads(output_file.read_text()):
        client.vector_stores.files.create(
            vector_store_id=VECTOR_STORE_ID,
            file_id=file_id
        )

def main():
    load_dotenv()
    api_key = os.getenv('OPEN_AI_API_TOKEN')
    print(api_key)
    upload_pdfs_in_folder(api_key, Path(FOLDER_PATH), Path(OUTPUT_FILE))
    add_files_to_vector_store(api_key, Path(OUTPUT_FILE))

if __name__ == "__main__":
    main()