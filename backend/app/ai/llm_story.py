import asyncio
import re
import json
from fastapi import HTTPException
from app.ai.llm_config import get_watsonx
from app.ai.llm_main import LLMDiary


async def ai_llm_story_run(input_date: list) -> tuple:
    try:
        config = get_watsonx()
        pipeline = LLMDiary()
        
        # LLM 실행 및 공백 제거
        raw_story_string = await pipeline.ai_llm_story_model_run(input_date, config)
        cleaned_string = raw_story_string.strip()
        
        # 마크다운 코드 블록 제거 (```json 또는 ``` 제거)
        cleaned_string = re.sub(r"^```[a-zA-Z]*\s*", "", cleaned_string)
        cleaned_string = re.sub(r"\s*```$", "", cleaned_string)
        cleaned_string = cleaned_string.strip()
        
        # 중괄호 { } 내부의 JSON 객체 데이터 추출 (가장 바깥쪽 괄호 기준)
        match = re.search(r"\{.*\}", cleaned_string, re.DOTALL)
        if not match:
            raise ValueError("LLM 응답에서 유효한 JSON 형식({ })을 찾을 수 없습니다.")
            
        json_style_string = match.group(0)
        
        # 변수 초기화
        story_title = "제목 없음"
        parsed_story_list = []
        
        try:
            # 안전하게 JSON 구조로 파싱
            parsed_data = json.loads(json_style_string)
            
            # JSON 데이터 처리
            if isinstance(parsed_data, dict):
                # 제목 추출 (존재할 경우)
                if "story_title" in parsed_data:
                    story_title = str(parsed_data["story_title"]).strip()
                
                # 리스트 추출
                if "diary_list" in parsed_data:
                    parsed_story_list = parsed_data["diary_list"]
                else:
                    raise ValueError("JSON 구조 내에서 diary_list를 찾을 수 없습니다.")
            elif isinstance(parsed_data, list):
                # 만약 기존처럼 배열 형태로 들어왔을 때를 대비한 방어 코드
                parsed_story_list = parsed_data
            else:
                raise ValueError("올바른 JSON 데이터 형식이 아닙니다.")
                
            if not isinstance(parsed_story_list, list):
                raise ValueError("추출된 데이터가 리스트 형식이 아닙니다.")
                
        except json.JSONDecodeError:
            raise ValueError("LLM 결과 문자열을 JSON 데이터로 변환하는 데 실패했습니다.")

        # 문장 정제 및 줄바꿈 처리
        final_list = []
        for story in parsed_story_list:
            if not isinstance(story, str):
                story = str(story)
            cleaned_story = story.strip()
            final_list.append(cleaned_story)
            
        # 콘솔 출력 (제목 먼저 출력 후 문장 리스트 출력)
        print(f"[제목]: {story_title}")
        print("=" * 40)  # 구분선
        for i in final_list:
            print(f'{i}\n')
            
        return final_list, story_title
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"디지털북 파이프라인 가동 실패 원인: {str(e)}")



if __name__ == "__main__":
    raw_diaries = [
        "새벽에 잠들려는데 속싸개 탈출해서 팔 버둥거리며 깜짝 깸. 만세 하고 잠 자다가도 혼자 깜짝 놀람 상태로 찡찡대서 속상함. 분유 80ml 젖병 허겁지겁 쪽쪽 잘 먹음 완료하고 쉬 기저귀 묵직함. 체온 36.5도 확인하고 품에 안기면 그나마 조용히 잠듦.",
        "낮잠 잘 때 맨날 주먹 꼭 쥐고 있어서 손아귀 힘이 장난 아님. 잼잼 안 됨 상태인 솜방망이 손이 너무 귀여움. 수유 밀착 시키니 빠는 힘 흡입력 엄청나서 꿀꺽꿀꺽 잘 먹음. 소변 기저귀 확인하고 열 36.6도 정상, 7시 전 조기 육퇴 감사.",
        "문소리에 깸 증상 때문에 낮잠을 20분밖에 못 잠. 파르르 떪 반응 보여서 안아주면 뚝 그치는데 내려놓으면 또 허우적거림. 다행히 저녁 막수 분유 100ml 남김없이 완분함. 대변 하나 생산했고 체온 36.4도 확인 후 밤잠 들어감.",
        "하루 종일 주먹고기 전 단계처럼 주먹 꼬옥 쥐고 입 주변을 탐색함. 큰 소리 놀람 반응에 팔을 번쩍 들며 스와들업 필수라는 걸 절감함. 찰떡같이 쪽쪽이기 빪 상태로 꿀잠 들어감. 소변 양 넉넉하고 체온 36.7도 미열 없이 정상.",
        "자다 깨서 욺 난리가 나서 백색소음 반응 유도하니 신기하게 안으면 그침. 하루 종일 솜방망이 주먹 쥐기 탈출을 못 하네. 저녁 수유 90ml 원샷하고 시원하게 감자 대변 생산 완료, 열 없는 것(36.5도) 확인 후 8시 조기 육퇴 성공."
    ]

    test_input_list = []
    test_missions = ["속싸개 탈출 방지", "주먹 쥐기 잼잼", "문소리에 반응하기", "옹알이 하기", "머리 똑바로 들기"]
    for i, content in enumerate(raw_diaries):
        test_input_list.append({
            "page_num": i + 1,
            "status": "True" if i % 2 == 0 else "False",
            "milestone_name": test_missions[i],
            "diary": content
        })

    ai_story_list, story_title = asyncio.run(ai_llm_story_run(test_input_list))
    
    print("\n\n==================== [최종 동화책 출력 결과] ====================")
    
    for index, story_content in enumerate(ai_story_list):
        print(f"\n[펼침면 {index + 1}번 세트]")
        print("input\n", raw_diaries[index])
        print("\n디지털북\n", story_content)
        print("=" * 70)