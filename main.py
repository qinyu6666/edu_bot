import os, json, random, time
import re
import threading
import dashscope
from dashscope import Generation
from src.rag import RAG
from src.memory_mysql import Memory
from sentence_transformers import SentenceTransformer,util
import numpy as np
import subprocess
dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")
import sys
# 初始化
rag = RAG()
memory = Memory()
memory.initialize_database()
model = SentenceTransformer("BAAI/bge-small-zh")

# 假设当前孩子ID为1（实际应用中可能需要登录或选择孩子）
CHILD_ID = 1


# def get_similarity(text1, text2):
#     """计算两段文本的余弦相似度"""
#     embeddings = model.encode([text1, text2], normalize_embeddings=True)
#     return np.dot(embeddings[0], embeddings[1])
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
    text1, text2 = str(text1), str(text2)
    if text1 == text2:
        return 1.0
    try:
        user_num = normalize_number(text1)
        std_num = normalize_number(text2)
        return 1.0 if abs(user_num - std_num)<= 1e-6 else 0.0
    except ValueError:
        pass

    user_emb = model.encode(text1, normalize_embeddings=True, convert_to_tensor= True)
    std_emb = model.encode(text2, normalize_embeddings=True, convert_to_tensor=True)
    cos_result = util.cos_sim(user_emb, std_emb).item()
    return cos_result ** 2


    # return np.dot(embeddings[0], embeddings[1])

def call_qwen(prompt):
    """调用千问大模型生成回答"""
    response = Generation.call(
        model='qwen-turbo',
        prompt=prompt,
        seed=1234,
        top_p=0.8
    )
    if response.status_code == 200:
        return response.output.text
    else:
        return "抱歉，我暂时回答不了这个问题。"


# def wait_for_input(timeout=4):
#     """等待用户输入，超时返回空字符串"""
#     start_time = time.time()
#     user_input = ""
#     while time.time() - start_time < timeout:
#         # 这里模拟输入，实际应用可能是从网络或控制台获取
#         # 为了演示，我们使用input，但设置超时需要使用多线程或异步，这里简化处理
#         # 注意：在真实环境中，可能需要使用非阻塞输入，这里为了简单，使用超时循环模拟
#         # 我们假设在等待期间，用户可能输入，这里用time.sleep模拟等待
#         time.sleep(0.1)
#         # 假设我们有一个函数可以非阻塞获取输入，但这里简化，我们随机模拟用户输入
#         # 实际开发中，这个函数需要根据具体的输入方式重写
#         # 这里我们模拟：在4秒内，有50%的几率在随机时间点收到输入
#         if random.random() < 0.5:  # 模拟50%几率有输入
#             user_input = "模拟的用户输入"  # 实际应该从输入设备获取
#             break
#     # 为了演示，我们直接返回空字符串模拟超时
#     # 实际应用中，这里应该返回真实输入
#     return user_input

###################################################################################
###################################################################################


# def wait_for_input(timeout=4, prompt="请输入: "):
#     """等待用户输入，超时返回空字符串（使用多线程实现）"""
#     print(prompt, end='', flush=True)  # 打印提示但不换行
#
#     user_input = [None]  # 使用列表来存储结果
#
#     input_done = threading.Event()
#
#     def get_input():
#         try:
#             # 获取用户输入
#             user_input[0] = input()
#         except EOFError:
#             user_input[0] = ""  # 处理Ctrl+D的情况
#         except KeyboardInterrupt:
#             user_input[0] = ""  # 处理Ctrl+C的情况
#         finally:
#             input_done.set()  # 标记输入已完成
#
#     # 创建一个线程来获取输入
#     input_thread = threading.Thread(target=get_input)
#     # input_thread.daemon = True  # 设置为守护线程
#     input_thread.start()
#     input_thread.join(4)
#
#     # 等待超时时间，显示倒计时
#     # start_time = time.time()
#     # while time.time() - start_time < timeout:
#     #     if not input_thread.is_alive():
#     #         break
#     #     time.sleep(0.1)
#
#
#     # 等待超时时间，或者输入完成
#     input_done.wait(timeout)
#
#     # 如果线程还在运行，说明超时了
#     if input_thread.is_alive():
#         print("\n时间到！")
#         return ""
#
#     # input_thread.join()
#
#     return user_input[0] if user_input[0] is not None else ""
################################################################################
#################################################################################
def wait_for_input(timeout=4, prompt="请输入: "):
    """
    用子进程读一行输入，超时直接杀进程。
    在 Windows 上也不会卡死。
    """
    print(prompt, end='', flush=True)

    # 启动一个极简 Python 子进程，只做 input()
    cmd = [sys.executable, "-c",
           "import sys; sys.stdout.write(sys.stdin.readline())"]
    try:
        proc = subprocess.Popen(
            cmd,
            stdin=sys.stdin,  # 共享控制台
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8'
        )
    except Exception:
        return ""

    try:
        out, _ = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.communicate()
        print("\n时间到！")
        return ""
    else:
        return out.rstrip('\n')

    # 调用函数





