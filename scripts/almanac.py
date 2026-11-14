"""Read the publisher's current almanac; never reuse another day's result."""
from datetime import datetime
from zoneinfo import ZoneInfo
import html
import re

ZONE = ZoneInfo('Asia/Shanghai')
SOURCE = 'https://www.1212.com/huangli/'


def clean(value):
    return html.unescape(re.sub(r'<[^>]+>', '', value)).strip()


def parse_almanac(document, day):
    def element(tag, identifier):
        match = re.search(r'<' + tag + r'\b[^>]*\bid="' + identifier + r'"[^>]*>(.*?)</' + tag + '>', document, re.S)
        if not match:
            raise ValueError('Incomplete almanac')
        return match.group(1)
    expected = f'{day.year}年{day.month}月{day.day}日'
    if clean(element('span', 'dayStr')) != expected:
        raise ValueError('Almanac date does not match today')
    lunar = re.sub(r'^农历.*?年\s*', '', clean(element('span', 'dayLunar')))
    yi = [clean(x) for x in re.findall(r'<li[^>]*>(.*?)</li>', element('ul', 'dayYi'), re.S)]
    ji = [clean(x) for x in re.findall(r'<li[^>]*>(.*?)</li>', element('ul', 'dayJi'), re.S)]
    if not lunar or not yi or not ji or not all(yi + ji):
        raise ValueError('Incomplete almanac details')
    return {'date': day.isoformat(), 'lunar': lunar, 'yi': yi[:2], 'ji': ji[:2],
            'source': '星座乐', 'sourceUrl': SOURCE,
            'fetchedAt': datetime.now(ZONE).isoformat(timespec='seconds')}
