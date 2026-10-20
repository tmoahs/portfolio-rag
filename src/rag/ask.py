from src.rag.retrieval import retrieve
from src.rag.generation import generate_answer

def ask():
    question = input('Pose ta question :')
    chunks = retrieve(question)
    response = generate_answer(question, chunks)
    print(response['answer'])
    print(response['sources'])
    print(response['latency'])
    print(response['tokens'])

if __name__ == "__main__":
    ask()