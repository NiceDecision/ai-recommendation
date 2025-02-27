# recommendation_model.py
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_openai import ChatOpenAI

# 다른 파일 로드
from data_processor import process_prompt_data          # 데이터 전처리, 후처리
from utils import parse_choice_to_json, show_token_result

# API KEY 자동 로드
load_dotenv()

# DB 설정
DB_CONNECTION = "sqlite:///sqlite_recommend.db"


class RecommendationModel:
    """
    GPT-4o 기반 추천 시스템
    """

    def __init__(self, model_name="gpt-4o-mini", model_provider="openai"):
        """
        모델 및 대화 히스토리 초기화
        """
        # LangChain 모델 초기화
        self.model = init_chat_model(model_name, model_provider=model_provider)
        self.llm = ChatOpenAI(model_name=model_name)

        # 프롬프트 템플릿 설정
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", "{context}"),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{question}")
        ])

        # SQLite 기반 대화 히스토리 저장 설정
        self.db_connection = DB_CONNECTION

    def _get_chat_history(self, session_id: str):
        """
        특정 세션의 대화 히스토리를 가져옴
        """
        chat_history = SQLChatMessageHistory(session_id=session_id, connection_string=self.db_connection)
        return chat_history.messages

    def _get_last_user_message(self, messages):
        """
        사용자 메시지 중 가장 최근 메시지를 추출
        """
        return next(
            (msg.content for msg in reversed(messages) if isinstance(msg, HumanMessage)),
            "안녕하세요, 어떤 추천을 원하시는지 알려주세요."
        )

    def get_recommendation(self, clean_data: dict, session_id: str = "default_session"):
        """
        정제된 데이터를 기반으로 GPT 프롬프트를 생성하고 실행
        """
        # 1. 대화 히스토리 로드
        past_messages = self._get_chat_history(session_id)
        input_messages = [HumanMessage(clean_data["question"])]
        all_messages = past_messages + input_messages

        # 2. 최근 질문 추출
        last_human_message = self._get_last_user_message(all_messages)

        # 3. 프롬프트 생성
        context = process_prompt_data(clean_data)

        # 4. 프롬프트 템플릿 적용
        prompt = self.prompt_template.invoke({
            "context": context,
            "history": all_messages,
            "question": last_human_message
        })

        # 5. GPT 실행
        response = self.model.invoke(prompt)

        # 6. 대화 히스토리 저장
        chat_history = SQLChatMessageHistory(session_id=session_id, connection_string=self.db_connection)
        chat_history.add_user_message(last_human_message)
        chat_history.add_ai_message(response.content)

        # 7. 토큰 사용량 분석
        show_token_result(str(prompt), response.content)

        return response.content


''' 별개로 5개의 질문을 생성하는 함수 '''
def generate_comparison_questions():
    # GPT 모델 초기화
    model = init_chat_model("gpt-4o-mini", model_provider="openai")

    # 시스템 프롬프트 템플릿 작성
    system_template = (
        "다음 형식에 맞춰 5개의 랜덤 비교 질문을 생성해 주세요:\n"
        "'testX: 항목 A vs 항목 B'\n"
        "항목은 단어 또는 문장이 될 수 있습니다.\n"
        "각 테스트 케이스는 줄 바꿈으로 구분해주세요.\n"
        "예제:\n"
        "test1: 강아지 vs 고양이\n"
        "test2: 커피 vs 차\n"
        "답변은 테스트 케이스만 포함하고, 다른 설명은 절대 추가하지 마세요."
    )

    # ChatPromptTemplate 생성 (system 메시지만 사용)
    prompt_template = ChatPromptTemplate.from_messages([("system", system_template)])

    # 프롬프트 생성
    prompt_value = prompt_template.invoke({})
    prompt_text = prompt_value.messages[-1].content  # 마지막 메시지의 content만 추출

    # GPT 호출 (응답 길이를 제한)
    response = model.invoke([HumanMessage(prompt_text)], max_tokens=200)

    clean_json = parse_choice_to_json(response.content.strip())

    # 응답에서 content만 반환
    return clean_json