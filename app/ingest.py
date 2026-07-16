# from langchain_community.document_loaders import PyPDFLoader
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_google_genai import GoogleGenerativeAIEmbeddings
# from dotenv import load_dotenv
# import os
# from langchain_community.vectorstores import FAISS

# loader = PyPDFLoader("data/sample.pdf")
# documents = loader.load()

# text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
# chunks = text_splitter.split_documents(documents)

# load_dotenv()
# embeddings = GoogleGenerativeAIEmbeddings(
#   model="models/gemini-embedding-001",
#   api_key=os.environ.get("GOOGLE_API_KEY"))

# test_vector = embeddings.embed_query(chunks[0].page_content)

# vectorstore = FAISS.from_documents(chunks, embeddings)

# vectorstore.save_local("vectorstore")

# print("FAISS index created and saved to 'vectorstore/' folder")