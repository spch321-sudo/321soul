#!/usr/bin/env python3
"""每天抓 YouTube 播放清單最新影片（RSS，免金鑰），依標題「NNN心靈快餐…」（繁）或「NNN心灵快餐…」（简）寫入 data/videos.json（{編號:{t:繁體影片, s:簡體影片}}）。"""
import json, re, sys, urllib.request, xml.etree.ElementTree as ET
LIST = 'PLid55ck_AyA2YwqTBhkMrx0mDtUtlwo8B'
URL = 'https://www.youtube.com/feeds/videos.xml?playlist_id=' + LIST
PATH = 'data/videos.json'
NS = {'a': 'http://www.w3.org/2005/Atom', 'y': 'http://www.youtube.com/xml/schemas/2015'}
RE1 = re.compile(r'0*(\d{1,4})\s*[-－—–]?\s*心([靈灵])快餐')
RE2 = re.compile(r'心([靈灵])快餐\s*[#＃No.第]*\s*0*(\d{1,4})')

def fetch(path=None):
    if path: return open(path, 'rb').read()
    req = urllib.request.Request(URL, headers={'User-Agent': 'Mozilla/5.0 (321soul video sync)'})
    return urllib.request.urlopen(req, timeout=30).read()

def main(src=None):
    root = ET.fromstring(fetch(src))
    vids = json.load(open(PATH, encoding='utf-8'))
    added = []
    for e in root.findall('a:entry', NS):
        vid = e.findtext('y:videoId', namespaces=NS)
        title = e.findtext('a:title', namespaces=NS) or ''
        m = RE1.search(title)
        if m: n, simp = str(int(m.group(1))), m.group(2) == '灵'
        else:
            m = RE2.search(title)
            if not m: continue
            n, simp = str(int(m.group(2))), m.group(1) == '灵'
        if not vid: continue
        k = 's' if simp else 't'
        o = vids.get(n)
        if not isinstance(o, dict): o = {} if not o else {'t': o}
        if o.get(k) != vid:
            if n not in vids: added.append(n)
            o[k] = vid; vids[n] = o
    if added or '--force' in sys.argv:
        out = {k: vids[k] for k in sorted(vids, key=lambda x: int(x))}
        open(PATH, 'w', encoding='utf-8').write(json.dumps(out, ensure_ascii=False, separators=(',', ':')))
    print('added:', ' '.join(added) if added else 'none')

if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('--') else None)
