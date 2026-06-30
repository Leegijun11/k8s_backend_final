import asyncio
from fastapi import HTTPException
from app.ai.llm_config import get_watsonx
from app.ai.llm_main import LLMDiary


async def ai_llm_story_run(input: str):
    try:
        config = get_watsonx()
        pipeline = LLMDiary()

        final_story = await pipeline.ai_llm_story_model_run(input, config)

        return {"input":input,
                "s_content": final_story}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"디지털북 파이프라인 가동 실패 원인: {str(e)}")


if __name__ == "__main__":
    ai = asyncio.run(ai_llm_story_run(
        """

        오늘 아침부터 변 보는 게 너무 힘들어 보여서 걱정이 많았어. 최근에 이유식이 늘어나서 그런지 얼굴이 빨갛게 되어 힘 주고 있더라고. 힘들게 토끼똥을 쌌는데 아팠는지 칭얼거리기도 했어. 간식을 먹이고 물을 많이 마시게 했는데, 컨디션은 그저 그렇고 체온은 36.8도로 정상이야. 내일은 시원하게 쾌변하고 낮잠도 푹 자줬으면 좋겠어. 화이팅! 
        """
    ))
    print("input\n", ai["input"].strip())
    print("\n\n디지털북\n", ai["s_content"].strip())
