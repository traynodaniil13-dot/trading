import re, sys

def parse_srt(path):
    txt = open(path, encoding='utf-8').read()
    blocks = re.split(r'\n\n+', txt.strip())
    cues = []
    for b in blocks:
        lines = b.strip().split('\n')
        if len(lines) < 2:
            continue
        # find timestamp line
        ts_line = None
        text_lines = []
        for l in lines:
            if '-->' in l:
                ts_line = l
            elif re.match(r'^\d+$', l.strip()):
                continue
            else:
                text_lines.append(l)
        if not ts_line:
            continue
        start = ts_line.split('-->')[0].strip()
        h, m, s_ms = start.split(':')
        s, ms = s_ms.split(',')
        total_s = int(h)*3600 + int(m)*60 + int(s)
        cues.append((total_s, ' '.join(text_lines).strip()))
    return cues

def collapse(cues, interval=12):
    out = []
    bucket_start = None
    bucket_text = []
    last_t = 0
    for t, text in cues:
        if bucket_start is None:
            bucket_start = t
        if t - bucket_start >= interval:
            out.append((bucket_start, ' '.join(bucket_text)))
            bucket_start = t
            bucket_text = []
        bucket_text.append(text)
        last_t = t
    if bucket_text:
        out.append((bucket_start, ' '.join(bucket_text)))
    return out

def fmt(t):
    m, s = divmod(t, 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"

if __name__ == '__main__':
    path = sys.argv[1]
    interval = int(sys.argv[2]) if len(sys.argv) > 2 else 12
    cues = parse_srt(path)
    collapsed = collapse(cues, interval)
    for t, text in collapsed:
        print(f"[{fmt(t)}] {text}")
