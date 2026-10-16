from pathlib import Path
from src.rag.config import KNOWLEDGE_DIR

def load_documents(knowledge_dir):
    documents = []
    for file_path in sorted(knowledge_dir.glob("*.md")):
        text = file_path.read_text(encoding="utf-8")
        doc = {
            "source": file_path.name,
            "text": text
        }
        documents.append(doc)

    return documents

if __name__ == "__main__":
    documents = load_documents(KNOWLEDGE_DIR)
    print('Nombre de documents: ', len(documents))
    print()
    for document in documents:
        print(document["source"])
        print('Nombre de caractères :',len(document["text"]))
        print()
    top = max(documents, key=lambda doc: len(doc["text"]))
    print('Le fichier le plus long est :', top['source'])