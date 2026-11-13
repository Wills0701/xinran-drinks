from datetime import datetime
from zoneinfo import ZoneInfo
import html
import re

ZONE = ZoneInfo("Asia/Shanghai")


def clean(value):
    return html.unescape(re.sub(r'<[^>]+>', '', value)).strip()


def parse_horoscope(document, day):
    expected = f'天秤座{day.year}年{day.month}月{day.day}日运势'
    title = re.search(r'class="attr-title"[^>]*>(.*?)</div>', document, re.S)
    if not title or clean(title.group(1)) != expected:
        raise ValueError('Source date does not match today')
    scores_block = document.split('class="xz-prog-list"', 1)[1].split('class="xz-attr-list"', 1)[0]
    scores = {clean(label): int(value) for value, label in re.findall(
        r'class="val"[^>]*>\s*<b>(\d+)</b>%</div>\s*<div class="tit">(.*?)</div>', scores_block, re.S)}
    attrs_block = document.split('class="xz-attr-list"', 1)[1].split('class="luck-detail-body"', 1)[0]
    attrs = {clean(label): clean(value) for value, label in re.findall(
        r'class="val"[^>]*>(.*?)</div>\s*<div class="tit">(.*?)</div>', attrs_block, re.S)}
    match = re.search(r'class="luck-detail-text"[^>]*>\s*<h3[^>]*>.*?</h3>\s*<div class="text">(.*?)</div>', document, re.S)
    if not match or not all(label in scores and 0 <= scores[label] <= 100 for label in ('综合', '爱情', '心情')):
        raise ValueError('Incomplete source content')
    if not attrs.get('幸运颜色') or not attrs.get('幸运数字'):
        raise ValueError('Missing lucky details')
    # A short attributed excerpt; keep the complete article on the publisher's site.
    sentences = [part.strip() for part in re.split('[。！？]', clean(match.group(1))) if part.strip()]
    sentence = sentences[-1]
    # Prefer a complete clause, rather than cutting a Chinese word in half.
    clause = sentence.split('，', 1)[0]
    excerpt = clause[:24] + ('…' if len(clause) > 24 or clause != sentence else '。')
    return {
        'date': day.isoformat(), 'source': '星座乐',
        'sourceUrl': f'https://www.1212.com/luck/libra/{day:%Y%m%d}.html',
        'excerpt': excerpt, 'scores': {key: scores[key] for key in ('综合', '爱情', '心情')},
        'color': attrs['幸运颜色'], 'number': attrs['幸运数字'],
        'fetchedAt': datetime.now(ZONE).isoformat(timespec='seconds')
    }

