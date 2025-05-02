from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from services.document_processor import DocumentProcessor
from services.llm_generator import LLMGenerator
from schemas.models import QuestionResponse, AnswerResponse, QuestionRequest
import traceback

router = APIRouter()
processor = DocumentProcessor()
generator = LLMGenerator()

@router.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    try:
        if not file.filename.lower().endswith(('.pdf', '.txt')):
            raise HTTPException(status_code=400, detail="Only PDF and TXT files are supported")
        
        file_bytes = await file.read()
        if len(file_bytes) == 0:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")
            
        vectorstore = processor.process_uploaded_file(file_bytes, file.filename)
        return {"status": "success", "filename": file.filename}
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")

@router.post("/generate-questions/", response_model=QuestionResponse)
async def generate_questions():
    try:
        if not processor.current_vectorstore:
            raise HTTPException(status_code=400, detail="No document uploaded yet")
            
        questions = generator.generate_questions(processor.current_vectorstore, 10)
        return QuestionResponse(questions=questions, status="success")
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to generate questions: {str(e)}")

@router.post("/answer/", response_model=AnswerResponse)
async def answer_question(request: QuestionRequest):
    try:
        if not processor.current_vectorstore:
            raise HTTPException(status_code=400, detail="No document uploaded yet")
            
        # Extract just the question text if it's numbered (e.g., "1. What is...")
        question_text = request.question.split('. ', 1)[1] if '. ' in request.question else request.question
        answer = generator.answer_question(processor.current_vectorstore, question_text)
        
        if not answer:
            raise HTTPException(status_code=404, detail="Answer not found in document")
            
        return AnswerResponse(answer=answer, status="success")
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to get answer: {str(e)}")