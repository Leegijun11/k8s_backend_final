import json
import re
from app.ai.model import llm
from app.db.models.logs import Log
from app.db.models.babyimages import BabyImage


DIARY_PROMPT = """\
너는 아기 일기를 대신 작성해주는 도우미야.
아래 정보를 참고해서 아기의 하루를 따뜻한 1인칭 시점(아기 입장) 일기로 작성해줘.

[활동 기록]
{log_content}

[사진 라벨 목록]
{image_labels}

다음 JSON 형식으로만 응답해. 다른 설명이나 코드블록 없이 순수 JSON만 출력해:
{{
  "d_title": "일기 제목 (짧고 귀엽게)",
  "d_content": "일기 본문 (3~5문장)",
  "d_label": "오늘의 감정/상태를 나타내는 짧은 라벨 (예: 행복, 기분좋음 등)",
  "d_eat": "오늘 식사 관련 요약",
  "d_sleep": "오늘 수면 관련 요약",
  "d_toilet": "오늘 배변 관련 요약",
  "d_temp": "오늘 체온/건강 상태 요약"
}}
"""


async def generate_diary_content(log: Log, images: list[BabyImage]) -> dict:
    image_labels = ", ".join([img.i_label for img in images if img.i_label]) or "없음"

    prompt = DIARY_PROMPT.format(
        log_content=log.l_content or "기록 없음",
        image_labels=image_labels
    )

    response = await llm.ainvoke(prompt)
    raw_text = response.content

    # LLM이 ```json ... ``` 으로 감싸서 줄 수도 있으니 제거
    cleaned = re.sub(r"^```(json)?|```$", "", raw_text.strip(), flags=re.MULTILINE).strip()

    try:
        result = json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(f"LLM 응답을 JSON으로 파싱하지 못했습니다: {e}\n원본 응답: {raw_text}")

    return result

STORY_PROMPT = """\
너는 아기의 성장 디지털북(스토리북)을 작성해주는 도우미야.
아래는 아기의 여러 날짜에 걸친 일기 기록이야. 이 일기들을 시간 순서대로 엮어서,
하나의 따뜻하고 연결된 성장 이야기로 재구성해줘. 각 날의 일기를 단순 나열하지 말고,
하나의 짧은 동화/회고록처럼 자연스럽게 이어지는 글로 작성해줘.

[일기 기록]
{diary_summaries}

다음 JSON 형식으로만 응답해. 다른 설명이나 코드블록 없이 순수 JSON만 출력해:
{{
  "s_name": "디지털북 제목 (짧고 감성적으로)",
  "s_content": "전체 이야기 내용 (여러 문단 가능, 시간 흐름에 따라 자연스럽게 서술)"
}}
"""


async def generate_story_content(diaries: list) -> dict:
    diary_summaries = "\n".join([
        f"- {d.d_date}: {d.d_title} | {d.d_content} (감정: {d.d_label})"
        for d in diaries
    ])

    prompt = STORY_PROMPT.format(diary_summaries=diary_summaries)

    response = await llm.ainvoke(prompt)
    raw_text = response.content

    cleaned = re.sub(r"^```(json)?|```$", "", raw_text.strip(), flags=re.MULTILINE).strip()

    try:
        result = json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(f"LLM 응답을 JSON으로 파싱하지 못했습니다: {e}\n원본 응답: {raw_text}")

    return result