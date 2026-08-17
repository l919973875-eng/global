from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path


def iso_time(value):
    if value in (None, ''):
        return None
    try:
        if isinstance(value, (int, float)) or str(value).isdigit():
            n = float(value)
            if n > 1e12: n /= 1000
            return datetime.fromtimestamp(n, tz=timezone.utc).isoformat()
    except Exception:
        pass
    try:
        from dateutil import parser as dtparser
        dt = dtparser.parse(str(value))
        if dt.tzinfo is None: dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc).isoformat()
    except Exception:
        return None


def first(d, *keys):
    for k in keys:
        v = d.get(k)
        if v not in (None, '', [], {}): return v
    return None


def normalize(platform: str, d: dict) -> dict | None:
    title = first(d,'title','note_title','video_title') or ''
    desc = first(d,'desc','content','text','note_desc','aweme_desc','description') or ''
    text = re.sub(r'\s+',' ',f'{title} {desc}').strip()
    if not text: return None
    author = first(d,'nickname','user_nickname','author_name','screen_name','user_name','author') or 'unknown'
    raw_id = first(d,'note_id','aweme_id','id','mblogid','content_id','video_id') or hashlib.sha256(text.encode('utf-8')).hexdigest()[:20]
    url = first(d,'note_url','aweme_url','video_url','url','content_url') or ''
    if not url:
        if platform == 'xiaohongshu': url = f'https://www.xiaohongshu.com/explore/{raw_id}'
        elif platform == 'douyin': url = f'https://www.douyin.com/video/{raw_id}'
        elif platform == 'weibo': url = f'https://weibo.com/detail/{raw_id}'
    published = iso_time(first(d,'time','create_time','created_at','publish_time','note_time'))
    engagement = {
        'like_count': int(first(d,'liked_count','like_count','attitudes_count','digg_count') or 0),
        'comment_count': int(first(d,'comment_count','comments_count') or 0),
        'share_count': int(first(d,'share_count','reposts_count') or 0),
    }
    media = first(d,'image_list','images','video_cover','video_url')
    media_count = len(media) if isinstance(media, list) else (1 if media else 0)
    sid = hashlib.sha256(f'{platform}:{raw_id}'.encode('utf-8')).hexdigest()[:20]
    return {'id':sid,'platform':platform,'author':str(author),'text':text[:1800],'url':str(url),'published_at':published,'collected_at':datetime.now(timezone.utc).isoformat(),'query':'mediacrawler-search','engagement':engagement,'media_count':media_count,'collector':'MediaCrawler-external'}


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--repo',required=True); ap.add_argument('--output',required=True); ap.add_argument('--status-output',default=''); args=ap.parse_args()
    repo=Path(args.repo); out_path=Path(args.output); out_path.parent.mkdir(parents=True,exist_ok=True)
    mapping={'xhs':'xiaohongshu','dy':'douyin','wb':'weibo'}; new=[]; status=[]
    for code, platform in mapping.items():
        files=list((repo/'data'/code).glob('json/*contents*.json')) if (repo/'data'/code).exists() else []
        count=0
        for path in files:
            try:
                rows=json.loads(path.read_text(encoding='utf-8'))
                if not isinstance(rows,list): rows=[rows]
                for d in rows:
                    if isinstance(d,dict):
                        row=normalize(platform,d)
                        if row: new.append(row); count+=1
            except Exception:
                continue
        status.append({'platform':platform,'status':'ok' if count else 'empty','items':count,'collector':'MediaCrawler'})
    try:
        existing=json.loads(out_path.read_text(encoding='utf-8')) if out_path.exists() else []
        if not isinstance(existing,list): existing=[]
    except Exception: existing=[]
    by_id={r.get('id'):r for r in existing if r.get('id')}
    for r in new: by_id[r['id']]=r
    cutoff=datetime.now(timezone.utc)-timedelta(days=14); kept=[]
    for r in by_id.values():
        try:
            dt=datetime.fromisoformat((r.get('published_at') or r.get('collected_at')).replace('Z','+00:00'))
            if dt.tzinfo is None: dt=dt.replace(tzinfo=timezone.utc)
            if dt < cutoff: continue
        except Exception: pass
        kept.append(r)
    kept.sort(key=lambda x:x.get('published_at') or x.get('collected_at') or '', reverse=True)
    out_path.write_text(json.dumps(kept[:12000],ensure_ascii=False,indent=2),encoding='utf-8')
    if args.status_output:
        Path(args.status_output).write_text(json.dumps(status,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'ingested MediaCrawler: new={len(new)}, stored={len(kept)}')

if __name__=='__main__': main()
