from langchain_community.chat_models import ChatOllama
from langchain.prompts import PromptTemplate
from langchain_community.vectorstores import FAISS
from typing import List, Optional
import re

class LLMGenerator:
    def __init__(self):
        self.llm = ChatOllama(
            model="deepseek-r1:1.5b",
            temperature=0.7,
            top_k=50,
            top_p=0.9,
            num_ctx=2048
        )

    def generate_questions(self, vectordb: FAISS, num_questions: int = 10) -> List[str]:
        try:
            sample_docs = vectordb.similarity_search("", k=5)
            context = "\n\n".join([doc.page_content for doc in sample_docs])
            
            prompt_template = """Generate exactly {num_questions} unique study questions based on this content:
            {context}

            RULES:
            - Number each question sequentially (1., 2., etc.)
            - Each question must be distinct and answerable from the text
            - Return ONLY the numbered list, no additional text
            - Format: "1. Question text"

            QUESTIONS:
            1."""

            prompt = PromptTemplate(
                template=prompt_template,
                input_variables=["context", "num_questions"]
            ).format(
                context=context[:5000],
                num_questions=num_questions
            )

            response = self.llm.invoke(prompt)
            
            # Extract and validate questions
            questions = []
            seen_numbers = set()
            
            for line in response.content.split('\n'):
                line = line.strip()
                match = re.match(r'^(\d+)\.\s*(.+)$', line)
                if match:
                    q_num = int(match.group(1))
                    q_text = match.group(2).strip()
                    
                    if 1 <= q_num <= num_questions and q_num not in seen_numbers:
                        seen_numbers.add(q_num)
                        questions.append(f"{q_num}. {q_text}")
            
            # Fill missing numbers if needed
            for i in range(1, num_questions+1):
                if i not in seen_numbers:
                    questions.append(f"{i}. What is key concept {i} in this document?")
            
            return sorted(questions, key=lambda x: int(x.split('.')[0]))
        
        except Exception as e:
            print(f"Generation error: {str(e)}")
            return [f"{i}. Sample question {i}" for i in range(1, num_questions+1)]

    def answer_question(self, vectordb: FAISS, question: str) -> str:
        try:
            relevant_docs = vectordb.similarity_search(question, k=3)
            if not relevant_docs:
                return "Answer not found in document."
                
            context = "\n\n".join([doc.page_content for doc in relevant_docs])
            
            prompt = f"""Answer this question based ONLY on the context below:
            Question: {question}
            Context: {context}
            
            Rules:
            - Be concise (2-3 sentences)
            - If answer isn't in context, say "Not found in document"
            - Don't make up information
            
            Answer:"""
            
            response = self.llm.invoke(prompt)
            return response.content.strip()
        
        except Exception as e:
            print(f"Answer error: {str(e)}")
            return "Error generating answer."