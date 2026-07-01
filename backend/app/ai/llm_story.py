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
                "sp_content": final_story}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"디지털북 파이프라인 가동 실패 원인: {str(e)}")


if __name__ == "__main__":
    ai = asyncio.run(ai_llm_story_run(
        """

오늘은 정말 큰맘 먹고 거실에 비닐 깔고 두부 촉감놀이를 시작했어요.
처음에 두부가 무서웠는지 손가락만 콕콕 찌르다가,
나중에 온몸으로 두부를 으깨고 머리에 샴푸처럼 바르는 모습을 보고는 정말 웃음이 났죠.
치우는 데만 1시간이나 걸려서 정신적으로 많이 지쳤는데,
아기가 깔깔거리며 웃는 모습에 피로가 싹 가시는 것 같았어요.
목욕 후 꿀잠 자는 모습이 너무 사랑스럽고 평온해서, 오늘 하루도 이렇게 행복하게 마무리할 수 있어서 기쁩니다.

        """
    ))
    print("input\n", ai["input"].strip())
    print("\n\n디지털북\n", ai["sp_content"].strip())
