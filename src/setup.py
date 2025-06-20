from setuptools import setup, find_packages

setup(
    name='rag',
    version='0.1.1',
    packages=find_packages(where='src'),
    package_dir={'rag': 'src'},
    install_requires=[
        'streamlit',
        'pandas',
        'numpy>=1.21',
        'groq',
        'python-dotenv',
        'sentence-transformers',
        'sqlalchemy',
        'bm25s',
        'unidecode',
        'spacy',
        'psycopg2-binary',
    ],
)