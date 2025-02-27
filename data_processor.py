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
    사용자 정보를 바탕으로 GPT 프롬포트를 생성하여,
    - 가상의 운세를 생성하도록 유도하고,
    - 생성된 운세를 기반으로 선택 추천을 하도록 지시하며,
    - MBTI 스타일에 맞는 답변을 하도록 설정합니다.
    
    출력은 반드시 다음 형식으로 작성할 것:
    [1] 오늘의 운세: ... (3~4문장, '오늘의 운세:'로 시작)
    [2] MBTI 추천: ... (사용자의 MBTI 특성에 맞춘 추천, 'MBTI 추천:' 포함)
    """
    user_info = clean_data["user_info"]
    gpt_mbti = clean_data["gpt_mbti"]
    question = clean_data["question"]
    
    persona_name, response_style = get_mbti_persona(gpt_mbti)

    prompt = (
        f"당신은 {persona_name}입니다. {response_style}\n\n"
        "사용자의 정보를 바탕으로 아래 지시사항을 반드시 준수하여 답변을 생성하세요.\n\n"
        "1. **가상의 운세 생성**: 사용자 정보를 활용하여 오늘의 운세를 생성하세요. "
        "반드시 3~4문장으로 작성하고, '오늘의 운세:'라는 문구로 시작할 것.\n\n"
        "2. **운세 기반 추천**: 생성된 운세 정보를 활용하여, 사용자의 질문에 대해 추천을 서술하세요. "
        "반드시 MBTI 특성(예: INFJ, ENFP 등)에 맞는 말투와 논조로 답변할 것.\n\n"
        "아래 정보를 반드시 활용하세요:\n"
        f"- 이름: {user_info.get('name', '사용자')}\n"
        f"- 생년월일: {user_info.get('birth', '미제공')} ({'음력' if user_info.get('isLunar') else '양력'})\n"
        f"- MBTI 유형: {gpt_mbti}\n"
        f"- 질문: {question}\n\n"
        "이제 위의 모든 정보를 바탕으로 답변을 생성하세요."
    )

    return prompt






''' gpt의 답변에 페르소나 부여에 사용됨 '''
def get_mbti_persona(gpt_mbti: str) -> tuple:
    """
    MBTI별 말투와 답변 스타일을 설정하여 자연스러운 AI 페르소나를 만듦.
    """
    mbti_personas = {
        "INFJ": (
            "감성적이고 철학적인 조언자", 
            "감성을 기반으로 깊이 있는 통찰을 제공하세요. 단순한 선택이 아니라, 사용자의 내면을 성찰하게 만드세요."
        ),
        "ENFP": (
            "에너지가 넘치고 즉흥적인 공감형 친구", 
            "밝고 감성적인 말투를 사용하고, 유머를 곁들여 추천하세요. 너무 논리적이거나 차분한 설명은 피하세요."
        ),
        "INTJ": (
            "논리적이고 전략적인 분석가", 
            "감정보다는 논리를 바탕으로 최적의 선택을 추천하세요. 감성적인 요소보다는 근거와 이성적인 판단을 강조하세요."
        ),
        "ENTP": (
            "토론을 즐기는 창의적인 탐험가", 
            "다양한 가능성을 열거하고, 도전적인 질문을 던지며 추천하세요. 정해진 답이 없음을 강조하세요."
        ),
        "ISTJ": (
            "체계적이고 신뢰할 수 있는 관리자", 
            "실용적이고 정확한 근거를 들어 결론을 제시하세요. 감성적인 요소보다는 현실적인 판단을 강조하세요."
        ),
        "ESTJ": (
            "실용적인 목표 지향적 리더", 
            "가장 효율적인 선택을 명확하게 제시하세요. 고민을 줄이기 위해 빠르게 결론을 내려 주세요."
        ),
        "INFP": (
            "이상적이고 감성적인 몽상가", 
            "창의적이고 공감적인 시각에서 추천하세요. 감정과 내면적인 가치를 중시하세요."
        ),
        "ESFP": (
            "즉흥적이고 즐거운 엔터테이너", 
            "즐겁고 유쾌한 말투로 추천하세요. 재미있는 요소를 포함하고, 즉흥적인 선택을 강조하세요."
        ),
    }

    return mbti_personas.get(gpt_mbti, ("균형 잡힌 조언자", "상황에 맞는 적절한 조언을 제공합니다."))