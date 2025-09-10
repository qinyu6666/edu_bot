import numpy as np
from sentence_transformers import SentenceTransformer,util
import numpy as np
import re
model = SentenceTransformer("BAAI/bge-small-zh")


def normalize_number(text: str) -> float:
    """把中文数字或阿拉伯数字统一转成 float；转不了就抛异常"""
    chinese_map = {
        '零': 0, '一': 1, '二': 2, '三': 3, '四': 4,
        '五': 5, '六': 6, '七': 7, '八': 8, '九': 9,
        '十': 10, '百': 100, '千': 1000, '万': 10000
    }
    text = text.strip()
    if re.fullmatch(r'[+-]?\d+(\.\d+)?', text):
        return float(text)
    # 简单处理“十以内”中文数字
    if text in chinese_map:
        return float(chinese_map[text])
    raise ValueError("不是可比较的数字")


def get_similarity(text1, text2):
    text1, text2 = str(text1).strip(), str(text2).strip()
    if text1 == text2:
        return 1.0
    try:
        user_num = normalize_number(text1)
        std_num = normalize_number(text2)
        return 1.0 if abs(user_num - std_num) <= 1e-6 else 0.0
    except ValueError:
        pass

    user_emb = model.encode(text1, normalize_embeddings=True, convert_to_tensor=True)
    std_emb = model.encode(text2, normalize_embeddings=True, convert_to_tensor=True)
    cos = util.cos_sim(user_emb, std_emb).item()
    return cos ** 2

text1 = "东北方向"
text2 = "西方"
similarity = get_similarity(text1, text2)
print(f"文本1: {text1}")
print(f"文本2: {text2}")
print(f"相似度: {similarity:.4f}")

w1 = "北京"
w2 = "北京市"
similarity = get_similarity(w1, w2)
print(f"文本1: {w1}")
print(f"文本2: {w2}")
print(f"相似度: {similarity:.4f}")