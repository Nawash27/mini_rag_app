# from fastapi import FastAPI
# from langchain_community.vectorstores import FAISS
# from pydantic import BaseModel
# from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_google_genai import GoogleGenerativeAIEmbeddings
# from dotenv import load_dotenv
# import os

# load_dotenv()

# embeddings = GoogleGenerativeAIEmbeddings(
#     model="models/gemini-embedding-001",
#     google_api_key=os.getenv("GOOGLE_API_KEY")
# )

# vectorstore = FAISS.load_local(
#     "vectorstore",
#     embeddings,
#     allow_dangerous_deserialization=True
# )

# app = FastAPI()

# class Question(BaseModel):
#     query: str

# llm = ChatGoogleGenerativeAI(
#     model="gemini-3.1-flash-lite",
#     google_api_key=os.getenv("GOOGLE_API_KEY")
# )

# @app.post("/ask")
# def ask(question: Question):
#     # Step 1: Retrieve top matching chunks from FAISS
#     docs = vectorstore.similarity_search(question.query, k=3)

#     # Step 2: Combine retrieved chunks into one context block
#     context = "\n\n".join([doc.page_content for doc in docs])

#     # Step 3: Build the prompt
#     prompt = f"""Answer the question based only on the context below.
# If the answer isn't in the context, say you don't know.

# Context:
# {context}

# Question: {question.query}
# """

#     # Step 4: Call Gemini to generate the answer
#     response = llm.invoke(prompt)

#     # Handle both plain string and structured list responses
#     if isinstance(response.content, list):
#         answer_text = " ".join(
#             block.get("text", "") for block in response.content if isinstance(block, dict)
#         )
#     else:
#         answer_text = response.content

#     return {
#         "answer": answer_text,
#         "sources": [doc.page_content[:100] for doc in docs]
#     }