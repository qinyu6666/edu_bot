import pymysql
import os
from dotenv import load_dotenv

load_dotenv()


class Memory:
    def __init__(self):
        self.conn = pymysql.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", "123456"),
            database=os.getenv("DB_DATABASE", "child_edu"),
            port=int(os.getenv("DB_PORT", 3306)),
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

    def initialize_database(self):

        # 添加默认问题（如果表为空）
        with self.conn.cursor() as cursor:
            # 检查questions表是否为空 - 使用字段名访问
            cursor.execute("SELECT COUNT(*) AS count FROM questions")
            result = cursor.fetchone()
            if result and result['count'] == 0:
                default_questions = [
                    ("1+1等于几？", "2"),
                    ("中国的首都是哪里？", "北京"),
                    ("太阳从哪个方向升起？", "东方"),
                    ("一年有几个月？", "12"),
                    ("水的化学式是什么？", "H2O")
                ]
                sql = "INSERT INTO questions (question_text, standard_answer) VALUES (%s, %s)"
                cursor.executemany(sql, default_questions)
                self.conn.commit()
                print("✅ 已添加默认问题")

        # 添加默认故事（如果表为空）
        with self.conn.cursor() as cursor:
            # 检查stories表是否为空 - 使用字段名访问
            cursor.execute("SELECT COUNT(*) AS count FROM stories")
            result = cursor.fetchone()
            if result and result['count'] == 0:
                default_stories = [
                    ("小兔子的冒险", "从前有一只小兔子，它决定去森林里冒险。在森林里，它遇到了很多朋友。"),
                    ("勤劳的小蜜蜂", "在一个花园里，有一只勤劳的小蜜蜂，它每天都会去采花蜜。"),
                    ("勇敢的小蚂蚁", "一群小蚂蚁要搬家，其中一只特别勇敢的小蚂蚁负责探路。")
                ]
                sql = "INSERT INTO stories (story_title, story_content) VALUES (%s, %s)"
                cursor.executemany(sql, default_stories)
                self.conn.commit()
                print("✅ 已添加默认故事")
    def get_cursor(self):
        return self.conn.cursor()

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()

    def get_questions_by_category(self, category=None):
        with self.conn.cursor() as cursor:
            if category:
                sql = "SELECT * FROM questions WHERE category=%s"
                cursor.execute(sql, (category,))
            else:
                sql = "SELECT * FROM questions"
                cursor.execute(sql)
            return cursor.fetchall()

    def get_stories_by_category(self, category=None):
        with self.conn.cursor() as cursor:
            if category:
                sql = "SELECT * FROM stories WHERE category=%s"
                cursor.execute(sql, (category,))
            else:
                sql = "SELECT * FROM stories"
                cursor.execute(sql)
            return cursor.fetchall()

    def ensure_child_exists(self, child_id, name="默认孩子"):
        """确保孩子记录存在于数据库中"""
        try:
            with self.conn.cursor() as cursor:
                # 检查孩子是否存在
                sql = "SELECT * FROM children WHERE child_id = %s"
                cursor.execute(sql, (child_id,))
                if not cursor.fetchone():
                    # 如果不存在则创建
                    sql = "INSERT INTO children (child_id, name) VALUES (%s, %s)"
                    cursor.execute(sql, (child_id, name))
                    self.conn.commit()
                    print(f"✅ 创建了新孩子记录: ID={child_id}, 姓名={name}")
        except Exception as e:
            print(f"❌ 确保孩子存在时出错: {e}")
            self.conn.rollback()

    def get_question_memory(self, child_id, question_id):
        with self.conn.cursor() as cursor:
            sql = "SELECT * FROM question_memory WHERE child_id=%s AND question_id=%s"
            cursor.execute(sql, (child_id, question_id))
            return cursor.fetchone()

    def record_interaction(self, child_id, question_id=None, story_id=None, user_input=None, bot_response=None,
                           is_correct=-1):
     try:
        # 确保孩子存在
        self.ensure_child_exists(child_id)
        """记录交互历史（使用interactions表）"""
        with self.conn.cursor() as cursor:
            sql = """
            INSERT INTO interactions 
            (child_id, question_id, story_id, user_input, bot_response, is_correct)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                child_id,
                question_id,
                story_id,
                user_input,
                bot_response,
                is_correct
            ))
            self.conn.commit()
            return cursor.lastrowid

     except Exception as e:
        print(f"❌ 记录交互时出错: {e}")
        self.conn.rollback()
        return None

    def get_child_history(self, child_id, limit=10):
        """获取孩子的交互历史（使用interactions表）"""
        with self.conn.cursor() as cursor:
            sql = """
            SELECT * FROM interactions 
            WHERE child_id = %s 
            ORDER BY created_at DESC 
            LIMIT %s
            """
            cursor.execute(sql, (child_id, limit))
            return cursor.fetchall()

    def update_question_memory(self, child_id, question_id, is_correct, next_ask_probability):
        # 先查询是否存在记录
        memory = self.get_question_memory(child_id, question_id)
        with self.conn.cursor() as cursor:
            if memory:
                # 更新
                if is_correct:
                    new_correct = memory["correct_count"] + 1
                    sql = "UPDATE question_memory SET correct_count=correct_count + %s, last_asked_time=NOW(), next_ask_probability= %s-0.2 WHERE memory_id=%s"
                    cursor.execute(sql, (new_correct, next_ask_probability, memory['memory_id']))
                else:
                    new_incorrect = memory['incorrect_count'] + 1
                    sql = "UPDATE question_memory SET incorrect_count=incorrect_count+%s, last_asked_time=NOW(), next_ask_probability=%s-0.2 WHERE memory_id=%s"
                    cursor.execute(sql, (new_incorrect, next_ask_probability,memory['memory_id']))
            else:
                # 插入
                if is_correct:
                    sql = "INSERT INTO question_memory (child_id, question_id, correct_count, next_ask_probability) VALUES (%s, %s, %s, %s)"
                    cursor.execute(sql, (child_id, question_id, 1, next_ask_probability))
                else:
                    sql = "INSERT INTO question_memory (child_id, question_id, incorrect_count, next_ask_probability) VALUES (%s, %s, %s, %s)"
                    cursor.execute(sql, (child_id, question_id, 1, next_ask_probability))
            self.conn.commit()

    def get_poorly_remembered_questions(self, child_id, limit=5):
        """获取需要加强记忆的问题（错误次数多，或者概率高）"""
        with self.conn.cursor() as cursor:
            sql = "SELECT q.* FROM question_memory m JOIN questions q ON m.question_id=q.question_id WHERE m.child_id=%s ORDER BY m.next_ask_probability DESC, m.incorrect_count DESC LIMIT %s"
            cursor.execute(sql, (child_id, limit))
            return cursor.fetchall()

    # def add_conversation(self, child_id, question_id, story_id, user_input, bot_response, is_correct=-1):
    #     with self.conn.cursor() as cursor:
    #         sql = """INSERT INTO conversation_history
    #                  (child_id, question_id, story_id, user_input, bot_response, is_correct)
    #                  VALUES (%s, %s, %s, %s, %s, %s)"""
    #         cursor.execute(sql, (child_id, question_id, story_id, user_input, bot_response, is_correct))
    #         self.conn.commit()
    #         return cursor.lastrowid

    # 其他方法根据需要添加

    def get_next_question(self, child_id):
        """获取下一个问题（根据记忆算法）"""
        try:
            with self.conn.cursor() as cursor:
                # 获取孩子最近答错的问题
                sql = """
                SELECT q.question_id, q.question_text, q.standard_answer
                FROM interactions i
                JOIN questions q ON i.question_id = q.question_id
                WHERE i.child_id = %s AND i.is_correct = 0
                ORDER BY i.interaction_id DESC
                LIMIT 1
                """
                cursor.execute(sql, (child_id,))
                question = cursor.fetchone()

                if question:
                    return question

                # 如果没有最近答错的问题，获取孩子最少回答的问题
                sql = """
                SELECT q.question_id, q.question_text, q.standard_answer
                FROM questions q
                LEFT JOIN (
                    SELECT question_id, COUNT(*) AS answer_count
                    FROM interactions
                    WHERE child_id = %s
                    GROUP BY question_id
                ) a ON q.question_id = a.question_id
                ORDER BY COALESCE(a.answer_count, 0), RAND()
                LIMIT 1
                """
                cursor.execute(sql, (child_id,))
                question = cursor.fetchone()

                if question:
                    return question

                # 如果还是没有找到问题，返回一个随机问题
                print("⚠️ 没有找到合适的问题，返回随机问题")
                sql = "SELECT question_id, question_text, standard_answer FROM questions ORDER BY RAND() LIMIT 1"
                cursor.execute(sql)
                return cursor.fetchone() or self.get_default_question()
        except Exception as e:
            print(f"❌ 获取问题时出错: {e}")
            return self.get_default_question()

    def get_random_story(self):
        """随机获取一个故事"""
        try:
            with self.conn.cursor() as cursor:
                sql = "SELECT story_id, story_title, story_content FROM stories ORDER BY RAND() LIMIT 1"
                cursor.execute(sql)
                story = cursor.fetchone()
                if story:
                    return story

                # 如果没有故事，返回默认故事
                print("⚠️ 没有找到故事，返回默认故事")
                return self.get_default_story()
        except Exception as e:
            print(f"❌ 获取故事时出错: {e}")
            return self.get_default_story()
