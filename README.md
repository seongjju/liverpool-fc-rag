# Liverpool FC RAG 시스템 코드



## 접속 URL
http://localhost:8501

## 주요 기능

### 1. RAG 시스템 초기화
- 위키피디아에서 리버풀 FC 관련 문서 자동 로드
- OpenAI text-embedding-3-small로 벡터화
- ChromaDB에 저장 및 인덱싱

### 2. 지능형 검색
- MMR 알고리즘으로 관련성과 다양성 균형
- 상위 5개 문서 선별하여 컨텍스트 구성

### 3. AI 답변 생성
- GPT-4o-mini를 통한 자연어 답변
- 검색된 문서 기반으로 정확한 정보 제공

### 4. 사용자 인터페이스
- Streamlit 기반 직관적 웹 UI
- 실시간 상태 표시 및 오류 처리
- 캐싱을 통한 성능 최적화
