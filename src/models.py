from pymysql import cursors

class KnowledgeBase:
    def __init__(self, id, content_type, content, answer, parent_id):
        self.id = id
        self.content_type = content_type
        self.content = content
        self.answer = answer
        self.parent_id = parent_id

    @classmethod
    def from_db_row(cls, row):
        return cls(
            id=row['id'],
            content_type=row['content_type'],
            content=row['content'],
            answer=row['answer'],
            parent_id=row['parent_id']
        )

class QuestionRecord:
    def __init__(self, knowledge_id, child_answer, is_correct, is_active):
        self.knowledge_id = knowledge_id
        self.child_answer = child_answer
        self.is_correct = is_correct
        self.is_active = is_active

    def to_db_tuple(self):
        return (
            self.knowledge_id,
            self.child_answer,
            self.is_correct,
            self.is_active
        )