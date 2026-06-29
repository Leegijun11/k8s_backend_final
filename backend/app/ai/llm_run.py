import asyncio
import json
import re
from fastapi import HTTPException
from app.ai.llm_config import get_watsonx
from app.ai.llm_main import LLMDiary


async def ai_llm_run(sample_step1_insight:str):
    try:
        config = get_watsonx()

        pipeline = LLMDiary()

        step2_labels = await pipeline.ai_llm_label_model_run_step2(
            step1_insights=sample_step1_insight,
            config=config
        )


        final_diary = await pipeline.ai_llm_diary_model_run_step3(
            perfect_match_input=step2_labels,
            config=config
        )


        if isinstance(step2_labels, str):
            cleaned = re.sub(r"```[a-zA-Z]*", "", step2_labels).strip()
            
            if "{" in cleaned:
                cleaned = cleaned[cleaned.index("{"):]
            if "}" in cleaned:
                cleaned = cleaned[:cleaned.rindex("}") + 1]
            
            try:
                step2_labels = json.loads(cleaned)
            except json.JSONDecodeError:
                try:
                    extracted = {}
                    patterns = {
                        "핵심어": r'"핵심어"\s*:\s*([^,\n\r]+)',
                        "감정": r'"감정"\s*:\s*([^,\n\r]+)',
                        "식사": r'"식사"\s*:\s*([^,\n\r]+)',
                        "배변": r'"배변"\s*:\s*([^,\n\r]+)',
                        "수면": r'"수면"\s*:\s*([^,\n\r]+)',
                        "시간": r'"시간"\s*:\s*([^,\n\r]+)',
                        "체온": r'"체온"\s*:\s*([^,\n\r]+)',
                        "육아범주": r'"육아범주"\s*:\s*([^,\n\r\s}]+)'
                    }
                    for key, pattern in patterns.items():
                        match = re.search(pattern, cleaned)
                        if match:
                            val = match.group(1).strip().strip('"').strip("'").strip('}')
                            extracted[key] = val
                    
                    if extracted:
                        step2_labels = extracted
                    else:
                        raise ValueError("정규식 매칭 실패")
                except Exception as e:
                    raise HTTPException(status_code=500,
                                        detail=f"LLM 응답 텍스트 정제 및 JSON 파싱 실패. 원본 데이터: {step2_labels}")


        d_label = step2_labels.get("감정", "")
        d_eat = step2_labels.get("식사", "")
        d_sleep = step2_labels.get("수면", "")
        d_toilet = step2_labels.get("배변", "")
        d_temp = step2_labels.get("체온", "")


        return {
            "d_label":d_label, 
            "d_eat":d_eat,
            "d_sleep":d_sleep,
            "d_toilet":d_toilet,
            "d_temp":d_temp,
            "d_content":final_diary}
        
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"자동 일기 파이프라인 가동 실패 원인: {str(e)}")


if __name__ == "__main__":
    # 비동기 루프 기동
    asyncio.run(ai_llm_run(
"오늘 아이가 아침부터 컨디션이 최고였는지 싱글벙글 웃으며 잘 놀 기세였습니다. 점심 이유식을 다 비우고도 더 달라고 칭얼거렸는데, 이상하게 낮 시간이 지나도 침대에 누워 잘 생각이 전혀 없어 보였습니다. 다행히 3시쯤 유모차를 타자마자 스르륵 잠들어 1시간 동안 땀을 흘리며 푹 잤습니다. 체온은 36.6도입니다."
    ))
