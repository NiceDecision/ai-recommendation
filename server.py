# server.py
from fastapi import FastAPI, Body, Path
from fastapi.middleware.cors import CORSMiddleware
from recommendation_model import RecommendationModel
from fastapi.responses import JSONResponse

# 다른 파일 로드
from data_processor import preprocess_input_data    # 데이터 전처리 함수
from utils import get_chat_history_with_roles, get_formatted_recommendation_response

app = FastAPI()

# CORS 설정 (필요한 도메인만 지정 가능)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 단계에서는 모든 도메인 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 모델 인스턴스 생성
gpt_model = RecommendationModel(model_name="gpt-4o-mini")

@app.post("/ai/fortune")
def get_fortune(data: dict = Body(..., example={
    "question": "내일 데이트 가는데 어떤 옷을 입어야 할까요?",
    "user_info": {"birth": "1990-01-01", "gender": "여성"},
    "gpt_mbti": {"MBTI": "INFJ"},
    "fortune": {"lucky": "대인 관계 운 상승, 재물운 평범, 정서적 안정감과 창의력이 돋보이는 하루"}
    # , "vs_data": {"커피_vs_차": "커피", "산_vs_바다": "바다", "원피스_vs_블라우스_스커트": "원피스"}
})):
    # 최초 데이터 정제해서
    clean_data = preprocess_input_data(data)
    # 모델에 프롬프트 전달하고 응답 받고
    ai_response = gpt_model.get_recommendation(clean_data, session_id="default_session")
    # 반환 데이터를 한번 더 정제해서 전달 (fe, be와 의논 필요)
    final_response = get_formatted_recommendation_response(ai_response, session_id="default_session")
    return JSONResponse(content=final_response)


@app.get("/ai/chat-history/{session_id}")
def get_chat_history(session_id: str = Path(..., 
    title="Session ID", description="조회할 대화 세션 ID", example="default_session"
)):
    """
    특정 session_id의 대화 기록을 role과 함께 JSON 형태로 반환하는 API 엔드포인트
    """
    DB_CONNECTION = "sqlite:///sqlite_recommend.db"
    chat_history = get_chat_history_with_roles(session_id, DB_CONNECTION)
    
    return JSONResponse(content={"session_id": session_id, "messages": chat_history})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)