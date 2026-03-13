import uuid
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

load_dotenv()


def load_pdf(instance):
    if not instance.file:
        return None

    file_path = instance.file.path

    # Check if file exists
    if not os.path.exists(file_path):
        print("File not found:", file_path)
        return None

    try:
        loader = PyPDFLoader(file_path)
        docs = loader.load_and_split()
        return docs

    except Exception as e:
        print("Error loading PDF:", str(e))
        return None




def chunk_text(docs,instance, chunk_size=1000, overlap=200):
    """Chunk text into smaller pieces with overlap."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = text_splitter.split_documents(docs)
    for i, chunk in enumerate(chunks):
        chunk.metadata = {
            'doc_id': instance.id,
            'doc_title': instance.title,
            'doc_type': instance.category,
            'doc_version': instance.version,
            'author': chunk.metadata.get("author", "unknown"),
            'source': chunk.metadata.get("source", "unknown"),
            'page':chunk.metadata.get("page", "unknown"),
            'chunk_content': chunk.page_content,
            'chunk_content_length': len(chunk.page_content),
        }

    return chunks


def get_embeddings_model():
    return GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        api_key=os.getenv("GEMINI_API_KEY"),
    )

def generate_embeddings(chunks):
    """Generate embeddings for all chunks in a single request."""
    try:
        embeddings_model = get_embeddings_model()
        texts = [chunk.page_content for chunk in chunks]
        metadata = [chunk.metadata for chunk in chunks]

        vectors = embeddings_model.embed_documents(texts)

        embeddings = [
            {"values": vector, "metadata": metadata,"id": str(uuid.uuid4()),}
            for vector, metadata in zip(vectors, metadata)
        ]

        return embeddings

    except Exception as e:
        print(f"Error generating embeddings: {str(e)}")
        return None




def get_pinecone_instance():
    return Pinecone(api_key=os.getenv("PINECONE_API_KEY"))


def store_embeddings(vectors):
    index_name = "documents"

    # Create index if it doesn't exist
    pc = get_pinecone_instance()
    if index_name not in pc.list_indexes().names():
        pc.create_index(
            name=index_name,
            dimension=3072,
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )

    # Connect to index
    index = pc.Index(index_name)

    # Upsert in batch
    index.upsert(vectors=vectors)

    print(f"Successfully stored {len(vectors)} embeddings.")