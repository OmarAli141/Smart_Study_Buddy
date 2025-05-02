from pydantic import BaseModel

class QuestionRequest(BaseModel):
    question: str

class QuestionResponse(BaseModel):
    questions: list[str]
    status: str

class AnswerResponse(BaseModel):
    answer: str
    status: str