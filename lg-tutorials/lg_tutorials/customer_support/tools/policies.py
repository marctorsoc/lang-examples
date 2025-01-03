import re
from pathlib import Path

import numpy as np
import openai
import pandas as pd
import requests
from langchain_core.tools import tool


class VectorStoreRetriever:

    md_file = Path("swiss_faq.md")
    vectors_file = Path("vectors")

    def __init__(self, oai_client):

        self._docs = self.get_docs()
        self._client = oai_client
        self._arr = self.get_vectors()

    def get_docs(self):
        self.download_if_needed()
        return self.create_docs()

    def download_if_needed(self):
        if self.md_file.exists():
            return

        response = requests.get(
            "https://storage.googleapis.com/benchmarks-artifacts/travel-db/swiss_faq.md"
        )
        response.raise_for_status()
        faq_text = response.text
        with open(self.md_file, "w") as f:
            f.write(faq_text)

    def create_docs(self):
        with open(self.md_file, "r") as f:
            faq_text = f.read()

        return [{"page_content": txt} for txt in re.split(r"(?=\n##)", faq_text)]

    def get_vectors(self):
        if self.vectors_file.exists():
            return pd.read_pickle(self.vectors_file)

        embeddings = self._client.embeddings.create(
            model="text-embedding-3-small", input=[doc["page_content"] for doc in self._docs]
        )
        vectors = np.array([emb.embedding for emb in embeddings.data])
        pd.to_pickle(vectors, self.vectors_file)
        return vectors

    def query(self, query: str, k: int = 5) -> list[dict]:
        embed = self._client.embeddings.create(model="text-embedding-3-small", input=[query])
        # "@" is just a matrix multiplication in numpy
        scores = np.array(embed.data[0].embedding) @ self._arr.T
        # get the top k scores...
        top_k_idx = np.argpartition(scores, -k)[-k:]
        # but order is not guaranteed, so now we order, but the amount to order
        # is just k <<< num docs
        top_k_idx_sorted = top_k_idx[np.argsort(-scores[top_k_idx])]
        return [{**self._docs[idx], "similarity": scores[idx]} for idx in top_k_idx_sorted]


retriever = VectorStoreRetriever(openai.Client())


@tool
def lookup_policy(query: str) -> str:
    """Consult the company policies to check whether certain options are permitted.
    Use this before making any flight changes performing other 'write' events."""
    retrieved_docs = retriever.query(query, k=2)
    return "\n\n".join([doc["page_content"] for doc in retrieved_docs])
