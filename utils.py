# utils.py
''' role + message로 대화 기록을 리턴하는 함수 '''
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage

def get_chat_history_with_roles(session_id: str, db_connection: str):
    """
    특정 session_id의 대화 기록을 role과 message로 변환하여 반환.

    Args:
        session_id (str): 조회할 세션 ID
        db_connection (str): SQLite 연결 문자열

    Returns:
        list: [{"role": "user", "message": "안녕하세요!"}, {"role": "ai", "message": "안녕하세요! 무엇을 도와드릴까요?"}]
    """
    chat_history = SQLChatMessageHistory(session_id=session_id, connection_string=db_connection)
    messages = chat_history.messages  # LangChain의 메시지 객체 리스트

    formatted_messages = []
    for msg in messages:
        if isinstance(msg, HumanMessage):
            formatted_messages.append({"role": "user", "message": msg.content})
        elif isinstance(msg, AIMessage):
            formatted_messages.append({"role": "ai", "message": msg.content})

    return formatted_messages


''' 추천 결과를 JSON으로 가공하는 함수 '''
def get_formatted_recommendation_response(ai_response: str, session_id: str):
    """ 임시 코드 """
    return {
        "session_id": session_id,
        "response": ai_response.strip()  # 불필요한 공백 제거
    }


''' 토큰 사용량 분석 함수 '''
import tiktoken

def get_token_count(text: str, model_name: str = "gpt-4o-mini") -> int:
    """
    텍스트의 토큰 개수를 반환하는 함수.
    """
    try:
        encoding = tiktoken.encoding_for_model(model_name)
    except Exception:
        encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))


def show_token_result(prompt: str, response_text: str, model_name: str = "gpt-4o-mini"):
    """
    프롬프트와 응답의 토큰 사용량을 분석하여 출력.
    """
    input_token_count = get_token_count(prompt, model_name)
    output_token_count = get_token_count(response_text, model_name)

    input_rate = 0.150 / 1_000_000  # $ per token for input tokens
    output_rate = 0.600 / 1_000_000  # $ per token for output tokens

    iteration_cost = (input_token_count * input_rate) + (output_token_count * output_rate)
    estimated_cost_100 = iteration_cost * 100

    print(f"[DEBUG] Input token count: {input_token_count}")
    print(f"[DEBUG] Output token count: {output_token_count}")
    print(f"[DEBUG] Cost for this iteration: ${iteration_cost:.8f}")
    print(f"[DEBUG] Estimated cost for 100 iterations: ${estimated_cost_100:.8f}")


''' 선택 문제 생성 파싱 '''
import re

def parse_choice_to_json(response_text):
    # 정규식으로 "testX: 항목A vs 항목B" 패턴 찾기
    pattern = r"test(\d+):\s*(.+?)\s*vs\s*(.+)"
    matches = re.findall(pattern, response_text)

    # JSON 변환
    json_data = {f"test{num}": f"{itemA.strip()} vs {itemB.strip()}" for num, itemA, itemB in matches}
    return json_data