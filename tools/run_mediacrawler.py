from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path


def replace_assignment(text: str, name: str, value_repr: str) -> str:
    # MediaCrawler 有少数配置（如 CRAWLER_TYPE）使用多行括号表达式，先完整替换。
    multi = re.compile(rf'(?ms)^{re.escape(name)}\s*=\s*\(.*?^\s*\)\s*(?:#.*)?$')
    if multi.search(text):
        return multi.sub(f'{name} = {value_repr}', text, count=1)
    pat = re.compile(rf'(?m)^{re.escape(name)}\s*=.*$')
    if pat.search(text):
        return pat.sub(f'{name} = {value_repr}', text, count=1)
    return text + f'\n{name} = {value_repr}\n'


def patch_config(repo: Path, platform: str, cookie: str, keywords: str, max_notes: int):
    path = repo / 'config' / 'base_config.py'
    text = path.read_text(encoding='utf-8')
    values = {
        'PLATFORM': repr(platform),
        'KEYWORDS': repr(keywords),
        'LOGIN_TYPE': repr('cookie'),
        'COOKIES': repr(cookie),
        'CRAWLER_TYPE': repr('search'),
        'SAVE_DATA_OPTION': repr('json'),
        'CRAWLER_MAX_NOTES_COUNT': str(max_notes),
        'MAX_CONCURRENCY_NUM': '1',
        'ENABLE_GET_COMMENTS': 'False',
        'ENABLE_GET_SUB_COMMENTS': 'False',
        'HEADLESS': 'True',
        'ENABLE_CDP_MODE': 'False',
        'ENABLE_IP_PROXY': 'False',
        'SAVE_LOGIN_STATE': 'False',
        'ENABLE_GET_WORDCLOUD': 'False',
    }
    for k, v in values.items():
        text = replace_assignment(text, k, v)
    path.write_text(text, encoding='utf-8')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', required=True)
    ap.add_argument('--platform', choices=['xhs','dy','wb'], required=True)
    ap.add_argument('--cookie-env', required=True)
    ap.add_argument('--keywords', required=True)
    ap.add_argument('--max-notes', type=int, default=20)
    args = ap.parse_args()
    cookie = os.getenv(args.cookie_env, '').strip()
    if not cookie:
        print(f'[skip] {args.platform}: secret {args.cookie_env} not configured')
        return 0
    repo = Path(args.repo).resolve()
    patch_config(repo, args.platform, cookie, args.keywords, max(10, min(50, args.max_notes)))
    print(f'[run] MediaCrawler platform={args.platform}, keywords configured, cookie present')
    proc = subprocess.run(['uv','run','python','main.py','--platform',args.platform,'--lt','cookie','--type','search','--save_data_option','json'], cwd=repo)
    if proc.returncode:
        print(f'[warn] MediaCrawler {args.platform} failed with exit={proc.returncode}; other sources will continue')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