def get_active_question():
    """获取一个主动提问的问题（优先选择记忆不好的）"""
    questions = memory.get_poorly_remembered_questions(CHILD_ID, limit=10)
    if questions:
        return random.choice(questions)
    else:
        # 如果没有记忆记录，随机选一个问题
        all_questions = memory.get_questions_by_category()
        if all_questions:
            return random.choice(all_questions)
        else:
            return None


def get_active_story():
    """随机获取一个故事"""
    stories = memory.get_stories_by_category()
    if stories:
        return random.choice(stories)
    else:
        return None


def main_loop():
    print("智能体已启动，等待孩子提问（等待4秒）...")
    user_input = wait_for_input(4)  # 等待4秒

    if user_input:  # 孩子提出了问题
        # 检索知识库
        context = rag.search(user_input, k=3)
        if context:
            # 将检索到的知识作为上下文
            prompt = f"根据以下信息：\n{context}\n\n请回答：{user_input}"
        else:
            prompt = user_input

        # 调用大模型
        bot_response = call_qwen(prompt)
        print("智能体:", bot_response)
        # 记录对话，此时没有提问问题，所以question_id为空，也没有故事，is_correct=-1
        memory.record_interaction(CHILD_ID, None, None, user_input, bot_response, -1)

    else:  # 主动交互
        # 随机选择是提问还是讲故事
        # choice = random.choice(['question', 'story'])
        options = ['question', 'story']
        weights = [0.9, 0.1]
        choice = random.choices(options, weights=weights, k=1)[0]
        # choice = random.choice(['question', 'story'], weights=[0.8, 0.2], k=1)[0]

        if choice == 'question':
            question = get_active_question()
            if question:
                print(f"智能体（主动提问）: {question['question_text']}")
                # 记录对话，记录这个问题ID，用户输入为空，等待回答
                memory.record_interaction(CHILD_ID, question['question_id'], None, None, question['question_text'], -1)

                # 等待孩子回答
                user_answer = wait_for_input(7)
                if user_answer:
                    # 计算相似度
                    similarity = get_similarity(user_answer, question['standard_answer'])
                    if similarity > 0.85:  # 阈值可调
                        print("智能体: 太棒了！你答对了！")
                        memory.update_question_memory(CHILD_ID, question['question_id'], True, next_ask_probability=0.5)
                        memory.record_interaction(CHILD_ID, question['question_id'], None, user_answer, "太棒了！你答对了！", 1)
                    else:
                        print(f"智能体: 正确答案是：{question['standard_answer']}，继续加油哦！")
                        memory.update_question_memory(CHILD_ID, question['question_id'], False, next_ask_probability=0.5)
                        memory.record_interaction(CHILD_ID, question['question_id'], None, user_answer,
                                                f"正确答案是：{question['standard_answer']}，继续加油哦！", 0)
                else:
                    print("智能体: 我再给你讲个故事好不好？")
                    story = get_active_story()
                    if story:
                        print(f"智能体: 故事标题：{story['story_title']}\n{story['story_content'][:100]}...")  # 截取部分内容
                        memory.record_interaction(CHILD_ID, None, story['story_id'], None,
                                                f"讲故事：{story['story_title']}，内容：{story['story_content'][:100]}...", -1)
                    else:
                        print("智能体: 有需要时随时叫我哦！")
                        return
            else:
                # 没有问题，就讲故事
                story = get_active_story()
                if story:
                    print(f"智能体: 我给你讲个故事吧：{story['story_title']}\n{story['story_content'][:100]}...")
                    memory.record_interaction(CHILD_ID, None, story['story_id'], None,
                                            f"讲故事：{story['story_title']}，内容：{story['story_content'][:100]}...", -1)
                else:
                    print("智能体: 有需要时随时叫我哦！")
                    return
        else:  # 讲故事
            story = get_active_story()
            if story:
                print(f"智能体: 我给你讲个故事吧：{story['story_title']}\n{story['story_content'][:100]}...")
                memory.record_interaction(CHILD_ID, None, story['story_id'], None,
                                        f"讲故事：{story['story_title']}，内容：{story['story_content'][:100]}...", -1)
            else:
                print("智能体: 有需要时随时叫我哦！")
                return

        # 讲完故事或提问后，再等待4秒，看孩子是否有反应
        user_reaction = wait_for_input(4)
        if user_reaction:
            # 如果孩子有反应，可以简单回应
            print("智能体: 你喜欢这个故事吗？")
            memory.record_interaction(CHILD_ID, None, None, user_reaction, "你喜欢这个故事吗？", -1)
        else:
            print("智能体: 有需要时随时叫我哦！")


if __name__ == "__main__":
    main_loop()
    # while True:
    #     main_loop()
    #     # 每次循环后等待一下，避免过于频繁
    #     time.sleep(1)
