import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from retrieval.retrieval import EnterpriseRetriever

retriever = EnterpriseRetriever()

response = retriever.retrieve(
    "What is the password policy?"
)

print()

print("Search Type :", response.search_type)

print("Chunks :", response.result_count)

print()

for chunk in response.retrieved_chunks:
    print(chunk.document)
    print(chunk.page)
    print(chunk.score)
    print("-" * 40)
