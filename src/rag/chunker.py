from google.genai._gaos.types.interactions import source, content
from rag.config import CHUNK_SIZE

# ----------------------------------------------------------------------------------------
def split_by_markdown_headers(text: str):
    sections = []
    current_title = "Introduction"
    current_lines = []

    for line in text.splitlines():
        if line.startswith("#"):
            content = "\n".join(current_lines).strip()
            if content:
                sections.append({"title": current_title, "content": content})
            current_title = line.lstrip("#").strip()
            current_lines = []
        else:
            current_lines.append(line)

    content = "\n".join(current_lines).strip()
    if content:
        sections.append({"title": current_title, "content": content})

    return sections

# -----------------------------------------------------------------------------------------
def create_chunk(source, title, content, index=0):
    text_with_context = f"[{source} > {title}]\n{content}"
    clean_title = title.lower().replace(" ", "_")
    chunk_id = f"{source}::{clean_title}::{index}"

    return {
        "id": chunk_id,
        "source": source,
        "title": title,
        "text": text_with_context
    }

# -----------------------------------------------------------------------------------------
def chunk_section(source, title, content, max_chunk_size):
    chunks = []

    # 1. Si la section rentre en entier
    if len(content) <= max_chunk_size:
        return [create_chunk(source, title, content, index=0)]

    # 2. Sinon, découpage par paragraphes
    paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
    current_chunk_text = ""
    chunk_index = 0

    for para in paragraphs:
        # Si ajouter ce paragraphe fait dépasser la limite et qu'on a déjà du texte
        if current_chunk_text and (len(current_chunk_text) + len(para) + 2 > max_chunk_size):
            chunks.append(create_chunk(source, title, current_chunk_text, index=chunk_index))
            chunk_index += 1
            current_chunk_text = para
        else:
            if current_chunk_text:
                current_chunk_text += "\n\n" + para
            else:
                current_chunk_text = para

    # Sauvegarder le dernier morceau restant après la boucle
    if current_chunk_text:
        chunks.append(create_chunk(source, title, current_chunk_text, index=chunk_index))

    return chunks

# ----------------------------------------------------------------------------------------------------
def chunk_all_documents(documents, max_chunk_size=500):
    all_chunks = []

    for doc in documents:
        sections = split_by_markdown_headers(doc["text"])
        for section in sections:
            section_chunks = chunk_section(
                source=doc["source"],
                title=section["title"],
                content=section["content"],
                max_chunk_size=max_chunk_size
            )
            # .extend() ajoute tous les éléments d'une liste dans une autre liste
            all_chunks.extend(section_chunks)

    return all_chunks

# ----------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    from src.rag.config import KNOWLEDGE_DIR, CHUNK_SIZE
    from src.rag.loader import load_documents

    documents = load_documents(KNOWLEDGE_DIR)
    chunks = chunk_all_documents(documents, max_chunk_size=CHUNK_SIZE)

    print(f"Nombre total de chunks créés : {len(chunks)}")

    # 1. Vérification des longueurs
    lengths = [len(c["text"]) for c in chunks]
    print(f"Taille min : {min(lengths)} car.")
    print(f"Taille max : {max(lengths)} car.")
    print(f"Taille moyenne : {sum(lengths) / len(lengths):.1f} car.")

    # 2. Vérification des identifiants uniques
    ids = [c["id"] for c in chunks]
    print(f"Identifiants uniques : {len(set(ids))} / {len(ids)}")

    # 3 Chunk le plus long
    longest_chunk = max(chunks, key=lambda c: len(c["text"]))
    print("Chunk le plus long :", longest_chunk["id"])
    print(longest_chunk["text"])