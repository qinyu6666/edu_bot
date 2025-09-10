import os, glob, pickle
from langchain.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import faiss, numpy as np
from langchain.schema import Document

# 加载问题文档和故事文档
# loader_questions = DirectoryLoader("data/questions", glob="**/*.txt", loader_cls=TextLoader, show_progress=True)
# loader_stories = DirectoryLoader("data/stories", glob="**/*.txt", loader_cls=TextLoader, show_progress=True)
loader_questions = DirectoryLoader("data/questions", glob="**/*.txt", show_progress=True)
loader_stories = DirectoryLoader("data/stories", glob="**/*.txt", show_progress=True)
docs_questions = loader_questions.load()
docs_stories = loader_stories.load()
docs = docs_questions + docs_stories

text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=300, chunk_overlap=50, separators=["\n\n", "\n", "。", "，", " "])
chunks = text_splitter.split_documents(docs)

model = SentenceTransformer("BAAI/bge-small-zh")
vectors = model.encode([c.page_content for c in chunks], normalize_embeddings=True)

index = faiss.IndexFlatIP(vectors.shape[1])
index.add(vectors.astype('float32'))

os.makedirs("vector_db", exist_ok=True)
faiss.write_index(index, "vector_db/faiss.index")
with open(r"vector_db/chunks.pkl", "wb") as f:
    pickle.dump(chunks, f)
print("✅ 知识库已建立，共", len(chunks), "段")
