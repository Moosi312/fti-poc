import json
import os
import time
from collections import ChainMap
from time import sleep
from typing import Callable, List

import openai
from dotenv import load_dotenv
from openai import OpenAI
from path import Path

from shared.setup import extract_text, get_strings, get_labels, get_indicators, get_topic_indicator_map, get_iso_date


def default_get_file_name(file: Path):
    return f"{file.stripext().name}.pdf"

def default_get_content(file: Path):
    return file.read_text('UTF-8')



class ChatGPTClient:
    temperature = 50

    def __init__(
            self,
            model: str,
            pdf_folder='../assets/docs/pdf',
            extracted_text_folder='./tmp/extracted-text',
            prompt_file='./tmp/prompt',
            prompt_template='../shared/prompt',
            batches_file='./tmp/batches.jsonl',
            prompt_output_file='./tmp/indicators-for-docs.json',
            output_file='./docs-by-indicator.json',
    ):
        Path('./tmp').makedirs_p()
        self.model = model
        self.pdf_folder = Path(pdf_folder)
        self.extracted_text_folder = Path(extracted_text_folder)
        self.prompt_file = Path(prompt_file)
        self.prompt_template = Path(prompt_template)
        self.batches_file = Path(batches_file)
        self.prompt_output_file = Path(prompt_output_file)
        self.output_file = Path(output_file)

        self.strings = get_strings()
        self.labels = get_labels()
        self.indicators = get_indicators(self.strings, self.labels)
        self.topicIndicatorMap = get_topic_indicator_map(self.strings)

        load_dotenv()
        api_key = os.getenv('OPEN_AI_API_TOKEN')
        self.client = OpenAI(
            api_key=api_key,
            project="proj_oR5I1XR4jtW2dcV6Um9QUbvZ"
        )

    def get_prompt_template(self):
        return self.prompt_template.read_text("UTF-8")

    def set_prompt(self, text: str):
        self.prompt_file.write_lines(text.split('\n'), "UTF-8")

    def extract_text(self):
        extract_text(self.extracted_text_folder, self.pdf_folder)


    def generate_batches(self, text_folder: Path, prompt_input: Path, file_name_transform: Callable[[Path], str] = default_get_file_name, content_transform: Callable[[Path], str] = default_get_content):
        with open(prompt_input, 'r', encoding='UTF-8') as f:
            prompt = f.read()

        return (self.get_batch_line(prompt, file_name_transform(file), content_transform(file)) for file in text_folder.files())

    def get_batch_line(self, system_prompt: str, filename: str, content: str):
        return {
            "custom_id": filename,
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
                "model": self.model,
                "messages": [
                    {
                        "content": system_prompt,
                        "role": "system",
                    },
                    {
                        "content": content,
                        "role": "user",
                    }
                ],
                "max_tokens": 2048,
                "response_format": {
                    "type": "json_object"
                },
            }
        }


    def prompt_query(self, file_name_transform: Callable[[Path], str] = default_get_file_name, content_transform: Callable[[Path], str] = default_get_content):
        with open(self.prompt_file, 'r', encoding='UTF-8') as f:
            prompt = f.read()
            output = {}

        file_amount = len(self.extracted_text_folder.files())
        for i, file in enumerate(self.extracted_text_folder.files()):
            file_name = file_name_transform(file)
            print(f"\r[{i:>3}/{file_amount:>3}] Prompting for doc {file_name}", end='')
            output.update({ file_name : list({*self.make_query(prompt, content_transform(file), file_name)})})

        print(f"\r[{file_amount:>3}/{file_amount:>3}] Finished prompts")

        with open(self.prompt_output_file, 'w', encoding='UTF-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

    def make_query(self, system_prompt: str, content: str, file_name: str, split = 0, waited=False) -> list[str]:
        try:
            return self.make_query_request(system_prompt, content)
        except openai.RateLimitError:
            if not waited:
                print(f"\r[WARN] <{split} | {file_name}> Rate limit exceeded. Waiting for one minute")
                sleep(60)
                return self.make_query(system_prompt, content, file_name, split, True)
            print(f"\r[WARN] <{split} | {file_name}> Rate limit exceeded twice. Waiting for one minute and splitting in half")
            sleep(60)
            return self.make_query(system_prompt, content[:len(content) // 2], file_name, split +1) + self.make_query(system_prompt, content[len(content) // 2:], file_name, split + 1)
        except openai.BadRequestError as e:
            if e.body['code'] == "context_length_exceeded":
                print(f"\r[WARN] <{split} | {file_name}> File too long, splitting in half")
                return self.make_query(system_prompt, content[:len(content) // 2], file_name, split +1) + self.make_query(system_prompt, content[len(content) // 2:], file_name, split + 1)
            print(f"\r[ERROR] <{split} | {file_name}> {e}")
            return []
        except Exception as e:
            print(f"\r[ERROR] <{split} | {file_name}> {e}")
            return []

    def prompt_batches(self, file_name_transform: Callable[[Path], str] = default_get_file_name, content_transform: Callable[[Path], str] = default_get_content):

        with open(self.prompt_file, 'r', encoding='UTF-8') as f:
            prompt = f.read()
            output = {}

        for file in self.extracted_text_folder.files():
            line = self.get_batch_line(prompt, file_name_transform(file), content_transform(file))
            with open(self.batches_file, 'w') as f:
                json.dump(line, f)

            print(f"[{get_iso_date()}] Prompting for docs {file.name.stripext()}")
            t = time.time()
            data = self.prompt_batch()
            output.update(data)
            print(f"\r[{get_iso_date()}] Prompt finished after {time.time() - t:.2f} seconds")
            print()

        with open(self.prompt_output_file, 'w') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)


    def prompt_batch(self):
        batch_input_file = self.client.files.create(file=open(self.batches_file, 'rb'), purpose="batch")
        batch_object = self.client.batches.create(
            input_file_id=batch_input_file.id,
            endpoint="/v1/chat/completions",
            completion_window="24h",
        )

        batch_id = batch_object.id

        batch_status = self.client.batches.retrieve(batch_id=batch_id)
        while batch_status.status not in ['cancelled', 'completed', 'expired', 'failed']:
            print(f"\r[{get_iso_date()}] Current status: {batch_status.status}", end='')
            sleep(10)
            batch_status = self.client.batches.retrieve(batch_id=batch_id)

        print(f"\r[{get_iso_date()}] Current status: {batch_status.status}", end='')

        if batch_status.status != 'completed':
            print(f"\r[{get_iso_date()}] ERROR: unknown error occurred for this request")
            return {}

        if batch_status.output_file_id is None:
            print(f"\r[{get_iso_date()}] ERROR: unknown error occurred for this request")
            return {}

        results = self.client.files.content(file_id=batch_status.output_file_id)

        dicts = (json.loads(json.loads(line)['response']['body']['choices'][0]['message']['content']) for line in
                 results.text.split('\n')[0:-1])

        print(f"\r[{get_iso_date()}] SUCCESS: requests successful")

        return dict(ChainMap(*dicts))

    def make_query_request(self, system_prompt: str, content: str) -> List[str]:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "content": system_prompt,
                    "type": "text",
                    "role": "system",
                },
                {
                    "content": content,
                    "type": "text",
                    "role": "user",
                }
            ],
            response_format={
                "type": "json_object"
            },
            temperature=self.temperature,
            max_completion_tokens=2048,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )

        values = json.loads(response.choices[0].message.content)
        if "Indicators" not in values:
            print(f"\r[{get_iso_date()}] ERROR: no indicators found : {values}")
            return []
        return values["Indicators"]

    def invert_map(self):
        with open(self.prompt_output_file, 'r') as f:
            orig = json.load(f)
        inverted_ind_map = {v: k for k, v in self.indicators.items()}
        invert = {}
        not_found_indicators = {}

        for file, indicators in orig.items():
            for indicator in indicators:
                if indicator not in inverted_ind_map:
                    if indicator not in not_found_indicators:
                        not_found_indicators[indicator] = 0
                    not_found_indicators[indicator] += 1
                    continue
                ind_id = inverted_ind_map[indicator]
                if ind_id not in invert:
                    invert[ind_id] = []
                invert[ind_id].append(file)

        with open(self.output_file, 'w') as f:
            json.dump(invert, f, indent=2, ensure_ascii=False)
