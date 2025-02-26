# ai-recommendation
LLM recommendation tuned by fortune, taste, .etc


### test
- python server.py 로 동작 (혹은 uvicorn server:app ~~~ 으로 가능)
    - https://~~/docs 를 통해 테스트 가능 (Swagger로 이동)
    - 테스트는 샘플 데이터 있으니 편하게 가능!

### .env
- OPENAI_API_KEY 필요함

### .gitignore
- Github Codespace 기준으로 작성됨
- 필요 시, 커스텀해서 사용해야 함


### 폴더 구조
```
project_root/
│── main.py  # FastAPI 또는 RecommendationModel 실행 파일
│── recommendation_model.py  # RecommendationModel 클래스
│── chat_history.py  # ✅ CustomSQLChatMessageHistory 추가할 파일
│── data_processor.py  # 데이터 전처리 관련 함수들
│── utils.py  # 기타 유틸리티 함수 (토큰 계산 등)
│── requirements.txt
│── sqlite_recommend.db  # SQLite DB 파일
```