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
                "stop_sequences": ["\n\n", "[AI_LLM_DIARY_END]"]
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
    

    async def ai_llm_label_model_run(self, input_data: str, config: dict) -> str:

        prompt = ChatPromptTemplate.from_template("""[Instruction]
                                                    당신은 대한민국 육아 기록 전문가입니다.
                                                    주어진 [Data]의 문장을 정밀 분석하여 아래 [예시] 양식에 맞춰 깨끗하게 출력하세요.

                                                    [추출 규칙]
                                                    1. "원본" 항목에는 주어진 [Data]의 문장을 글자, 띄어쓰기, 문장 부호까지 있는 그대로 복사하여 붙여넣기하세요.
                                                    2. 모든 출력 항목은 오직 표준 한국어(한글)와 숫자만을 결합하여 구성하세요. 원문에 실재하는 글자와 수치 형태를 그대로 결과에 포함하여 출력하세요.
                                                    3. "핵심어"는 원본 문장에 적혀 있는 글자 형태(어절 또는 명사 가독 단어)를 그대로 골라 최소 3개 이상 찾아서 나열하세요.
                                                    4. "식사", "배변", "수면" 항목은 해당되는 내용이 존재하면 수를 세어 횟수를 추출하고 "체온"이 존재하면 추출하세요.
                                                    5. [예시]의 모든 항목은 누락 없이 전부 화면에 출력되어야 하며, 원문에 내용이 없거나 추출할 수 없는 항목은 오직 '없음'이라는 두 글자만을 채워서 깔끔하게 출력하세요.
                                                    6. 문맥을 파악하여 행동을 행한 주체(예: 아기, 엄마 등)가 누구인지 명확히 인지하고 추출을 진행하세요.


                                                    [카테고리 규칙]
                                                    카테고리들은 반드시 설정해 놓은 단어들 중에서 가장 적합성이 높은 1-2개를 선택하여 출력하라.
                                                    - 부모감정: 뿌듯하다, 지치다, 답답하다, 미안하다, 행복하다, 걱정되다 
                                                    - 아이감정: 기쁘다, 화나다, 슬프다, 무섭다, 심심하다, 짜증나다
                                                    - 육아범주 : 수면, 식사, 사회성, 운동, 언어, 배변, 정서, 인지, 건강, 의복                                            

                                                    [예시 1]
                                                    input : "오전 이유식 한 숟가락 먹고 입을 꾹 닫음. 남은 미음은 양손으로 다 엎어서 본의 아니게 촉감 놀이 파티함. 치우느라 영혼 탈탈 털렸으나 목욕 후 기분 찢어짐. 오후 간식 퓨레는 다행히 순삭하고 응가도 시원하게 성공. 내일은 제발 한 그릇 다 비워주라."
                                                    output : 
                                                    [
                                                        {{
                                                            "원본": "오전 이유식 한 숟가락 먹고 입을 꾹 닫음. 남은 미음은 양손으로 다 엎어서 본의 아니게 촉감놀이 파티함. 치우느라 영혼 탈탈 털렸으나 목욕 후 기분 찢어짐. 오후 간식 퓨레는 다행히 순삭하고 응가도 시원하게 성공. 내일은 제발 한 그릇 다 비워주라.",
                                                            "핵심어": "오전, 이유식, 한 숟가락, 먹고, 입, 닫음, 남은, 미음, 양손, 엎어서, 촉감놀이, 파티, 치우느라, 영혼, 털렸으나, 목욕, 기분 찢어짐, 오후, 간식 퓨레, 순삭, 응가, 성공, 내일, 한 그릇, 비워주라",
                                                            "부모감정": "답답하다, 행복하다",
                                                            "아이감정": "짜증나다, 기쁘다",
                                                            "식사": "2회",
                                                            "배변": "1회",
                                                            "수면": "없음",
                                                            "체온": "없음",
                                                            "육아범주": "식사, 배변"
                                                        }}
                                                    ]

                                                    [예시 2]
                                                    input : "오전 접종 열차 타고 와서 그런지 낮부터 계속 품에만 안겨 있으려고 함. 눕히면 등 센서 발동해서 오후 내내 인간 침대 노릇 함. 다행히 저녁 체온 37.1도로 미열 수준 유지 중. 밤새 열 오르지 않고 무사히 넘어가길 바라며 해열제 대기 완료. 내일은 컨디션 회복하자."
                                                    output : 
                                                    [
                                                        {{
                                                            "원본": "오전 접종 열차 타고 와서 그런지 낮부터 계속 품에만 안겨 있으려고 함. 눕히면 등 센서 발동해서 오후 내내 인간 침대 노릇 함. 다행히 저녁 체온 37.1도로 미열 수준 유지 중. 밤새 열 오르지 않고 무사히 넘어가길 바라며 해열제 대기 완료. 내일은 컨디션 회복하자.",
                                                            "핵심어": "오전, 접종 열차, 타고, 와서, 낮, 품에, 안겨, 눕히면, 등 센서, 발동해서, 오후, 인간 침대 노릇 함, 저녁, 체온 37.1도, 미열, 오르지 않고, 넘어가길, 바라며, 해열제, 대기, 내일, 컨디션, 회복하자",
                                                            "부모감정": "걱정되다, 지치다",
                                                            "아이감정": "무섭다",
                                                            "식사": "없음",
                                                            "배변": "없음",
                                                            "수면": "1회",
                                                            "체온": "37.1도",
                                                            "육아범주": "건강"
                                                        }}
                                                    ]


                                                    [Data]
                                                    {input_data}

                                                    [Output]:""")

        try:
            model = self.get_ai_llm_label_model(config)

            chain = prompt | model | StrOutputParser()
            input_data=input_data.strip()
            keywords = await chain.ainvoke({"input_data": input_data})
            return keywords.strip()
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Watsonx 2단계 라벨 추출 중 예외 발생: {str(e)}")
        

    async def ai_llm_diary_model_run(self, input_data: str, config: dict) -> str:

        prompt = ChatPromptTemplate.from_template("""
                                                  너는 인스타그램에서 오늘 하루의 기록을 다정하고 솔직하게 독백 형태로 공유하는 대한민국 엄마이다.
                                                  관찰자나 제3자가 아닌, 진짜 내 아기를 키우는 엄마의 다정한 시선에서 솔직한 속마음 일기를 작성해라.
                                                  제공된 [Data]의 '원본'을 바탕으로, 명시된 '핵심어', '부모감정', '육아범주' 라벨 정보들을 조합하여 자연스러운 한국어 일기를 작성해라.

                                                  [작성 규칙]
                                                    1. 인스타그램 피드에 어울리는 솔직한 엄마의 독백이므로, 문맥의 흐름과 감정 선에 따라 다정한 존댓말 어미(~요, ~랍니다, ~했네요)와 친근한 반말 독백(~했어, ~알았어)을 자연스럽게 섞어서 부드러운 구어체로 작성하세요.
                                                    2. [Data]의 원본에 담긴 하루 일과를 억지로 나열하지 말고, 마치 친한 이웃에게 오늘 있었던 일을 조곤조마 이야기하듯 자연스러운 일상의 흐름으로 서술하세요.
                                                    3. 대한민국 엄마들이 인스타 피드에서 실제로 쓰는 친근한 공통 육아 단어(예: 맘마, 완밥, 육퇴, 낮잠 등)를 적극적으로 활용하세요. 아기 성별이 명시된 경우에만 아들이나 딸이라는 단어를 쓰세요.
                                                    4. 주어진 '부모감정' 라벨의 분위기가 일기 전체의 정서에 그대로 녹아들게 하세요. 힘들고 지친 상황이라면 속상한 마음을 솔직하게 털어놓고, 다행이거나 기쁜 상황이라면 안도하는 감정을 밀착형 표현으로 다정하게 표현하세요.
                                                    5. 문맥상 주어인 '아기'나 '나(엄마)'는 최대한 자연스럽게 생략하여, 온전히 내 가족의 일상 조각을 들여다보는 듯한 일체감과 가독성을 최우선으로 하세요.
                                                    6. [단위 자석 결합 규칙] 원본 및 식사 항목에 명시된 모든 숫자 뒤에는 원래 적혀 있던 수치의 단위(ml, g, kg, cc, cm, ℃ 등)를 무조건 단 한 칸의 공백도 없이 글자와 자석처럼 단단히 결합하여 완벽하게 출력하세요. (예: 150g이나, 200ml를 등)
                                                    7. 문장마다 자연스럽게 줄바꿈을 하고, 모바일 화면에서 한눈에 가장 예쁘게 읽힐 수 있도록 전체 분량은 호흡이 짧은 3~4줄 내외로 콤팩트하게 작성하세요.
                                                    8. 모든 문장 작성을 완료한 바로 다음 줄에 [AI_LLM_DIARY_END]를 출력하세요.
                                                  
                                                  [예시1]
                                                    원본: 오전 낮잠 20분 만에 깨더니 하루 종일 눈 밑이 힁뎅그렁함. 졸리면서 안 자겠다고 버티느라 오후 내내 징징 모드. 다행히 저녁 분유는 200ml 원샷하고 기절하듯 7시 조기 육퇴함. 소변 기저귀 묵직하고 체온은 36.7도 정상. 내일은 낮잠 좀 푹 자자. 
                                                    핵심어: 오전, 낮잠 20분, 깨더니, 눈밑, 힁뎅그렁함, 졸리면서, 안 자겠다고, 버티느라, 오후, 징징 모드, 저녁, 분유, 200ml, 원샷, 기절, 7시, 조기 육퇴, 소변, 기저귀, 묵직하고, 체온 36.7도, 정상, 내일, 낮잠, 푹 자자
                                                    부모감정: 지치다, 행복하다
                                                    아이감정: 짜증나다
                                                    식사: 1회
                                                    수면: 1회
                                                    배변: 1회
                                                    체온: 36.7도
                                                    육아범주: 건강

                                                    출력 일기:
                                                    아침부터 낮잠을 20분 만에 깨더니 하루 종일 눈 밑이 힁뎅그렁하더라고요.
                                                    졸리면서도 안 자겠다고 버티는데, 오후 내내 징징 모드여서 조금 지치고 속상했어요.
                                                    그래도 다행히 저녁에는 200ml 분유를 원샷하고 기절하듯 7시에 일찍 잠들어주었네요.
                                                    소변 기저귀도 묵직하고 체온은 36.7도로 정상이라 안심했어요. 내일은 낮잠 좀 푹 자 주면 좋겠네요.

                                                    [예시2]
                                                    원본: 오늘 완전 먹고 자는 날인 듯. 아침 분유 먹고 기절하듯 2시간 자고, 깨서 점심 이유식 완밥하더니 오후에 또 유모차에서 1시간 반 꿀잠 잠. 소변 기저귀 엄청 자주 갈아줌. 잘 자고 일어나서 기분 좋은지 혼자 옹알이 폭발함. 체온 36.6도 건강 이상 무! 
                                                    핵심어: 먹고, 자는, 아침, 분유, 기절, 2시간 자고, 깨서, 점심, 이유식 완밥, 오후, 유모차, 1시간 반 꿀잠, 소변 기저귀, 자주, 갈아줌, 자고, 일어나서, 기분 좋은지, 옹알이 폭발, 체온 36.6도, 건강 이상 무
                                                    부모감정: 기쁘다, 행복하다
                                                    아이감정: 기쁘다
                                                    식사: 2회
                                                    수면: 2회
                                                    배변: 1회
                                                    체온: 36.6도
                                                    육아범주: 식사, 수면

                                                    출력 일기:
                                                    완전 먹고 자는 날이네요. 아침 분유를 먹고 기절하듯 2시간을 푹 자고 일어나더라고요.
                                                    깨서 점심 이유식은 기특하게 완밥하더니, 오후에 또 유모차에서 1시간 반이나 꿀잠을 자 주었어요.
                                                    소변 기저귀는 엄청 자주 갈아주며 수시로 챙겨주었답니다. 
                                                    잘 자고 일어나서 기분이 좋은지 혼자 신나서 옹알이가 폭발하는데 그 모습이 어찌나 귀엽고 예쁜지 모르겠어요.
                                                    체온도 36.6도로 정상이라 오늘도 건강 이상 무! 참 기쁘고 감사한 하루였어요.

                                                  [Data]
                                                  {input_data}

                                                  [Diary]:""")
        
        try:
            model = self.get_ai_llm_diary_model(config)
            chain = prompt | model | StrOutputParser()
            
            raw_diary = await chain.ainvoke({"input_data": input_data})
            cleaned_diary = self.clean_raw_text(raw_diary)
            
            return cleaned_diary.strip()    
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Watsonx 3단계 일기 생성 중 예외 발생: {str(e)}")
        
        
    async def ai_llm_story_model_run(self, input_data: str, config: dict) -> str:

        prompt = ChatPromptTemplate.from_template("""
                                                너는 아이의 시점으로 오늘 일상에 대한 일기를 작성할 거야.
                                                제공된 [Data]의 '원본'을 바탕으로 자연스러운 한국어 일기를 작성해라.
                                                부모의 시점의 정보들은 모두 누락하라.
                                                수치 관련 정보는 누락하라.
                                                
                                                [작성 규칙 - 절대 기준]
                                                1. 일기는 전부 아이의 시점으로만 작성합니다. 오직 아기가 직접 손으로 만지고, 눈으로 보고, 느낀 신체 행동과 감정만 기록합니다.
                                                2. 아기 특유의 귀여운 어조를 위해 문장 끝은 무조건 "~했어요!", "~했답니다!", "~했지 뭐예요!"로만 끝맺어라. 아기의 직접적인 행동 종결어만 사용해라.
                                                3. 원본에 등장하는 모든 추측이나 관찰성 표현은 아이가 주체가 되는 확실한 감정 표현과 구체적인 행동으로 완전히 바꾸어라.
                                                4. 아이가 직접 눈으로 본 엄마의 표정과 행동만 단순하게 씁니다. 아이가 느낀 부정적이거나 낯선 감정을 아이가 직접 느낀 그대로 표현해라.
                                                5. 문장은 아기 눈높이에 맞게 아주 짧고 직관적으로 끊어서 작성합니다.
                                                6. 아기의 소리와 행동에 맞추어 실제 의성어와 의태어를 넣어줍니다.
                                                7. 엄마의 말을 전할 때는 큰따옴표를 사용하여 "엄마가 '재미있어?' 했어요"처럼 아기가 기억하기 쉬운 아주 짧고 단순한 대사로만 표현합니다.
                                                8. 2줄 정도의 양으로 작성하라.

                                                [예시1]
                                                원본: 
                                                  아침부터 컨디션이 최고였는지 웃으며 아주 잘 놀 기세였어요. 
                                                  점심 이유식을 한 그릇 싹 다 비우고도 모자라 더 달라고 칭얼거리는 모습이 어찌나 귀엽던지요. 
                                                  낮 시간이 한참 지나도 침대에 누워 잘 생각이 전혀 없어 보였는데, 다행히 3시쯤 유모차를 타자마자 마법처럼 잠들어 1시간 동안 푹 자주었답니다. 
                                                  따끈한 몸을 안아 올리며 체온을 재보니 36.6도로 정상이었어요. 잘 먹고 잘 놀아준 덕분에 오늘도 무사히 하루가 저물어가네요. 
                                                  내일도 오늘처럼 밥 잘 먹고 방글방글 웃으며 행복하게 보내주길 바라요. 
                                                출력 일기: 
                                                  눈뜨자마자 엄마한테 방긋 웃고 점심 맘마도 냠냠 많이 먹었어요!
                                                  낮에는 눈이 초롱초롱했는데 유모차 타니까 쿨쿨 잠이 왔지 뭐예요!
                                                  개운하게 자고 일어나서 완전 튼튼해요, 내일도 또 재미있게 놀고 싶어요!
                                                
                                                [예시2]
                                                원본: 
                                                  낮잠을 겨우 20분 만에 깨버려서 눈 밑이 휑뎅그렁해졌어요. 
                                                  졸리면서도 안 자려고 버티는 통에 오후 내내 징징거림을 받아내느라 애를 먹었네요. 
                                                  그래도 저녁에는 분유 200ml를 단숨에 원샷하고 기절하듯 잠들어주어 고마울 따름이에요. 
                                                  덕분에 저녁 7시, 뜻밖의 이른 육퇴를 선물 받아 정말 좋았답니다. 
                                                  묵직해진 소변 기저귀를 갈아주고 체온을 재보니 36.7도로 정상이었어요. 
                                                  내일은 꼭 낮잠 좀 푹 자주길 바라요. 푹 자줘야 엄마도 숨을 좀 돌리지요. 내일은 우리 둘 다 푹 쉬었으면 좋겠어요!
                                                출력 일기: 
                                                  오늘 낮잠을 눈 깜짝할 사이에 깨버려서 하루 종일 피곤했지 뭐예요!
                                                  졸린데 눈이 자꾸 떠져서 엄마한테 징징 투정 부렸지만 저녁 우유는 꿀맛이었답니다!
                                                  엄마 미안해요, 내일은 푹 자고 재미있게 놀고 싶어요!
                                                
                                                [예시3]
                                                원본: 
                                                  날씨 좋아서 오후에 아빠하고 유모차를 태워서 동네 한 바퀴 돌고 왔어요. 
                                                  밖이 신기한지 두리번거리며 구경 잘 하다가 집에 거의 다와서 잠이 들었네요. 
                                                  다녀와서 시원하게 대변 보고 기분이 좋은지 방긋방긋 웃는게 정말 귀여웠어요. 
                                                  하루 종일 열도 없고 36.4도 완전 건강했어요. 방긋 웃는 얼굴을 보니 마음이 참 든든하고 행복하네요.
                                                출력 일기: 
                                                  오늘 날씨가 반짝반짝해서 아빠랑 유모차 타고 밖으로 슝 나갔답니다!
                                                  초록 나무 구경하다가 스르륵 잠들었고, 집에 와서 응가를 뿡 싸서 기분이 아주 좋아요!
                                                  이마도 안 뜨겁고 쌩쌩해요, 내일도 아빠랑 같이 재미있게 놀고 싶어요!

                                                [Data]
                                                {input_data}
                                                  

                                                [Story]:""")

        try:
            model = self.get_ai_llm_diary_model(config)
            chain = prompt | model | StrOutputParser()
            
            raw_story = await chain.ainvoke({"input_data": input_data})
            
            return raw_story.strip()    
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Watsonx 4단계 디지털북 생성 중 예외 발생: {str(e)}")