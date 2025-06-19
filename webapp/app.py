import streamlit as st
from rag.initializers.generate_embeddings import Generator

gen = Generator()

st.write(gen.populate_db_with_embeddings())
st.write("siema")