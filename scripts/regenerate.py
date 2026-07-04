#!/usr/bin/env python3
"""
geungogma 최신 enGB.json 기반으로 translations.json 재생성
Usage: python3 scripts/regenerate.py <enGB_path> <docs_dir>
"""
import json, re, sys, os, hashlib

def is_korean(t):
    return bool(re.search(r'[가-힣]', t))

def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()

def main():
    engb_path = sys.argv[1] if len(sys.argv) > 1 else 'enGB_latest.json'
    docs_dir  = sys.argv[2] if len(sys.argv) > 2 else 'docs'

    hash_path      = os.path.join(docs_dir, 'source_hash.txt')
    originals_path = os.path.join(docs_dir, 'english_originals.json')
    output_path    = os.path.join(docs_dir, 'translations.json')

    # 변경 감지
    new_hash = sha256(engb_path)
    if os.path.exists(hash_path):
        with open(hash_path) as f:
            old_hash = f.read().strip()
        if old_hash == new_hash:
            print(f'변경 없음 (hash: {new_hash[:12]}...). 스킵.')
            sys.exit(0)

    print(f'새 버전 감지 (hash: {new_hash[:12]}...)')

    with open(engb_path, encoding='utf-8') as f:
        geo = json.load(f)
    with open(originals_path, encoding='utf-8') as f:
        originals = json.load(f)  # uuid -> 영어 원문

    uuids = list(geo['strings'].keys())
    total = len(uuids)
    entries = []

    for i, u in enumerate(uuids):
        if u not in originals:
            continue  # 영어 원문 없는 항목 스킵
        eng = originals[u]
        kor = geo['strings'][u]['Text']
        if not is_korean(kor):
            continue  # 아직 미번역
        pct = i / total
        act = 1 if pct < 0.20 else 2 if pct < 0.40 else 3 if pct < 0.60 else 4 if pct < 0.80 else 5
        entries.append({'u': u, 'e': eng, 'k': kor, 'a': act})

    print(f'번역 항목: {len(entries):,}개')

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(entries, f, ensure_ascii=False, separators=(',', ':'))

    with open(hash_path, 'w') as f:
        f.write(new_hash)

    print(f'저장 완료: {output_path}')
    print(f'CHANGED=true')  # GitHub Actions 변경 감지용

if __name__ == '__main__':
    main()
