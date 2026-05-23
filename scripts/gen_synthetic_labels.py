"""生成合成标注数据,用于 M4 评测框架验证。"""

from __future__ import annotations

import csv
import random
from collections import Counter
from pathlib import Path

# 基于已有帖子 keyword 的合成评论
COMMENTS_POOL: dict[str, list[tuple[str, int, bool, str, str]]] = {
    "甲骨文": [
        ("看好甲骨文云业务", 2, True, "easy", "normal"),
        ("甲骨文财报太牛了", 2, True, "easy", "normal"),
        ("云业务是未来趋势", 1, True, "easy", "normal"),
        ("ORCL长期持有", 1, True, "easy", "normal"),
        ("甲骨文被低估了", 1, True, "medium", "normal"),
        ("加仓甲骨文", 2, True, "easy", "normal"),
        ("甲骨文云业务增速惊人", 2, True, "easy", "normal"),
        ("已上车，坐等翻倍", 1, True, "easy", "normal"),
        ("甲骨文是下一个万亿市值公司", 2, True, "medium", "normal"),
        ("看好Oracle的AI战略", 1, True, "medium", "normal"),
        ("甲骨文垃圾，赶紧跑", -2, True, "easy", "normal"),
        ("割肉了，再也不碰", -1, True, "easy", "normal"),
        ("甲骨文就是个泡沫", -2, True, "easy", "normal"),
        ("高位接盘的韭菜们好", -1, True, "hard", "sarcasm"),
        ("韭菜本菜在此", -1, True, "hard", "sarcasm"),
        ("又一个要被割的", -1, True, "hard", "sarcasm"),
        ("梭哈了生活费等暴富", -1, True, "hard", "sarcasm"),
        ("甲骨文？不如买彩票", -2, True, "hard", "sarcasm"),
        ("这波啊，这波是韭菜入场", -1, True, "hard", "sarcasm"),
        ("笑死，又有人信了", -1, True, "hard", "sarcasm"),
        ("恭喜高位站岗的朋友们", -1, True, "hard", "sarcasm"),
        ("甲骨文必涨！（反指）", -1, True, "hard", "sarcasm"),
        ("今天天气真好", 0, False, "easy", "normal"),
        ("路过，看看热闹", 0, False, "easy", "normal"),
        ("广告位招租", 0, False, "easy", "normal"),
        ("沙发", 0, False, "easy", "normal"),
        ("关注了", 0, False, "easy", "normal"),
        ("不错的分析", 0, False, "easy", "normal"),
        ("谢谢分享", 0, False, "easy", "normal"),
        ("甲骨文是古代文字吗", 0, False, "medium", "novice"),
        ("这个甲骨文是做考古的？", 0, False, "medium", "novice"),
        ("ORCL是啥意思", 0, False, "medium", "novice"),
        ("小白求问怎么买", 0, False, "medium", "novice"),
        ("什么是云业务", 0, False, "medium", "novice"),
        ("第一次买股票选这个行吗", 0, False, "medium", "novice"),
        ("看不懂，但感觉很厉害", 0, False, "medium", "novice"),
        ("不温不火", 0, True, "medium", "normal"),
        ("再观望一下", 0, True, "easy", "normal"),
        ("短期震荡，长期看好", 1, True, "medium", "normal"),
        ("等回调再入", 0, True, "medium", "normal"),
    ],
    "英伟达": [
        ("英伟达是AI芯片之王", 2, True, "easy", "normal"),
        ("NVDA闭眼买", 2, True, "easy", "normal"),
        ("AI时代英伟达就是卖铲子的", 1, True, "medium", "normal"),
        ("显卡太贵了买不起", -1, True, "medium", "normal"),
        ("英伟达泡沫迟早破", -2, True, "easy", "normal"),
        ("韭菜们又冲进去了", -1, True, "hard", "sarcasm"),
        ("NVDA跌了才好上车", 1, True, "medium", "normal"),
        ("黄仁勋牛逼", 1, True, "easy", "normal"),
        ("英伟达市值太高了", -1, True, "medium", "normal"),
        ("等英伟达拆股", 0, True, "medium", "normal"),
        ("游戏显卡党路过", 0, False, "easy", "normal"),
        ("我只关心4090降不降价", 0, False, "medium", "novice"),
        ("英伟达是做显卡的对吧", 0, False, "medium", "novice"),
        ("今天又亏了", -1, True, "easy", "normal"),
        ("满仓英伟达等起飞", 2, True, "easy", "normal"),
        ("高位站岗的都是勇士", -1, True, "hard", "sarcasm"),
        ("AI概念炒过头了", -1, True, "medium", "normal"),
        ("长期持有不折腾", 1, True, "easy", "normal"),
        ("又来割韭菜了", -1, True, "hard", "sarcasm"),
        ("英伟达财报要来了，准备好了吗", 0, True, "easy", "normal"),
    ],
    "机器人": [
        ("人形机器人是未来", 2, True, "easy", "normal"),
        ("机器人ETF值得配置", 1, True, "medium", "normal"),
        ("具身智能要爆发了", 2, True, "medium", "normal"),
        ("机器人概念太虚了", -1, True, "medium", "normal"),
        ("纯炒作，不看好", -2, True, "easy", "normal"),
        ("机器人都能炒股了？", 0, True, "hard", "sarcasm"),
        ("等机器人帮我搬砖", 0, True, "hard", "sarcasm"),
        ("这个机器人好可爱", 0, False, "easy", "normal"),
        ("孩子想要个机器人玩具", 0, False, "easy", "normal"),
        ("波士顿动力的机器人好厉害", 0, False, "medium", "normal"),
        ("什么是具身智能", 0, False, "medium", "novice"),
        ("机器人概念股有哪些", 0, False, "medium", "novice"),
        ("小白求推荐机器人ETF", 0, False, "medium", "novice"),
        ("机器人板块今天涨了", 1, True, "easy", "normal"),
        ("机器人赛道太拥挤了", -1, True, "medium", "normal"),
        ("特斯拉机器人要量产了", 1, True, "medium", "normal"),
        ("机器人概念股泡沫严重", -2, True, "medium", "normal"),
        ("看好国内机器人产业链", 1, True, "medium", "normal"),
        ("机器人替代人类？想多了", -1, True, "hard", "sarcasm"),
        ("又一个被炒上天的概念", -1, True, "hard", "sarcasm"),
    ],
    "半导体": [
        ("半导体是国之重器", 2, True, "easy", "normal"),
        ("芯片国产化势在必行", 1, True, "medium", "normal"),
        ("半导体周期见底了", 1, True, "medium", "normal"),
        ("芯片过剩还在持续", -1, True, "medium", "normal"),
        ("半导体骗局", -2, True, "easy", "normal"),
        ("国产芯片？笑话", -2, True, "hard", "sarcasm"),
        ("又来骗补贴了", -1, True, "hard", "sarcasm"),
        ("什么是半导体", 0, False, "medium", "novice"),
        ("芯片和半导体是一个东西吗", 0, False, "medium", "novice"),
        ("我手机芯片是哪个公司的", 0, False, "easy", "normal"),
        ("半导体ETF可以定投吗", 1, True, "medium", "novice"),
        ("光刻机才是关键", 0, True, "medium", "normal"),
        ("华为芯片怎么样了", 0, False, "medium", "normal"),
        ("半导体板块反弹了", 1, True, "easy", "normal"),
        ("芯片制裁影响很大", -1, True, "medium", "normal"),
        ("看好国内半导体龙头", 1, True, "medium", "normal"),
        ("半导体行业水太深", -1, True, "hard", "sarcasm"),
        ("投半导体不如存银行", -1, True, "hard", "sarcasm"),
        ("国产替代的韭菜们", -1, True, "hard", "sarcasm"),
        ("芯片涨价利好半导体", 1, True, "easy", "normal"),
    ],
}

