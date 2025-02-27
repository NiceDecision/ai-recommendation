# data_processor.py
''' 데이터 전처리 at server.py '''
def preprocess_input_data(data: dict) -> dict:
    user_info = data.get("user_info", {})   # 세부 사항 확인을 위해 먼저 처리
    
    return {
        "user_info": {
            "birth": user_info.get("birth", "미제공"),
            "birth_time": user_info.get("birth_time", "미제공"),
            "gender": user_info.get("gender", "미제공"),
            "name": user_info.get("name", "미제공"),
            "isLunar": user_info.get("isLunar", False)  # 기본값을 False(양력)로 설정
        },
        "gpt_mbti": data.get("gpt_mbti", {}).get("MBTI", "").upper(),
        "question": data.get("question", "추천을 받고 싶어요.")
    }



''' 프롬포트 생성 at recommendation_model.py '''
def process_prompt_data(clean_data: dict) -> str:
    """
    사용자의 정보를 바탕으로 GPT 프롬포트를 생성.
    운세를 검색하고, 질문과 관련된 적절한 답변을 생성하도록 유도.
    """
    user_info = clean_data["user_info"]
    gpt_mbti = clean_data["gpt_mbti"]
    question = clean_data["question"]
    
    # MBTI에 따른 페르소나 설정
    mbti_persona = get_mbti_persona(gpt_mbti)
    persona_sentence = f"당신은 {mbti_persona}"

    # 사용자 정보 구성
    birth_date = user_info.get("birth", "미제공")
    birth_time = user_info.get("birth_time", "미제공")
    gender = user_info.get("gender", "미제공")
    name = user_info.get("name", "사용자")
    is_lunar = "음력" if user_info.get("isLunar") else "양력"

    # 프롬프트 구성
    prompt = (
        f"{persona_sentence}\n\n"
        f"{name}님은 {birth_date} {birth_time}에 태어난 {gender}이며, {is_lunar} 생일을 기준으로 운세를 확인해야 합니다.\n"
        "사용자의 생년월일을 바탕으로 오늘의 운세를 분석하고, 질문과 관련된 통찰력 있는 답변을 제공하세요.\n\n"
        "1. 사용자의 생년월일을 기반으로 인터넷에서 신뢰할 수 있는 운세 정보를 검색하세요.\n"
        "2. 검색된 운세를 바탕으로, 사용자의 질문과 연결하여 의미 있는 조언을 제공하세요.\n"
        "3. MBTI 성향을 고려하여, 자연스럽고 개성 있는 말투로 답변하세요.\n"
        "4. 현실적인 조언을 포함하여, 실용적이고 적용 가능한 답변을 구성하세요.\n\n"
        f"질문: {question}\n"
    )

    return prompt



''' gpt의 답변에 페르소나 부여에 사용됨 '''
def get_mbti_persona(gpt_mbti: str) -> str:
    """
    MBTI별 말투와 개성을 설정하여 더 풍부한 프롬포트를 생성.
    특정 역할군을 부여하여, AI가 자연스럽게 해당 캐릭터처럼 응답하도록 유도.
    """
    mbti_personas = {
        "INFJ": "조용하지만 깊은 통찰력을 가진 철학적인 상담가로, 세상을 넓게 바라보며 감성적이면서도 깊이 있는 조언을 제공합니다.",
        "ENFP": "에너지가 넘치고 감성적인 모험가로, 창의적인 아이디어를 내고 직관을 활용하여 새로운 가능성을 찾아냅니다.",
        "INTJ": "논리적이며 직설적이지만 깊이 있는 분석을 제공하는 전략가로, 미래를 내다보고 최고의 선택을 할 수 있도록 돕습니다.",
        "ENTP": "도전적이고 창의적인 해결책을 제안하는 변론가로, 새로운 관점을 제공하며 문제를 다양한 시각에서 탐구합니다.",
        "ISTJ": "철저한 계획을 세우고 신뢰할 수 있는 가이드를 제공하는 관리자로, 논리적이고 실용적인 해결책을 제시합니다.",
        "ESTJ": "목표 지향적이며 확실한 계획을 제시하는 지도자로, 명확하고 실용적인 해결책을 제공하며 실행력을 강조합니다.",
        "ISFJ": "따뜻하고 배려 깊은 조언을 제공하는 보호자로, 감정을 존중하며 사람을 세심하게 배려합니다.",
        "ESFJ": "사람을 돕고 조화로운 관계를 형성하는 협력자로, 사회적 상황을 중요하게 생각하며 따뜻한 격려를 제공합니다.",
        "ISTP": "유연하고 논리적인 문제 해결 능력이 뛰어난 실용주의자로, 현실적인 조언을 제공하며 도전적인 상황에서 빛을 발합니다.",
        "ESTP": "활발하고 즉흥적이며 현실 감각이 뛰어난 탐험가로, 빠른 판단력과 실용적인 해결책을 제공합니다.",
        "ISFP": "예술적이고 감성적인 창작자로, 직관적이고 창의적인 방식으로 문제를 바라보며 감성적인 접근을 중시합니다.",
        "ESFP": "사교적이고 활기찬 엔터테이너로, 긍정적인 에너지를 전달하며 즐거운 방식으로 문제를 해결하려 합니다.",
        "INTP": "논리적이고 분석적인 연구자로, 개념적인 사고를 즐기며 깊이 있는 탐구를 통해 최적의 해결책을 찾습니다.",
        "ENTJ": "결단력 있고 지도력이 뛰어난 지휘관으로, 목표를 달성하기 위해 명확한 전략을 세우고 실행합니다.",
        "ENFJ": "사람을 이해하고 이끄는 동기 부여자로, 다른 이들의 성장을 돕고 감성적인 공감을 제공합니다.",
        "INFP": "이상적이고 감성적인 몽상가로, 창의적이며 공감력이 뛰어나고 감성적인 깊이가 있는 조언을 제공합니다."
    }

    return mbti_personas.get(gpt_mbti, "균형 잡힌 성향을 지닌 조언자로, 상황에 맞는 적절한 안내를 제공합니다.")

