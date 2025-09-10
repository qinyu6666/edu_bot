import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("BAAI/bge-small-zh")

def calculate_similarity(text1, text2):
    emb1 = model.encode([text1], normalize_embeddings=True)[0]
    emb2 = model.encode([text2], normalize_embeddings=True)[0]
    return np.dot(emb1, emb2)

def format_story(story):
    return f"《{story['title']}》\n\n{story['content']}\n\n故事讲完啦！你觉得有趣吗？"
