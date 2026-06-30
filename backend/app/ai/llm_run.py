import asyncio
import json
import re
from fastapi import HTTPException
from app.ai.llm_config import get_watsonx
from app.ai.llm_main import LLMDiary
from collections import Counter


async def ai_llm_run(input: str):
    try:
        config = get_watsonx()
        pipeline = LLMDiary()

        raw_labels_json = await pipeline.ai_llm_label_model_run(input, config)

        cleaned_res = re.sub(r"```[a-zA-Z]*", "", raw_labels_json).strip()
        if "[" in cleaned_res:
            cleaned_res = cleaned_res[cleaned_res.index("["):]
        if "]" in cleaned_res:
            cleaned_res = cleaned_res[:cleaned_res.rindex("]") + 1]

        label_list = []
        try:
            label_list = json.loads(cleaned_res)
        except json.JSONDecodeError:
            try:
                dict_blocks = re.findall(r"\{[^{}]*\}", cleaned_res)
                for block in dict_blocks:
                    extracted = {}
                    patterns = {
                        "핵심어": r'"핵심어"\s*:\s*"?([가-힣ㄱ-ㅎㅏ-ㅣ0-9\s.,!?a-zA-Z]+)"?',
                        "부모감정": r'"부모감정"\s*:\s*"?([가-힣ㄱ-ㅎㅏ-ㅣ0-9\s.,!?a-zA-Z]+)"?',
                        "감정": r'"감정"\s*:\s*"?([가-힣ㄱ-ㅎㅏ-ㅣ0-9\s.,!?a-zA-Z]+)"?',
                        "식사": r'"식사"\s*:\s*"?([가-힣ㄱ-ㅎㅏ-ㅣ0-9\s.,!?a-zA-Z]+)"?',
                        "배변": r'"배변"\s*:\s*"?([가-힣ㄱ-ㅎㅏ-ㅣ0-9\s.,!?a-zA-Z]+)"?',
                        "수면": r'"수면"\s*:\s*"?([가-힣ㄱ-ㅎㅏ-ㅣ0-9\s.,!?a-zA-Z]+)"?',
                        "시간": r'"시간"\s*:\s*"?([가-힣ㄱ-ㅎㅏ-ㅣ0-9\s.,!?a-zA-Z]+)"?',
                        "체온": r'"체온"\s*:\s*"?([가-힣ㄱ-ㅎㅏ-ㅣ0-9\s.,!?a-zA-Z]+)"?',
                        "육아범주": r'"육아범주"\s*:\s*"?([가-힣ㄱ-ㅎㅏ-ㅣ0-9\s.,!?a-zA-Z]+)"?'
                    }

                    for key, pattern in patterns.items():
                        match = re.search(pattern, block)
                        if match:
                            val = match.group(1).strip().strip('"').strip("'").strip('}')
                            extracted[key] = val
                    if extracted:
                        label_list.append(extracted)
            except Exception:
                label_list = []

        merged_labels = {
            "핵심어": [], "부모감정": [], "감정": [], "식사": "없음", "배변": "없음", 
            "수면": "없음", "시간": "없음", "체온": "없음", "육아범주": []
        }
        raw_sentences = []

        for idx, label_dict in enumerate(label_list):
            if not isinstance(label_dict, dict):
                continue

            orig = label_dict.get("원본", "").strip()
            if orig:
                if not orig.endswith(('.', '!', '?')):
                    orig += '.'
                raw_sentences.append(f"이벤트 {idx+1}: {orig}")

            if label_dict.get("핵심어") and label_dict["핵심어"] != "없음":
                merged_labels["핵심어"].append(label_dict["핵심어"])
            if label_dict.get("부모감정") and label_dict["부모감정"] != "없음":
                merged_labels["부모감정"].append(label_dict["부모감정"])
            if label_dict.get("감정") and label_dict["감정"] != "없음":
                merged_labels["감정"].append(label_dict["감정"])
            if label_dict.get("육아범주") and label_dict["육아범주"] != "없음":
                merged_labels["육아범주"].append(label_dict["육아범주"])
                
            for key in ["식사", "배변", "수면", "시간", "체온"]:
                if label_dict.get(key) and label_dict[key] != "없음":
                    merged_labels[key] = label_dict[key]

        structured_text = "\n".join(raw_sentences)

        if merged_labels["부모감정"]:
            p_emotion = Counter(merged_labels["부모감정"]).most_common(1)[0][0]
        else:
            p_emotion = "평온하다"

        if merged_labels["감정"]:
            b_emotion = Counter(merged_labels["감정"]).most_common(1)[0][0]
        else:
            b_emotion = "기쁘다"

        labels = {
            "원본": input,
            "핵심어": pipeline.clean_raw_text(", ".join(merged_labels["핵심어"])) if merged_labels["핵심어"] else "없음",
            "부모감정": p_emotion,
            "감정": b_emotion,
            "식사": merged_labels["식사"],
            "배변": merged_labels["배변"],
            "수면": merged_labels["수면"],
            "시간": merged_labels["시간"],
            "체온": merged_labels["체온"],
            "육아범주": merged_labels["육아범주"][-1] if merged_labels["육아범주"] else "건강",
            "perfect_match_input": structured_text
        }

        llm_data_input = (
            f"원본: {labels['원본']}\n"
            f"핵심어: {labels['핵심어']}\n"
            f"부모감정: {labels['부모감정']}\n"
            f"감정: {labels['감정']}\n"
            f"식사: {labels['식사']}\n"
            f"수면: {labels['수면']}\n"
            f"배변: {labels['배변']}\n"
            f"체온: {labels['체온']}\n"
            f"육아범주: {labels['육아범주']}"
        )

        final_diary = await pipeline.ai_llm_diary_model_run(llm_data_input, config)

        return {
            "d_main": labels["원본"],
            "d_word": labels["핵심어"],
            "d_p_label": labels["부모감정"],
            "d_label": labels["감정"], 
            "d_eat": labels["식사"],
            "d_sleep": labels["수면"],
            "d_toilet": labels["배변"],
            "d_temp": labels["체온"],
            "d_content": final_diary
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"자동 일기 파이프라인 가동 실패 원인: {str(e)}")


if __name__ == "__main__":
    ai = asyncio.run(ai_llm_run(
        """

        오늘 큰맘 먹고 거실에 비닐 깔고 두부 촉감놀이 시작함. 처음엔 무서워서 손가락만 콕콕 찌르더니, 나중에는 온몸으로 두부를 으깨고 머리에 샴푸 하듯 바름. 치우는 데만 1시간 걸려서 내 영혼은 털렸지만, 아기가 깔깔거리며 웃는 모습에 피로가 싹 가심. 목욕 후 꿀잠 자는 모습이 너무 사랑스러움.
        
        """
    ))

    print("원본", ai["d_main"])
    print("핵심", ai["d_word"])
    print("부모", ai['d_p_label'])
    print("감정", ai['d_label'])
    print("식사", ai['d_eat'])
    print("수면", ai['d_sleep'])
    print("배변", ai['d_toilet'])
    print("체온", ai['d_temp'])
    print("일기\n", ai['d_content'])
