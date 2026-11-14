from datetime import datetime
from zoneinfo import ZoneInfo
import html
import re

ZONE = ZoneInfo("Asia/Shanghai")


def clean(value):
    return html.unescape(re.sub(r'<[^>]+>', '', value)).strip()


# Short original guidance keyed to topics in the dated publisher text.
# No percentage is interpreted as an event probability. Unknown topics link to
# the original rather than inventing a daily prediction.
TOPICS = {
    '综合': [
        (r'琐碎|有求于你|老好人', '先照顾好自己的要事，额外的请求量力接下。'),
        (r'疲劳|忙碌|压力|负担', '给今天留一点空档，别把安排排得太满。'),
        (r'机会|机遇|好运', '留意身边的新机会，先弄清细节再行动。'),
        (r'情绪|心情|焦虑|烦恼', '先整理心情，再处理眼前的事。'),
        (r'沟通|人际|朋友', '多听一句、说清一点，有助于减少误会。'),
        (r'计划|规划|目标', '挑一件最重要的事，按自己的节奏推进。'),
        (r'学习|新鲜|尝试', '可以给新事物留一点时间，从小尝试开始。'),
    ],
    '感情': [
        (r'沟通|交流|表达|说开', '有想法及时说清楚，别让对方只靠猜。'),
        (r'迎合|附和|立场|迁就', '照顾对方感受时，也记得表达自己的需要。'),
        (r'陪伴|约会|相处|互动', '留一点专心相处的时间，日常的小回应也很重要。'),
        (r'矛盾|争吵|误会|冲突', '情绪上来先缓一缓，再谈具体的问题。'),
        (r'主动|桃花|脱单|好感', '想靠近就自然地多聊几句，不必急着推进。'),
        (r'稳定|甜蜜|幸福|顺利', '珍惜相处里的小事，把关心落在行动上。'),
    ],
    '工作': [
        (r'规划|计划|目标', '先理清接下来的安排，再逐项推进。'),
        (r'人际|合作|团队|同事', '需要配合的事情，提前对齐想法与分工。'),
        (r'琐碎|忙碌|任务|效率', '把任务分出轻重缓急，先完成最要紧的一项。'),
        (r'机会|表现|创意|想法', '把想法写下来，准备好再争取展示的机会。'),
        (r'细节|失误|谨慎|粗心', '交付前多留一轮检查，尤其注意容易遗漏的细节。'),
        (r'学习|提升|进步', '给学习留一小段时间，把收获用到手头的事上。'),
        (r'稳定|顺利|向前', '按现有节奏稳步推进，完成后再安排下一件事。'),
    ],
    '生活': [
        (r'吃喝|饮食|暴饮|体重', '吃喝留一点余地，也给日常活动腾一点时间。'),
        (r'睡眠|熬夜|休息|疲劳|作息', '今天给休息留出时间，尽量别把事情拖到深夜。'),
        (r'运动|锻炼|活动|散步', '忙完可以起身走走，安排一点轻松的活动。'),
        (r'情绪|压力|心情', '给自己一段安静的空档，做点能放松的小事。'),
        (r'出行|安全|交通', '出门给行程多留一点时间，途中照顾好自己。'),
    ],
}


def daily_insights(general, details):
    texts = {'综合': general, '感情': details.get('爱情运势', ''),
             '工作': details.get('事业运势', ''), '生活': details.get('健康运势', '')}
    result = {}
    for name, source in texts.items():
        matches = [tip for pattern, tip in TOPICS[name] if re.search(pattern, source)]
        result[name] = ''.join(matches[:2]) if matches else f'今天的{name}解读可在原文中查看。'
    return result


def parse_horoscope(document, day):
    expected = f'白羊座{day.year}年{day.month}月{day.day}日运势'
    title = re.search(r'class="attr-title"[^>]*>(.*?)</div>', document, re.S)
    if not title or clean(title.group(1)) != expected:
        raise ValueError('Source date does not match today')
    attrs_block = document.split('class="xz-attr-list"', 1)[1].split('class="luck-detail-body"', 1)[0]
    attrs = {clean(label): clean(value) for value, label in re.findall(
        r'class="val"[^>]*>(.*?)</div>\s*<div class="tit">(.*?)</div>', attrs_block, re.S)}
    match = re.search(r'class="luck-detail-text"[^>]*>\s*<h3[^>]*>.*?</h3>\s*<div class="text">(.*?)</div>', document, re.S)
    details = {clean(label): clean(value) for label, value in re.findall(
        r'<dt>(.*?)</dt>\s*<dd>(.*?)</dd>', document.split('class="luck-detail-body"', 1)[1].split('id="pcWzwb"', 1)[0], re.S)}
    if not match or not all(key in details for key in ('爱情运势', '事业运势', '健康运势')):
        raise ValueError('Incomplete source content')
    if not attrs.get('幸运颜色') or not attrs.get('幸运数字'):
        raise ValueError('Missing lucky details')
    insights = daily_insights(clean(match.group(1)), details)
    return {
        'sign': 'aries', 'date': day.isoformat(), 'source': '星座乐',
        'sourceUrl': f'https://www.1212.com/luck/aries/{day:%Y%m%d}.html',
        'insights': insights,
        'color': attrs['幸运颜色'], 'number': attrs['幸运数字'],
        'fetchedAt': datetime.now(ZONE).isoformat(timespec='seconds')
    }

