# -*- coding: utf-8 -*-
"""Preprocess GSM8K dataset by cleaning answer strings.

This script reads a JSONL file where each entry contains a question and an
answer (or response). For every record the answer text is normalized using
``answer_cleansing`` from the repository utilities. The cleaned answer is added
under the key ``cleaned_answer`` and written back to an output JSONL file.

Example
-------
python preprocess_gsm8k.py --input data/test/GSM8K_test.jsonl --output cleaned.jsonl --workers 8
"""
from __future__ import annotations
import argparse
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from itertools import islice
from pathlib import Path

# Enable imports from code_for_generating_data/code
REPO_UTILS = Path(__file__).resolve().parent / 'code_for_generating_data' / 'code'
if str(REPO_UTILS) not in sys.path:
    sys.path.append(str(REPO_UTILS))

from utils.answer_clean_utils import answer_cleansing  # type: ignore


def _process_line(line: str) -> str:
    """Parse one JSON line and return processed JSON string."""
    data = json.loads(line)
    answer_text = data.get('answer') or data.get('response', '')
    cleaned = answer_cleansing(answer_text, ds_name='GSM8K')
    data['cleaned_answer'] = cleaned
    return json.dumps(data, ensure_ascii=False)


def main(args: argparse.Namespace) -> None:
    workers = max(1, int(args.workers))
    input_path = Path(args.input)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with input_path.open('r', encoding='utf-8') as fin, \
            output_path.open('w', encoding='utf-8') as fout, \
            ProcessPoolExecutor(max_workers=workers) as executor:
        while True:
            lines = list(islice(fin, workers * 4))
            if not lines:
                break
            for out in executor.map(_process_line, lines):
                fout.write(out + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Clean GSM8K answers')
    parser.add_argument('--input', required=True, help='Input JSONL file')
    parser.add_argument('--output', required=True, help='Output JSONL file')
    parser.add_argument('--workers', type=int, default=1, help='Number of processes')
    main(parser.parse_args())
