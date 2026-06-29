import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from retrieval.bm25 import BM25Retriever
from retrieval.retrieval import EnterpriseRetriever
from langchain_core.documents import Document

retriever = EnterpriseRetriever()

data = retriever.collection.get(
    include=["documents", "metadatas"]
)

documents = [
    Document(
        page_content=text,
        metadata=metadata,
    )
    for text, metadata in zip(
        data["documents"],
        data["metadatas"],
    )
]

bm25 = BM25Retriever(documents)

results = bm25.retrieve(
    "password policy",
    top_k=5,
)

print("\n===== BM25 RESULTS =====\n")

for i, doc in enumerate(results, start=1):

    print(f"{i}")

    print(doc.metadata["document"])

    print(doc.metadata["page"])

    print(doc.page_content[:150])

    print("-" * 60)
