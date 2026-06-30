from fastapi import HTTPException
from langchain_ibm import ChatWatsonx
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import re

class LLMDiary:
    def __init__(self):
        self.ai_llm_label_model = None
        self.ai_llm_diary_model = None


    def get_ai_llm_label_model(self, config: dict) -> ChatWatsonx:
        if self.ai_llm_label_model is None:
            extract_params = {
                "decoding_method": "greedy",
                "min_new_tokens": 10,
                "max_new_tokens": 500,
                "repetition_penalty": 1.0,
            }
            
            self.ai_llm_label_model = ChatWatsonx(
                model_id="mistralai/mistral-small-3-1-24b-instruct-2503",
                url=config["credentials"]["url"],
                apikey=config["credentials"]["apikey"],
                project_id=config["project_id"],
                params=extract_params
            )
        return self.ai_llm_label_model
    

    def get_ai_llm_diary_model(self, config: dict) -> ChatWatsonx:
        if self.ai_llm_diary_model is None:
            creative_params = {
                "decoding_method": "sample",
                "min_new_tokens": 10,
                "max_new_tokens": 150,
                "repetition_penalty": 1.15,
                "temperature": 0.2,
                "top_p": 0.8,
                "stop_sequences": ["\n\n", "[END]"]
            }
            
            self.ai_llm_diary_model = ChatWatsonx(
                model_id="mistralai/mistral-small-3-1-24b-instruct-2503",
                url=config["credentials"]["url"],
                apikey=config["credentials"]["apikey"],
                project_id=config["project_id"],
                params=creative_params
            )
        return self.ai_llm_diary_model
    

    def clean_raw_text(self, text):
        if not text:
            return ""

        text = re.sub(r'(?i)(\d+\.?\d*)\s*ml', r'\1밀리리터보존', text)
        text = re.sub(r'(?i)(\d+\.?\d*)\s*kg', r'\1킬로그램보존', text)
        text = re.sub(r'(?i)(\d+\.?\d*)\s*cc', r'\1씨씨보존', text)
        text = re.sub(r'(?i)(\d+\.?\d*)\s*cm', r'\1센티미터보존', text)
        text = re.sub(r'(?i)(\d+\.?\d*)\s*g\b', r'\1그램보존', text)
        text = re.sub(r'(\d+\.?\d*)\s*℃', r'\1도씨보존', text)

        text = re.sub(r'[^가-힣ㄱ-ㅎㅏ-ㅣ0-9\s.,!?]', '', text)
        
        text = text.replace('밀리리터보존', 'ml')
        text = text.replace('킬로그램보존', 'kg')
        text = text.replace('씨씨보존', 'cc')
        text = text.replace('센티미터보존', 'cm')
        text = text.replace('그램보존', 'g')
        text = text.replace('도씨보존', '도')

        text = re.sub(r'[ \t]+', ' ', text)
        return text.strip()
    
    def structure_diary_context(self, raw_text):
        cleaned = self.clean_raw_text(raw_text)
        if not cleaned:
            return "이벤트 1: 기록된 내용이 없습니다."
        
        raw_sentences = []
        lines = cleaned.split('\n')
        for line in lines:
            split_sentences = re.split(r'(?<=[.!?])\s+', line)
            for s in split_sentences:
                if s.strip():
                    raw_sentences.append(s.strip())
        
        structured_context = []
        for idx, sentence in enumerate(raw_sentences):
            if not sentence.endswith(('.', '!', '?')):
                sentence += '.'
            structured_context.append(f"이벤트 {idx+1}: {sentence}")
            
        return "\n".join(structured_context)
   

    async def ai_llm_label_model_run(self, input: str, config: dict) -> str:

        prompt = ChatPromptTemplate.from_template("""[Instruction]
                                                    당신은 육아 기록 전문가입니다.
                                                    주어진 [Data]의 각 문장을 순서대로 정밀 분석하여 아래 [Output Format] 양식에 맞춰 오직 핵심 라벨 결과만 깨끗하게 출력하세요.

                                                    [추출 규칙]
                                                    1. "원본" 항목에는 주어진 [Data]의 문장을 글자, 띄어쓰기, 문장 부호까지 있는 그대로 복사하여 붙여넣기하세요.
                                                    2. "핵심어"는 원본에서 '누가(주체)', '무엇을 하다(행동)', '무엇을(대상)', '상태나 장소'를 나타내는 핵심 단어들을 골라 있는 그대로 최소 3개 이상 찾아서 모두 나열하세요.
                                                    3. "식사", "배변", "수면", "체온" 항목은 수치뿐만 아니라 거부, 남김, 무난함 등 상태와 결과를 나타내는 단어를 반드시 포함하여 간결하게 요약하세요. 
                                                    - 명확한 종류가 언급되었다면 문장 형태가 아닌 해당 단어 위주로만 정확하게 추출하세요. (예: 밤잠, 낮잠 1시간, 설사 2회, 분유 3회)
                                                    4. 모든 출력 결과는 '한국어'만 사용하지만 원문에 한국어 외의 글자가 직접 적혀 있는 경우에만 해당 글자를 변형 없이 그대로 결과에 포함하여 출력하세요. 
                                                    5. [Output Format]의 9개 항목은 모든 문장마다 무조건 전부 화면에 나타나야 하고 원문에 내용이 없거나 추출할 수 없는 항목은 '없음'이라는 두 글자를 채워서 출력하세요.
                                                    6. 문맥을 파악하여 행동을 행한 주체(예: 아기, 엄마 등)가 누구인지 명확히 인지하고 추출을 진행하세요.

                                                    [카테고리 규칙]
                                                    - 부모감정: 뿌듯하다, 지치다, 답답하다, 미안하다, 평온하다, 걱정되다 중 오직 하나만 선택
                                                    - 감정: 기쁘다, 화나다, 슬프다, 무섭다, 심심하다, 짜증나다 중 오직 하나만 선택

                                                    - 육아범주 라벨 후보:
                                                    수면, 식사, 사회성, 운동, 언어, 배변, 정서, 인지, 건강, 의복
                                                    이 중에서 가장 적합성이 높은 하나만 선택하세요.                                                

                                                    [Output Format]
                                                    [
                                                    {{
                                                        "원본": "첫 번째 문장 그대로 복사",
                                                        "핵심어": "핵심 단어들 나열",
                                                        "부모감정": "감정 라벨 중 하나 선택",
                                                        "감정": "아이의 감정 라벨 중 하나 선택",
                                                        "식사": "수치와 단위를 포함하여 출력 또는 없음",
                                                        "배변": "배변 관련 내용 또는 없음",
                                                        "수면": "수면 관련 내용 또는 없음",
                                                        "시간": "시간대 또는 없음",
                                                        "체온": "체온 수치 또는 없음",
                                                        "육아범주": "육아범주 중 하나"
                                                    }},
                                                    {{
                                                        "원본": "두 번째 문장 그대로 복사",
                                                        ...
                                                    }}
                                                    ]

                                                    [Data]
                                                    {input}

                                                    [Output]:""")

        try:
            model = self.get_ai_llm_label_model(config)

            chain = prompt | model | StrOutputParser()
            input=input.strip()
            keywords = await chain.ainvoke({"input": input})
            return keywords.strip()
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Watsonx 2단계 라벨 추출 중 예외 발생: {str(e)}")
        

    async def ai_llm_diary_model_run(self, input: str, config: dict) -> str:

        prompt = ChatPromptTemplate.from_template("""
                                                  너는 인스타그램에서 오늘 하루의 기록을 다정하고 솔직하게 독백 형태로 공유하는 대한민국 엄마이다.
                                                  관찰자나 제3자가 아닌, 진짜 내 아기를 키우는 엄마의 다정한 시선에서 솔직한 속마음 일기를 작성해라.
                                                  제공된 [Data]의 '원본'을 바탕으로, 명시된 '핵심어', '부모감정', '육아범주' 라벨 정보들을 조합하여 자연스러운 한국어 일기를 작성해라.

                                                  [작성 규칙]
                                                    1. 국립국어원 표준 맞춤법을 준수하되, 실제 엄마들이 친근한 혼잣말을 할 때 쓰는 자연스러운 구어체 어미를 사용하여 일관성 있고 부드러운 톤앤매너를 유지하세요. 
                                                    2. [Data]의 원본에 담긴 사건의 순서를 자연스럽게 이어 나가되, 한국어의 흐름상 문장들이 물 흐르듯 부드럽게 연결되도록 문맥의 가독성을 최우선으로 하세요.
                                                    3. 명확한 성별 단어가 있는 경우 아들이나 딸을 사용하고 공통 육아 단어만 사용하세요.
                                                    4. 주어진 '핵심어'들과 '부모감정' 라벨의 의미가 문장 속에 녹여내어, 솔직하고 다정한 생활 밀착형 감정 표현으로 친근한 표현을 적절히 활용하거나, 주어를 자연스럽게 생략하여 온전히 내 가족의 이야기로 느껴지게 쓰세요
                                                    5. 육아 일기이므로 모든 행동의 주체는 '아기'입니다. 한국어 문맥상 자연스럽게 주어를 생략하거나 다른 표현으로 다채롭게 분산시키세요.
                                                    6. '원본'이나 '식사'에 적힌 수치의 단위(ml, kg, cc, cm, ℃ 등)를 단 한 글자도 생략하지 말고 숫자 뒤에 반드시 붙여서 사용하라. 
                                                    7. 문장마다 줄바꿈을 하고, 전체 분량은 인스타그램 피드에 알맞게 3~4줄(공백 포함 150자 내외)로 작성하세요.
                                                    8. 모든 문장 작성을 완료한 바로 다음 줄에 [AI_LLM_DIARY_END]를 출력하세요.
                                                  
                                                    [예시1]
                                                    원본: 오전 낮잠 20분 만에 깨더니 하루 종일 눈 밑이 힁뎅그렁함. 졸리면서 안 자겠다고 버티느라 오후 내내 징징 모드. 다행히 저녁 분유는 200ml 원샷하고 기절하듯 7시 조기 육퇴함. 소변 기저귀 묵직하고 체온은 36.7도 정상. 내일은 낮잠 좀 푹 자자. 
                                                    핵심어: 낮잠, 깨다, 눈밑, 징징, 분유, 원샷, 기절, 육퇴, 체온, 정상
                                                    부모감정: 평온하다
                                                    감정: 짜증나다
                                                    식사: 분유 200ml
                                                    수면: 낮잠 20분
                                                    배변: 소변 기저귀 1회
                                                    체온: 36.7도
                                                    육아범주: 건강

                                                    출력 일기:
                                                    오늘 아침부터 낮잠을 20분 만에 깨더니 하루 종일 눈 밑이 힁뎅그렁하더라고요.
                                                    졸리면서도 안 자겠다고 버티느라 오후 내내 징징 모드여서 조금 속상했답니다.
                                                    다행히 저녁에는 200ml 분유를 원샷하고 기절하듯 7시에 일찍 잠들어주었네요.
                                                    소변 기저귀도 묵직하고 체온은 36.7도로 정상이라 다행이에요. 내일은 낮잠 좀 푹 자 주면 좋겠네요.

                                                    [예시2]
                                                    원본: 오늘 완전 먹고 자는 날인 듯. 아침 분유 먹고 기절하듯 2시간 자고, 깨서 점심 이유식 완밥하더니 오후에 또 유모차에서 1시간 반 꿀잠 잠. 소변 기저귀 엄청 자주 갈아줌. 잘 자고 일어나서 기분 좋은지 혼자 옹알이 폭발함. 체온 36.6도 건강 이상 무! 
                                                    핵심어: 먹고 자다, 아침, 분유, 기절, 2시간, 깨다, 점심, 이유식 완밥, 오후, 유모차, 1시간 반 꿀잠, 소변 기저귀, 자고 일어나다, 기분 좋다, 옹알이 폭발, 체온 36.6도, 건강 이상 무
                                                    부모감정: 기쁘다
                                                    감정: 기쁘다
                                                    식사: 아침 분유, 점심 이유식 완밥
                                                    수면: 아침 2시간, 오후 1시간반
                                                    배변: 소변 기저귀 자주
                                                    체온: 36.6도
                                                    육아범주: 식사, 수면

                                                    출력 일기:
                                                    오늘 아침부터 완전 먹고 자는 날인 듯한 느낌이 드네요. 아침 분유를 먹고 기절하듯 2시간을 푹 자고 일어나더라고요.
                                                    깨서 점심 이유식은 기특하게 완밥하더니, 오후에 또 유모차에서 1시간 반이나 꿀잠을 자 주었어요.
                                                    소변 기저귀는 엄청 자주 갈아주며 수시로 챙겨주었답니다. 잘 자고 일어나서 기분이 좋은지 혼자 신나서 옹알이가 폭발하는데 그 모습이 어찌나 귀엽고 예쁜지 몰라요.
                                                    체온도 36.6도로 정상이라 오늘도 건강 이상 무, 참 기쁜 하루였어요.

                                                  [Data]
                                                  {input}

                                                  [Diary]:""")
        
        try:
            model = self.get_ai_llm_diary_model(config)
            chain = prompt | model | StrOutputParser()
            
            raw_diary = await chain.ainvoke({"input": input})
            cleaned_diary = self.clean_raw_text(raw_diary)
            
            return cleaned_diary.strip()    
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Watsonx 3단계 일기 생성 중 예외 발생: {str(e)}")
        
        
    async def ai_llm_story_model_run(self, input: str, config: dict) -> str:

        prompt = ChatPromptTemplate.from_template("""
                                                너는 아이의 시점으로 오늘 일상에 대한 일기를 작성할 거야.
                                                제공된 [Data]의 '원본'을 바탕으로 자연스러운 한국어 일기를 작성해라.
                                                수치 관련 정보는 누락하라.
                                                      
                                                [예시1]
                                                원본 
                                                아침부터 컨디션이 최고였는지 웃으며 아주 잘 놀 기세였어요. 점심 이유식을 한 그릇 싹 다 비우고도 모자라 더 달라고 칭얼거리는 모습이 어찌나 귀엽던지요.
                                                낮 시간이 한참 지나도 침대에 누워 잘 생각이 전혀 없어 보였는데, 다행히 3시쯤 유모차를 타자마자 마법처럼 잠들어 1시간 동안 푹 자주었답니다.
                                                따끈한 몸을 안아 올리며 체온을 재보니 36.6도로 정상이었어요. 잘 먹고 잘 놀아준 덕분에 오늘도 무사히 하루가 저물어가네요.
                                                내일도 오늘처럼 밥 잘 먹고 방글방글 웃으며 행복하게 보내주길 바라요. 
                                                  
                                                출력 일기:
                                                오늘 아침에 눈뜨자마자 기분이 너무 좋아서 엄마한테 방긋방긋 미소 날려줬어요! 
                                                점심 맘마가 대빵 맛있어서 꿀꺽 다 먹구 더 달라고 찡찡거렸어요. 
                                                낮에는 침대 누웠는데도 눈이 초롱초롱했는데, 유모차 타자마자 시원한 바람 솔솔 불어서 나도 모르게 쿨쿨 잠들었어요! 
                                                땀 뻘뻘 흘리면서 개운하게 자고 일어나니까 이마도 뽀송뽀송하고 건강하대요!
                                                내일도 밥 잘 먹고 웃으며 놀아요. 사랑해요!
                                                  
                                                [예시2]
                                                원본
                                                낮잠을 겨우 20분 만에 깨버려서 눈 밑이 휑뎅그렁해졌어요. 졸리면서도 안 자려고 버티는 통에 오후 내내 징징거림을 받아내느라 애를 먹었네요.
                                                그래도 저녁에는 분유 200ml를 단숨에 원샷하고 기절하듯 잠들어주어 고마울 따름이에요. 
                                                덕분에 저녁 7시, 뜻밖의 이른 육퇴를 선물 받아 정말 좋았답니다. 묵직해진 소변 기저귀를 갈아주고 체온을 재보니 36.7도로 정상이었어요. 
                                                내일은 꼭 낮잠 좀 푹 자주길 바라요. 푹 자줘야 엄마도 숨을 좀 돌리지요. 내일은 우리 둘 다 푹 쉬었으면 좋겠어요!
                                                
                                                출력 일기:
                                                오늘 낮잠을 눈 깜짝할 사이에 깨버려서 하루 종일 피곤했어요. 
                                                졸려 죽겠는데 눈은 자꾸 떠지고 마음대로 안 돼서 오후 내내 엄마한테 징징 모드로 투정 부렸어요. 
                                                그래도 저녁 우유는 꿀맛이라 단숨에 먹었는데 눈 뜨니까 폭신한 침대였어요. 
                                                묵직한 소변 기저귀 뽀송하게 갈아입고 이마 삑삑이 하니까 정상이래요! 
                                                엄마 미안해요, 내일은 꼭 낮잠 푹 자고 일어나서 같이 재미있게 놀아요. 사랑해요!
                                                  
                                                [예시3]
                                                원본
                                                날씨 좋아서 오후에 아빠하고 유모차를 태워서 동네 한 바퀴 돌고 왔어요. 밖이 신기한지 두리번거리며 구경 잘 하다가 집에 거의 다와서 잠이 들었네요.
                                                다녀와서 시원하게 대변 보고 기분이 좋은지 방긋방긋 웃는게 정말 귀여웠어요. 하루 종일 열도 없고 36.4도 완전 건강했어요.
                                                방긋 웃는 얼굴을 보니 마음이 참 든든하고 행복하네요.
 
                                                출력 일기:
                                                오늘 날씨가 빤짝반짝해서 아빠가 유모차 태워주고 밖으로 슝 나갔어요! 
                                                초록 나무랑 지나가는 사람들이 너무 신기해서 두리번두리번 구경하다가 나도 모르게 스르륵 잠들었어요.
                                                집에 와서 시원하게 응가까지 뿡 싸서 기분 날아갈 것 같아요! 이마도 안 뜨겁고 완전 건강하대요!
                                                내일도 아빠랑 같이 놀면 좋겠어요.

                                                [Data]
                                                {input}

                                                [Story]:""")

        try:
            model = self.get_ai_llm_diary_model(config)
            chain = prompt | model | StrOutputParser()
            
            raw_diary = await chain.ainvoke({"input": input})
            cleaned_diary = self.clean_raw_text(raw_diary)
            
            return cleaned_diary.strip()    
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Watsonx 4단계 디지털북 생성 중 예외 발생: {str(e)}")