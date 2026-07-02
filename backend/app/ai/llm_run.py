import asyncio
import json
import re
from fastapi import HTTPException
from app.ai.llm_config import get_watsonx
from app.ai.llm_main import LLMDiary
from collections import Counter


async def ai_llm_run(input_data: str):
    try:
        config = get_watsonx()
        pipeline = LLMDiary()

        raw_labels_json = await pipeline.ai_llm_label_model_run(input_data, config)

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
                        "아이감정": r'"아이감정"\s*:\s*"?([가-힣ㄱ-ㅎㅏ-ㅣ0-9\s.,!?a-zA-Z]+)"?',
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
            "핵심어": [], "부모감정": [], "아이감정": [], 
            "식사": [], "배변": [], "수면": [], "시간": [], "체온": [], 
            "육아범주": []
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

            for key in merged_labels.keys():
                val = label_dict.get(key, "").strip()
                if val and val != "없음":
                    tokens = [t.strip() for t in val.split(",") if t.strip()]
                    merged_labels[key].extend(tokens)

        clean_words = []
        for w in dict.fromkeys(merged_labels["핵심어"]):
            if re.match(r'^[가-힣0-9\s]+$', w):
                clean_token = w.strip()
                
                if any(c.isdigit() for c in clean_token):
                    clean_words.append(w)
                    continue
                
                is_valid = False
                if len(clean_token) >= 2:
                    for i in range(len(clean_token) - 1):
                        if clean_token[i:i+2] in input_data.replace(" ", ""):
                            is_valid = True
                            break
                else:
                    if clean_token in input_data:
                        is_valid = True
                if is_valid:
                    clean_words.append(w)

        valid_p_emotions = ["뿌듯하다", "지치다", "답답하다", "미안하다", "행복하다", "걱정되다"]
        valid_b_emotions = ["기쁘다", "화나다", "슬프다", "무섭다", "심심하다", "짜증나다"]
        
        clean_p_emotions = [e for e in dict.fromkeys(merged_labels["부모감정"]) if e in valid_p_emotions]
        clean_b_emotions = [e for e in dict.fromkeys(merged_labels["아이감정"]) if e in valid_b_emotions]

        def clean_metric_label(tokens_list: list, original_input: str) -> str:
            if not tokens_list:
                return "없음"
            valid_tokens = []
            for token in tokens_list:
                clean_token = re.sub(r'[^가-힣0-9\.]', '', token).strip()
                if clean_token in original_input.replace(" ", "") or any(x in token for x in ["회", "정상", "안정", "원샷"]):
                    valid_tokens.append(token)
            return ", ".join(dict.fromkeys(valid_tokens)) if valid_tokens else "없음"

        p_emotion = ", ".join(clean_p_emotions) if clean_p_emotions else "지치다"
        b_emotion = ", ".join(clean_b_emotions) if clean_b_emotions else "짜증나다"

        labels = {
            "원본": input_data,
            "핵심어": ", ".join(clean_words) if clean_words else "없음",
            "부모감정": p_emotion,
            "아이감정": b_emotion,
            "식사": clean_metric_label(merged_labels["식사"], input_data),
            "배변": clean_metric_label(merged_labels["배변"], input_data),
            "수면": clean_metric_label(merged_labels["수면"], input_data),
            "시간": ", ".join(dict.fromkeys(merged_labels["시간"])) if merged_labels["시간"] else "없음",
            "체온": clean_metric_label(merged_labels["체온"], input_data),
            "육아범주": ", ".join(dict.fromkeys(merged_labels["육아범주"])) if merged_labels["육아범주"] else "건강"
        }

        llm_data_input = (
            f"원본: {labels['원본']}\n"
            f"핵심어: {labels['핵심어']}\n"
            f"부모감정: {labels['부모감정']}\n"
            f"아이감정: {labels['아이감정']}\n"
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
            "d_label": labels["아이감정"], 
            "d_eat": labels["식사"],
            "d_sleep": labels["수면"],
            "d_toilet": labels["배변"],
            "d_temp": labels["체온"],
            "d_content": final_diary
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"자동 일기 파이프라인 가동 실패 원인: {str(e)}")



