from fastapi import FastAPI, UploadFile, File, HTTPException
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv
import os
import shutil

load_dotenv()

app = FastAPI()

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

os.makedirs("app/static", exist_ok=True)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
def home():
    return FileResponse("app/static/index.html")

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

os.makedirs("data", exist_ok=True)
os.makedirs("vectorstore", exist_ok=True)


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    # Validate file type
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    doc_name = os.path.splitext(file.filename)[0]
    save_path = f"data/{file.filename}"

    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    loader = PyPDFLoader(save_path)
    documents = loader.load()

    if not documents or not any(doc.page_content.strip() for doc in documents):
        raise HTTPException(
            status_code=422,
            detail="No extractable text found in this PDF. It may be a scanned image without OCR — try a text-based PDF."
        )

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_documents(documents)

    if not chunks:
        raise HTTPException(status_code=422, detail="Could not split document into chunks.")

    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local(f"vectorstore/{doc_name}")

    return {
        "message": f"'{file.filename}' processed successfully",
        "doc_id": doc_name,
        "num_chunks": len(chunks)
    }
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite",
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

class Question(BaseModel):
    query: str
    doc_id: str


@app.get("/documents")
def list_documents():
    if not os.path.exists("vectorstore"):
        return {"documents": []}
    docs = [
        name for name in os.listdir("vectorstore")
        if os.path.isdir(os.path.join("vectorstore", name))
    ]
    return {"documents": docs}


@app.post("/ask")
def ask(question: Question):
    index_path = f"vectorstore/{question.doc_id}"

    if not os.path.exists(index_path):
        raise HTTPException(
            status_code=404,
            detail=f"No document found with id '{question.doc_id}'. Upload it first via /upload."
        )

    if not question.query.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    vectorstore = FAISS.load_local(
        index_path, embeddings, allow_dangerous_deserialization=True
    )

    docs = vectorstore.similarity_search(question.query, k=3)

    if not docs:
        return {"answer": "I couldn't find anything relevant in this document.", "sources": []}

    context = "\n\n".join([doc.page_content for doc in docs])

    prompt = f"""Answer the question based only on the context below.
If the answer isn't in the context, say you don't know.

Context:
{context}

Question: {question.query}
"""

    try:
        response = llm.invoke(prompt)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LLM call failed: {str(e)}")

    if isinstance(response.content, list):
        answer_text = " ".join(
            block.get("text", "") for block in response.content if isinstance(block, dict)
        )
    else:
        answer_text = response.content

    return {
        "answer": answer_text,
        "sources": [doc.page_content[:100] for doc in docs]
    }