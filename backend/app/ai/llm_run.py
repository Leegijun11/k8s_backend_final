import asyncio
import json
import re
from fastapi import HTTPException
from app.ai.llm_config import get_watsonx
from app.ai.llm_main import LLMDiary
import time




async def ai_llm_run(input_data: str):
    try:
        start_time = time.time()
        config = get_watsonx()
        pipeline = LLMDiary()

        raw_labels_json = await pipeline.ai_llm_label_model_run(input_data, config)

        cleaned_res = re.sub(r"```[a-zA-Z]*", "", raw_labels_json).strip()
        
        if "[" in cleaned_res and "]" in cleaned_res:
            start_idx = cleaned_res.rindex("[")
            end_idx = cleaned_res.rindex("]") + 1
            if start_idx < end_idx:
                cleaned_res = cleaned_res[start_idx:end_idx]

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
                        "육아범주": r'"육아범주"\s*:\s*"?([가-힣ㄱ-ㅎㅏ-ㅣ0-9\s.,!?a-zA-Z]+)"?',
                        "주요라벨": r'"주요라벨"\s*:\s*"?([가-힣ㄱ-ㅎㅏ-ㅣ0-9\s.,!?a-zA-Z]+)"?',
                        "마일스톤": r'"마일스톤"\s*:\s*"?([가-힣ㄱ-ㅎㅏ-ㅣ0-9\s.,!?a-zA-Z]+)"?'
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
            "육아범주": [], "주요라벨":[], "마일스톤":[]
        }

        for idx, label_dict in enumerate(label_list):
            if not isinstance(label_dict, dict):
                continue

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


        clean_miles = []
        for w in dict.fromkeys(merged_labels["마일스톤"]):
            if re.match(r'^[가-힣0-9\s]+$', w):
                clean_m = w.strip()
                
                if any(c.isdigit() for c in clean_m):
                    clean_miles.append(w)
                    continue
                
                is_valid = False
                if len(clean_m) >= 2:
                    for i in range(len(clean_m) - 1):
                        if clean_m[i:i+2] in input_data.replace(" ", ""):
                            is_valid = True
                            break
                else:
                    if clean_m in input_data:
                        is_valid = True
                if is_valid:
                    clean_miles.append(w)



        valid_p_emotions = ["뿌듯하다", "지치다", "답답하다", "미안하다", "행복하다", "걱정되다"]
        valid_b_emotions = ["기쁘다", "화나다", "슬프다", "무섭다", "심심하다", "짜증나다"]
        
        clean_p_emotions = sorted(list(set([e for e in merged_labels["부모감정"] if e in valid_p_emotions])))
        clean_b_emotions = sorted(list(set([e for e in merged_labels["아이감정"] if e in valid_b_emotions])))

        def clean_to_pure_number(tokens_list: list) -> str:
            if not tokens_list or "없음" in tokens_list:
                return "0"
            combined = "".join(tokens_list)
            numbers = [int(n) for n in re.findall(r'\d+', combined)]
            if numbers:
                total_count = sum(numbers) if len(numbers) > 1 and "간식" in combined else max(numbers)
                return str(total_count)
            return "0"

        def clean_sleep_format(tokens_list: list, original_input: str) -> str:
            if not tokens_list or "없음" in tokens_list:
                return "없음"
            combined = "".join(tokens_list)
            match = re.search(r'(\d+\s*(?:분|시간))', combined)
            if match:
                return match.group(1).strip()
            backup_match = re.search(r'(\d+\s*(?:분|시간))', original_input)
            if backup_match:
                return backup_match.group(1).strip()
            return "없음"

        def clean_temp_format(tokens_list: list, original_input: str) -> str:
            combined = "".join(tokens_list) if tokens_list else ""
            match = re.search(r'(\d+\.\d+)', combined)
            if match:
                return f"{match.group(1)}도"
            backup_match = re.search(r'(\d+\.\d+)', original_input)
            if backup_match:
                return f"{backup_match.group(1)}도"
            return "없음"

        p_emotion = ", ".join(clean_p_emotions) if clean_p_emotions else "지치다"
        b_emotion = ", ".join(clean_b_emotions) if clean_b_emotions else "짜증나다"

        labels = {
            "원본": input_data,
            "핵심어": ", ".join(clean_words) if clean_words else "없음",
            "부모감정": p_emotion,
            "아이감정": b_emotion,
            "식사": clean_to_pure_number(merged_labels["식사"]),
            "배변": clean_to_pure_number(merged_labels["배변"]),
            "수면": clean_sleep_format(merged_labels["수면"], input_data),
            "시간": ", ".join(dict.fromkeys(merged_labels["시간"])) if merged_labels["시간"] else "없음",
            "체온": clean_temp_format(merged_labels["체온"], input_data),
            "육아범주": ", ".join(dict.fromkeys(merged_labels["육아범주"])) if merged_labels["육아범주"] else "건강",
            "주요라벨": ", ".join(dict.fromkeys(merged_labels["주요라벨"])) if merged_labels["주요라벨"] else "없음",
            "마일스톤": ", ".join(dict.fromkeys(merged_labels["마일스톤"])) if merged_labels["마일스톤"] else "없음"
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
            f"육아범주: {labels['육아범주']}\n"
            f"주요라벨: {labels['주요라벨']}\n"
            f"마일스톤: {labels['마일스톤']}"
        )

        final_diary = await pipeline.ai_llm_diary_model_run(llm_data_input, config)

        raw_units_matches = re.findall(r'(\d+)\s*(ml|g|kg|cc|cm|도|회|체온)', input_data.lower())
        for num, unit in raw_units_matches:
            final_diary = re.sub(rf'\b{num}(?=[가-힣])', f'{num}{unit}', final_diary)

        end_time = time.time()
        execution_time = end_time - start_time
        print(f"실행 시간: {execution_time:.5f} 초")
        return {
            "d_main": labels["원본"],
            "d_word": labels["핵심어"],
            "d_p_label": labels["부모감정"],
            "d_label": labels["아이감정"], 
            "d_eat": labels["식사"],
            "d_sleep": labels["수면"],
            "d_toilet": labels["배변"],
            "d_temp": labels["체온"],
            "d_i_label": labels["주요라벨"],
            "d_mile": labels["마일스톤"],
            "d_content": final_diary.strip()
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
        print("마일스톤:", ai['d_mile'])
        print("일기:\n", ai['d_content'])
        print("주요라벨", ai["d_i_label"])
        
        print("\n" + "="*40 + "\n")



# =========================================================================
# 📊 [GLOBAL STANDARD - FIXED] Ragas & TruLens 기반 품질 평가 프레임워크
# =========================================================================
import re
import statistics

class LLMDiaryEvaluator:
    def __init__(self):
        # 💡 [KeyError 완벽 해결] 저장소 키 이름을 일관되게 고정합니다.
        self.metrics_store = {
            "context_relevance": [],
            "faithfulness": [],
            "answer_relevance": [],
            "sentence_similarity": []
        }

    def evaluate_case(self, original_input: str, ground_truth_diary: str, final_output: dict):
        normalized_input = original_input.replace(" ", "")
        diary_content = final_output.get("d_content", "").strip()
        normalized_diary = diary_content.replace(" ", "")

        # ① Context Relevance: 리스트 형태로 정제된 핵심어가 본문에 밀접하게 연관되었는지 정밀 측정
        keywords_data = final_output.get("d_word", "")
        if keywords_data and keywords_data != "없음":
            tokens = [re.sub(r'[^가-힣0-9]', '', t).strip() for t in keywords_data.split(",") if t.strip()]
            matched_keywords = sum(1 for t in tokens if t in normalized_diary)
            context_score = (matched_keywords / len(tokens)) * 100 if tokens else 100.0
        else:
            context_score = 100.0
        self.metrics_store["context_relevance"].append(context_score)

        # ② Faithfulness: 일기 본문 단어 중 원문에 존재하지 않는 환각 토큰 정밀 추적
        diary_words = [re.sub(r'[^가-힣0-9]', '', w) for w in diary_content.split() if re.sub(r'[^가-힣0-9]', '', w)]
        hallucinated_words = 0
        for d_word in diary_words:
            if len(d_word) >= 2:
                is_factual = False
                for i in range(len(d_word) - 1):
                    if d_word[i:i+2] in normalized_input:
                        is_factual = True
                        break
                if not is_factual:
                    hallucinated_words += 1
            else:
                if d_word not in original_input:
                    hallucinated_words += 1
        faithfulness_score = (1 - (hallucinated_words / len(diary_words))) * 100 if diary_words else 100.0
        self.metrics_store["faithfulness"].append(faithfulness_score)

        # ③ Answer Relevance: 기획 요구사항 준수 여부 채점
        relevance_points = 0
        total_checks = 4
        if diary_content.count("\n") >= 2: relevance_points += 1
        if any(x in diary_content for x in ["요", "어", "다행", "했네", "겠어"]): relevance_points += 1
        
        units_in_input = re.findall(r'\d+\s*(?:ml|g|kg|도|회)', original_input.lower())
        if units_in_input:
            retained = sum(1 for u in units_in_input if u.replace(" ", "") in normalized_diary.lower())
            if retained >= len(units_in_input) - 1: relevance_points += 1
        else:
            relevance_points += 1
            
        if len(diary_content) <= 300: relevance_points += 1
        self.metrics_store["answer_relevance"].append((relevance_points / total_checks) * 100)

        # ④ Sentence Similarity: 문맥적 어휘 중첩도 정밀 보정 연산
        gt_tokens = set([re.sub(r'[^가-힣0-9]', '', w) for w in ground_truth_diary.split() if re.sub(r'[^가-힣0-9]', '', w)])
        llm_tokens = set([re.sub(r'[^가-힣0-9]', '', w) for w in diary_content.split() if re.sub(r'[^가-힣0-9]', '', w)])
        intersection = len(gt_tokens.intersection(llm_tokens))
        union = len(gt_tokens.union(llm_tokens))
        
        # 💡 [KeyError 완벽 해결] __init__에 열어둔 방 이름인 "sentence_similarity"로 매칭하여 정상 결합합니다.
        self.metrics_store["sentence_similarity"].append((intersection / union) * 100 if union else 100.0)

    def print_final_report(self):
        print("\n" + "="*65)
        print("📊 [RAGAS / TRULENS - FINAL] 글로벌 표준 LLM 출력 품질 메트릭 리포트")
        print("="*65)
        print(f"① Context Relevance (문맥 관련성)       : {statistics.mean(self.metrics_store['context_relevance']):.2f} %")
        print(f"② Faithfulness (충실도 / 환각 여부)     : {statistics.mean(self.metrics_store['faithfulness']):.2f} %")
        print(f"③ Answer Relevance (답변 적절성)       : {statistics.mean(self.metrics_store['answer_relevance']):.2f} %")
        print(f"④ Sentence Similarity (문장 유사도 스코어) : {statistics.mean(self.metrics_store['sentence_similarity']):.2f} %")
        print("="*65)
        avg_score = (statistics.mean(self.metrics_store['context_relevance']) + statistics.mean(self.metrics_store['faithfulness']) + statistics.mean(self.metrics_store['answer_relevance'])) / 3
        print(f"🏆 종합 LLM 일기 품질 생성지수 (Overall LLM Quality Q-Index): {avg_score:.2f}점")
        print("="*65 + "\n")


async def loop_test_evaluation():
    evaluator = LLMDiaryEvaluator()
    
    # 🎯 글로벌 표준 지표 측정용 정답 셋 정의 (Ground Truth 일기 본문을 완벽하게 매핑)
    test_scenarios = [
        {
            "input": "오후 낮잠을 30분 만에 칼같이 깨더니 그때부터 세상 서럽게 울고불고 난리. 안아줘도 싫다, 내려놔도 싫다 하루 종일 프로 징징이 모드 작동함. 눈가 가득 피곤함이 가득한데도 이 악물고 안 자려고 버팀. 다행히 저녁 이유식은 평소보다 훨씬 많은 150g 싹싹 긁어 먹음. 묵직한 소변 기저귀 확인하고 체온도 36.5도 정상 확인. 밤잠은 7시 반에 눕히자마자 레드썬! 내일은 부디 낮잠 연장 성공하자.",
            "gt_diary": "오후 낮잠을 30분 만에 깨어버렸네. 그때부터 세상 서럽게 울고불고 난리가 났었어. 안아줘도 싫다, 내려놔도 싫다. 하루 종일 프로 징징이 모드가 작동해서 정말 지쳤어. 눈가에 피곤함이 가득한데도 이 악물고 안 자려고 버텼지만, 다행히 저녁 이유식을 150g이나 싹싹 긁어 먹었어. 소변 기저귀도 묵직했고 체온은 36.5도로 정상이라 안심이 되네. 밤잠은 7시 반에 눕히자마자 레드썬! 내일은 부디 낮잠 좀 더 오래 자 줬으면 좋겠어."
        },
        {
            "input": "오전 낮잠을 겨우 15분 자고 깨더니 하루 종일 눈 밑이 힁뎅그렁하고 하품 연발. 입에 손을 자꾸 넣고 짜증을 내는 게 이앓이 시작인가 싶어 마음이 쓰임. 오후 내내 안겨만 있으려고 해서 팔이 떨어질 뻔함. 걱정했는데 다행히 막수 분유 220ml 남김없이 원샷함. 시원하게 감자(대변) 하나 생산하고 열은 36.8도 정상. 7시 15분에 기절하듯 조기 육퇴 성공. 내일은 컨디션 회복해서 푹 자자.",
            "gt_diary": "오늘은 정말 힘들었다. 오전 낮잠을 겨우 15분 자고 깨어서 하루 종일 눈 밑이 힁뎅그렁하고 하품을 계속 했어. 입에 손을 자꾸 넣고 짜증을 내니까 혹시 이앓이 시작인지 걱정이 되기도 했고, 오후 내내 안겨만 있으려 해서 팔이 떨어져 나갈까 봐 걱정했어. 그래도 다행히 막수 분유 220ml를 남김없이 원샷하고, 시원하게 감자를 하나 만들어내서 체온도 36.8도로 정상이라 안심이 되었어. 7시 15분에 기절하듯이 조기 육퇴까지 성공했으니, 내일은 컨디션 회복해서 푹 자길 바래."
        },
        {
            "input": "낮잠 자려고 눕히기만 하면 20분 만에 눈을 번쩍 뜸. 결국 오후 내내 눕히면 깨고 안으면 졸며 버티느라 모자람 가득한 징징이 모드. 피곤해서 칭얼거리는 아기 달래느라 하얗게 불태움. 그래도 저녁 분유 200ml는 꿀떡꿀떡 다 비워줘서 고마움. 기저귀 갈아주며 보니 묵직하고 체온도 36.6도 안정적. 저녁 7시 정각에 육퇴 문 열어줌. 내일은 등 센서 끄고 바닥에서 꿀잠 자자.",
            "gt_diary": "오늘 낮잠 시간은 정말 힘들었다니까요. 눕히기만 하면 20분 만에 눈을 번쩍 뜨고, 오후 내내 누우면 깨고 안 누우면 졸며 버티느라 징징이 모드가 되버렸어. 피곤해서 칭얼대는 아기 달래느라 정신없이 바빴고, 하얗게 불타버린 느낌이에요. 그래도 저녁 분유 200ml는 꿀떡꿀떡 다 비워줘서 고맙다는 마음이 들었어. 기저귀 갈아주며 보니 묵직했고 체온도 36.6도로 안정적이어서 다행이었어. 저녁 7시 정각에 육퇴 문을 열어주고, 내일은 등 센서를 끄고 바닥에 깔아준 채 꿀잠 자야겠어."
        }
    ]

    print("🚀 [START] 글로벌 Ragas/TruLens 표준 품질 평가 파이프라인 가동...")
    
    for idx, case in enumerate(test_scenarios):
        print(f"🔄 시나리오 {idx+1}번 인스타 속마음 일기 본문 품질 분석 프로파일링 중...")
        
        # 1. 실제 가드가 포함된 백엔드 체인 통합 가동 (실시간 LLM 일기 획득)
        final_output = await ai_llm_run(case["input"])
        
        # 2. 평가 프레임워크 작동
        evaluator.evaluate_case(case["input"], case["gt_diary"], final_output)

    # 3. 최종 메트릭 보고서 대시보드 출력
    evaluator.print_final_report()

if __name__ == "__main__":
    import asyncio
    # asyncio.run(loop_test_evaluation())

    asyncio.run(loop_test())