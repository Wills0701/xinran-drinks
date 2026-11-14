#!/usr/bin/env python3
"""Generate today's date-checked almanac before deploying Pages."""
from datetime import datetime
from pathlib import Path
import json
import subprocess
import sys

from almanac import ZONE, SOURCE, parse_almanac

ROOT = Path(__file__).resolve().parents[1]


def generate():
    day = datetime.now(ZONE).date()
    url = SOURCE
    try:
        response = subprocess.run(
            ['curl', '-sSL', '--fail', '--retry', '2', '--retry-delay', '3',
             '--max-time', '20', '--max-filesize', '2000000', url],
            capture_output=True, timeout=80, check=True)
        data = parse_almanac(response.stdout.decode('utf-8'), day)
        if datetime.now(ZONE).date() != day:
            raise ValueError('Day changed during fetch')
        print(f'Almanac fetched and date checked: {day}')
    except (ValueError, IndexError, UnicodeError, subprocess.SubprocessError) as error:
        # Still publish the drink picker. Never ship yesterday as today's fortune.
        data = {'date': day.isoformat(), 'error': '暂时未获取到今天的黄历', 'sourceUrl': url}
        print(f'::warning::Almanac unavailable ({type(error).__name__}); publishing a dated error state.', file=sys.stderr)
    destination = ROOT / 'site' / 'almanac.json'
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix('.tmp')
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    temporary.replace(destination)


if __name__ == '__main__':
    generate()
