import streamlit as st
from rag.chatbot import create_prompt, get_answer
from rag.semantic_search import SemanticSearchEngine

st.title("Zapytaj o program studiów!")


@st.cache_resource
def get_search_engine() -> SemanticSearchEngine:
    return SemanticSearchEngine()


semantic_search_engine = get_search_engine()

query = st.text_input("")

if st.button("Pytaj") and query:
    with st.spinner("Pracuję..."):
        results = semantic_search_engine.search(query)
        prompt = create_prompt(query, results)
        answer = get_answer(prompt)
        st.write(f"Odpowiedź z systemu:\n\n{answer}")
