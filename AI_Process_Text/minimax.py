from openai import OpenAI
import os
import textwrap

# MiniMax API 配置
GROUP_ID = "1995320804241314053"

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://api.minimaxi.com/v1",
    default_headers={"Group-ID": GROUP_ID}
)

PROMPT_TEMPLATE = textwrap.dedent("""\
你是一名专业播客制作人，请将以下新闻信息改写成1分钟AI口播稿（约200-250字）。要求：
1. **结构**：开场白→核心事实→专家/民众观点→结尾升华
2. **语言**：口语化、有节奏感，避免长句和术语
3. **时长控制**：按正常语速朗读约55-65秒
4. **关键要素**：
   - 用「听众朋友们」开头
   - 关键数据需重复强调
   - 结尾抛出互动问题
5. **禁止**：添加原文没有的信息

新闻原文：
{news}
""")


def build_podcast_prompt(news_text: str) -> str:
    """返回填充了新闻原文的播客生成 Prompt（可直接作为用户消息发送给模型）。"""
    return PROMPT_TEMPLATE.format(news=news_text.strip())


def _extract_chinese_script(text: str) -> str:
    """尝试从模型输出中提取以“听众朋友们”开头的中文口播稿，如果找不到则返回原文的第一段（去除多余空行）。"""
    if not text:
        return text
    text = text.strip()
    idx = text.find("听众朋友")
    if idx != -1:
        return text[idx:].strip()
    # 找不到关键词，取第一段
    parts = [p.strip() for p in text.splitlines() if p.strip()]
    return parts[0] if parts else text


def generate_podcast_script(news_text: str) -> dict:
    """调用模型生成播客稿并返回包含 reasoning 和正文的字典。

    返回示例：{"thinking": str, "text": str, "raw_response": dict}
    """
    user_prompt = build_podcast_prompt(news_text)

    system_msg = (
        "You are a professional podcast producer and copywriter."
        " When replying, output ONLY the final podcast script in Chinese (about 200-250 Chinese characters, ~55-65 seconds)."
        " Do not include analysis, bullet points, headers, or extra commentary in the assistant message content; any chain-of-thought belongs in reasoning_details."
    )

    resp = client.chat.completions.create(
        model="MiniMax-M2.1",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_prompt},
        ],
        extra_body={"reasoning_split": True},
    )

    choice = resp.choices[0]
    thinking = ""
    if getattr(choice.message, "reasoning_details", None):
        rd = choice.message.reasoning_details
        if isinstance(rd, list) and len(rd) > 0:
            thinking = rd[0].get("text", "")

    raw_text = choice.message.content or ""
    script = _extract_chinese_script(raw_text)

    return {
        "thinking": thinking,
        "text": script,
        "raw_response": resp,
    }


# ------------------------
# 本地测试与示例（可直接运行）
# ------------------------
TEST_NEWS = (
    "财政部今日宣布新能源汽车购置税减免政策延续至2027年底，但减免额度逐年递减20%。"
    "2024年单车最高免1.5万元，2025年降至1.2万。行业数据显示，2023年新能源车销量达949万辆，占乘用车总销量31.6%。"
    "特斯拉Model Y成为年度销冠，比亚迪海豚、五菱宏光MINI EV分列二三位。充电基础设施同期扩容，全年新增充电桩235万台，超充桩占比达18%。"
    "中汽协专家王明远指出：‘政策退坡将加速行业洗牌，具备核心技术企业将脱颖而出。’"
)


if __name__ == "__main__":
    # 直接运行生成示例播客稿
    result = generate_podcast_script(TEST_NEWS)

    print("--- Prompt (for reference) ---")
    print(build_podcast_prompt(TEST_NEWS))
    print("\n--- Model Thinking ---")
    print(result["thinking"].strip())
    print("\n--- Podcast Script ---")
    print(result["text"].strip())
