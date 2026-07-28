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
아래는 아기의 여러 날짜에 걸친 일기 기록이야. 이 일기들을 단순 나열하지 말고,
전통적인 이야기 구조인 '기승전결(起承轉結)' 4단계로 재구성해서
하나의 따뜻하고 자연스럽게 이어지는 성장 이야기(짧은 동화/회고록)로 만들어줘.

[기승전결 구성 규칙]
1. 전체 일기 기록을 시간 순서를 유지한 채 대략 4등분하여 각 구간을 아래 단계에 배정해.
   일기 개수가 4로 나누어 떨어지지 않으면 뒤 단계(전, 결)에 조금 더 배정해도 좋아.
   - 기(起, 도입): 이야기의 배경과 초반 일상을 소개하며 자연스럽게 시작을 열어줘.
   - 승(承, 전개): 기에서 이어지는 일상과 성장 과정을 쌓아가며 이야기를 발전시켜줘.
   - 전(轉, 전환): 그 사이에 있었던 변화, 새로운 시도, 감정의 굴곡이나 작은 사건 등
     이야기의 흐름이 한 번 바뀌는 전환점을 드러내줘.
   - 결(結, 마무리): 앞의 세 단계를 자연스럽게 매듭지으며, 아기의 성장을 따뜻하게
     되돌아보는 여운 있는 마무리로 끝맺어줘.
2. 각 단계는 문단으로 구분하되, 단계가 바뀌는 지점이 툭 끊기지 않도록 앞 단계의
   감정이나 사건을 자연스럽게 이어받는 연결 문장을 넣어서 하나의 흐름으로 읽히게 해줘.
3. "기승전결" 같은 단계 이름이나 구조를 본문에 직접 언급하지 말고, 오직 이야기의
   흐름 자체로만 구조가 느껴지게 써줘.

[일기 기록]
{diary_summaries}

다음 JSON 형식으로만 응답해. 다른 설명이나 코드블록 없이 순수 JSON만 출력해:
{{
  "s_name": "디지털북 제목 (짧고 감성적으로)",
  "s_content": "기승전결 흐름에 따라 자연스럽게 이어지는 전체 이야기 내용 (여러 문단 가능)"
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