POST_TEXTS = {
    "甲骨文": "甲骨文ORCL财报超预期，今日甲骨文发布财报，云业务收入同比增长25%，超出市场预期。股价盘后大涨。",
    "英伟达": "英伟达NVDA发布最新AI芯片，性能提升3倍，各大云厂商争相下单，AI算力需求持续爆发。",
    "机器人": "人形机器人赛道火爆，多家企业发布新品，具身智能成为下一个万亿级市场。",
    "半导体": "半导体行业迎来拐点，国产芯片突破关键制程，芯片国产化进程加速。",
}


def main() -> None:
    output_path = Path("data/eval/labeled_200.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    rows: list[dict] = []
    idx = 0

    for keyword, comments in COMMENTS_POOL.items():
        for text, sentiment, is_relevant, difficulty, style in comments:
            idx += 1
            rows.append({
                "comment_id": f"c{idx:03d}",
                "keyword": keyword,
                "text": text,
                "n_likes": random.randint(0, 50),
                "post_text": POST_TEXTS[keyword],
                "difficulty": difficulty,
                "style": style,
                "sentiment_label": sentiment,
                "is_relevant_label": "TRUE" if is_relevant else "FALSE",
            })

    random.seed(42)
    random.shuffle(rows)

    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "comment_id", "keyword", "text", "n_likes", "post_text",
            "difficulty", "style", "sentiment_label", "is_relevant_label",
        ])
        writer.writeheader()
        writer.writerows(rows)

    style_counts = Counter(r["style"] for r in rows)
    diff_counts = Counter(r["difficulty"] for r in rows)
    kw_counts = Counter(r["keyword"] for r in rows)

    print(f"Total: {len(rows)} samples")
    print(f"By style: {dict(style_counts)}")
    print(f"By difficulty: {dict(diff_counts)}")
    print(f"By keyword: {dict(kw_counts)}")
    print(f"Saved to: {output_path}")


if __name__ == "__main__":
    main()