async def loop_test():
    label = [
        "오후 낮잠을 30분 만에 칼같이 깨더니 그때부터 세상 서럽게 울고불고 난리. 안아줘도 싫다, 내려놔도 싫다 하루 종일 프로 징징이 모드 작동함. 눈가 가득 피곤함이 가득한데도 이 악물고 안 자려고 버팀. 다행히 저녁 이유식은 평소보다 훨씬 많은 150g 싹싹 긁어 먹음. 묵직한 소변 기저귀 확인하고 체온도 36.5도 정상 확인. 밤잠은 7시 반에 눕히자마자 레드썬! 내일은 부디 낮잠 연장 성공하자.",
        "오전 낮잠을 겨우 15분 자고 깨더니 하루 종일 눈 밑이 힁뎅그렁하고 하품 연발. 입에 손을 자꾸 넣고 짜증을 내는 게 이앓이 시작인가 싶어 마음이 쓰임. 오후 내내 안겨만 있으려고 해서 팔이 떨어질 뻔함. 걱정했는데 다행히 막수 분유 220ml 남김없이 원샷함. 시원하게 감자(대변) 하나 생산하고 열은 36.8도 정상. 7시 15분에 기절하듯 조기 육퇴 성공. 내일은 컨디션 회복해서 푹 자자.",
        "낮잠 자려고 눕히기만 하면 20분 만에 눈을 번쩍 뜸. 결국 오후 내내 눕히면 깨고 안으면 졸며 버티느라 모자람 가득한 징징이 모드. 피곤해서 칭얼거리는 아기 달래느라 하얗게 불태움. 그래도 저녁 분유 200ml는 꿀떡꿀떡 다 비워줘서 고마움. 기저귀 갈아주며 보니 묵직하고 체온도 36.6도 안정적. 저녁 7시 정각에 육퇴 문 열어줌. 내일은 등 센서 끄고 바닥에서 꿀잠 자자.",
        "낮잠을 20분 만에 깨고는 하루 종일 눈이 껌뻑껌뻑, 졸린 기색이 역력함. 성장기인지 오후 내내 유독 사소한 일에도 찡찡거리며 껌딱지처럼 달라붙음. 허리가 부서질 것 같았지만 저녁 막수 때 분유 210ml를 한 번도 안 쉬고 다 마심. 소변 양 넉넉하고 열 없는 것(36.7도) 확인 완료. 칭칭대던 게 무색하게 6시 50분에 바로 골아떨어짐. 내일은 깨지 말고 낮잠 푹 자길.",
        "잠깐 외출했다가 낮잠 타이밍을 놓쳐서 20분밖에 못 잠. 차에서 깨더니만 눈 밑이 쾡해진 채로 오후 내내 짜증 지수 폭발. 졸리면 자면 되는데 왜 버티는지 의문. 영혼 탈탈 털렸으나 저녁 분유 200ml는 대견하게 완분함. 쉬 기저귀 빵빵하고 체온은 36.5도로 지극히 정상. 피곤했는지 7시도 안 되어서 딥슬립 들어가심. 조기 육퇴 감사하며, 내일은 집에서 푹 자자.",
    ]

    for idx, text in enumerate(label):
        ai = await ai_llm_run(text)
        
        print(f"--- 분석 결과 ({idx + 1}) ---") 
        print("원본:", ai["d_main"])
        print("핵심:", ai["d_word"])
        print("부모:", ai['d_p_label'])
        print("아이:", ai['d_label'])
        print("식사:", ai['d_eat'])
        print("수면:", ai['d_sleep'])
        print("배변:", ai['d_toilet'])
        print("체온:", ai['d_temp'])
        print("일기:\n", ai['d_content'])
        print("\n" + "="*40 + "\n")




if __name__ == "__main__":
    asyncio.run(loop_test())
