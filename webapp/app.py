import streamlit as st
from rag.semantic_search import SemanticSearchEngine
from rag.chatbot import get_answer, create_prompt

st.title("Zapytaj o program studiów!")

semantic_search_engine = SemanticSearchEngine()

query = st.text_input("")

if st.button("Pytaj") and query:
    with st.spinner("Pracuję..."):
        results = semantic_search_engine.search(query)
        prompt = create_prompt(query, results)
        answer = get_answer(prompt)
        st.write(f"Odpowiedź z systemu:\n\n{answer}")
