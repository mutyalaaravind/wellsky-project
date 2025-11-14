from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import VertexAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.llms import VertexAI

from formographer.infrastructure.ports import IQNAPort


class TextBisonQNAAdapter(IQNAPort):
    class TextBisonQNAModel(IQNAPort.IQNAModel):
        def __init__(self, qa: RetrievalQA):
            self.qa = qa

        async def query(self, question: str) -> str:
            return self.qa({'query': question})['result']

    def __init__(self, project):
        self.embeddings = VertexAIEmbeddings(project=project)
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=0)

    async def build_model(self, text: str) -> IQNAPort.IQNAModel:
        docs = self.text_splitter.split_text(text)

        db = Chroma.from_texts(docs, self.embeddings)
        retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 1})
        llm = VertexAI(
            model_name="text-bison@001",
            max_output_tokens=256,
            temperature=0.1,
            top_p=0.8,
            top_k=40,
            verbose=True,
        )
        qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever, return_source_documents=True)
        return self.TextBisonQNAModel(qa)
