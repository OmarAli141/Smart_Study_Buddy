import os
from services.document_processor import DocumentProcessor
from services.llm_generator import LLMGenerator

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def display_questions(questions):
    clear_screen()
    print("\n=== Generated Questions ===")
    for q in questions:
        print(q)
    print("\n")

def main():
    document_processor = DocumentProcessor()
    llm_generator = LLMGenerator()

    print("=== Smart Study Buddy ===")
    print("Using DeepSeek 1.5B via Ollama\n")
    print("Note: Make sure 'ollama serve' is running\n")

    while True:
        file_path = input("Enter file path (or 'quit'): ").strip()
        if file_path.lower() == 'quit':
            break
        
        if not os.path.exists(file_path):
            print("Error: File not found")
            continue
        
        try:
            print("\nProcessing document...", end='', flush=True)
            with open(file_path, "rb") as f:
                vectorstore = document_processor.process_uploaded_file(
                    f.read(), 
                    os.path.basename(file_path)
                )
            print(" Done!")
            
            print("Generating questions...", end='', flush=True)
            questions = llm_generator.generate_questions(vectorstore)
            print(" Done!\n")
            
            display_questions(questions)

            while True:
                choice = input("Choose question (1-10), 'new', or 'quit': ").strip().lower()
                
                if choice == 'quit':
                    return
                if choice == 'new':
                    break
                
                try:
                    q_num = int(choice)
                    if 1 <= q_num <= 10:
                        question_text = questions[q_num-1].split('. ', 1)[1]
                        print(f"\nGenerating answer for: {question_text}...", end='', flush=True)
                        answer = llm_generator.answer_question(vectorstore, question_text)
                        print(" Done!\n")
                        
                        clear_screen()
                        print(f"\n=== Question {q_num} ===")
                        print(question_text)
                        print(f"\n=== Answer ===")
                        print(answer)
                        print("\n" + "="*50 + "\n")
                        
                        input("Press Enter to return to questions...")
                        display_questions(questions)
                    else:
                        print("Please enter 1-10")
                except ValueError:
                    print("Invalid input. Enter a number, 'new', or 'quit'")
                    
        except Exception as e:
            print(f"\nError: {str(e)}\n")

if __name__ == "__main__":
    main()