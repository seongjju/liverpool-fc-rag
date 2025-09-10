#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import streamlit as st
from dotenv import load_dotenv
import wikipedia
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.document_loaders import WikipediaLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain import hub
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# 환경 설정
load_dotenv()

# Streamlit 페이지 설정
st.set_page_config(
    page_title="리버풀 FC RAG 검색",
    page_icon="⚽",
    layout="wide"
)

@st.cache_resource
def initialize_rag_system():
    """RAG 시스템 초기화 (캐시 적용)"""
    try:
        # 1. LLM 설정
        model_name = os.getenv("CHAT_MODEL", "gpt-4o-mini")
        llm = ChatOpenAI(model=model_name, temperature=0)
        # 2. 임베딩 모델 설정
        model_name = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
        embeddings = OpenAIEmbeddings(model=model_name)

        # 3. 위키피디아에서 리버풀 FC 관련 문서 로드
        topics = [
            "Liverpool F.C.",
            "Liverpool F.C. players",
            "Liverpool F.C. history", 
        ]
        
        all_documents = []
        for topic in topics:
            try:
                loader = WikipediaLoader(
                    query=topic, 
                    lang="en",
                    load_max_docs=2,
                    doc_content_chars_max=3000
                )
                documents = loader.load()
                all_documents.extend(documents)
            except Exception as e:
                st.warning(f"'{topic}' 로드 중 오류: {str(e)}")
                continue
        
        if not all_documents:
            st.error("위키피디아 문서를 로드할 수 없습니다.")
            return None
            
        # 4. 텍스트 분할
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        split_documents = text_splitter.split_documents(all_documents)
        
        # 5. 벡터 데이터베이스 구축
        db = Chroma.from_documents(
            documents=split_documents, 
            embedding=embeddings,
            persist_directory="./chroma_db"
        )
        
        # 6. 검색기 설정
        retriever = db.as_retriever(
            search_type="mmr",
            search_kwargs={"k": 5, "fetch_k": 20, "lambda_mult": 0.5}
        )
        
        # 7. 프롬프트 템플릿
        prompt_template = hub.pull("langchain-ai/retrieval-qa-chat")
        
        # 8. 출력 파서
        parser = StrOutputParser()
        
        # 9. RAG 체인 구성
        rag_chain = {
            "context": retriever,
            "input": RunnablePassthrough()
        } | prompt_template | llm | parser
        
        return rag_chain, len(split_documents)
        
    except Exception as e:
        st.error(f"RAG 시스템 초기화 오류: {str(e)}")
        return None

def main():
    st.title("⚽ 리버풀 FC RAG 검색 시스템")
    st.markdown("---")
    
    # 사이드바
    with st.sidebar:
        st.header("📋 시스템 정보")
        st.info("위키피디아의 리버풀 FC 관련 정보를 기반으로 질문에 답변합니다.")
    
    # 메인 영역
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🔍 질문 입력")
        
        # 세션 상태에서 질문 가져오기
        default_question = st.session_state.get('user_question', '')
        user_input = st.text_area(
            "리버풀 FC에 대해 궁금한 것을 물어보세요:",
            value=default_question,
            height=100,
            placeholder="예: 리버풀 FC의 역사에 대해 알려주세요"
        )
        
        # 질문 초기화
        if st.button("질문 지우기"):
            st.session_state.user_question = ""
            st.rerun()
    
    with col2:
        st.subheader("⚙️ 시스템 상태")
        
        # RAG 시스템 초기화
        with st.spinner("RAG 시스템 초기화 중..."):
            rag_result = initialize_rag_system()
            
        if rag_result:
            rag_chain, doc_count = rag_result
            st.success("시스템 준비 완료")
            st.metric("로드된 문서 수", doc_count)
        else:
            st.error("시스템 초기화 실패")
            return
    
    # 질문 처리
    if user_input.strip():
        st.markdown("---")
        st.subheader("💬 답변")
        
        try:
            with st.spinner("답변 생성 중..."):
                # RAG 체인 실행
                response = rag_chain.invoke(user_input)
                
            # 답변 표시
            st.write(response)

                
        except Exception as e:
            st.error(f"답변 생성 중 오류가 발생했습니다: {str(e)}")
    

if __name__ == "__main__":
    main()