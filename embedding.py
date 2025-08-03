from google import genai
from google.genai import types
from kaggle_secrets import UserSecretsClient
import chromadb
from google.api_core import retry

GOOGLE_API_KEY = UserSecretsClient().get_secret("GOOGLE_API_KEY")
client = genai.Client(api_key=GOOGLE_API_KEY)

class GeminiEmbeddingFunction(chromadb.api.EmbeddingFunction):
    document_mode = True

    @retry.Retry(predicate=lambda e: isinstance(e, genai.errors.APIError) and e.code in {429, 503})
    def __call__(self, input: list[str]) -> list[list[float]]:
        task = "retrieval_document" if self.document_mode else "retrieval_query"
        response = client.models.embed_content(
            model="models/text-embedding-004",
            contents=input,
            config=types.EmbedContentConfig(task_type=task),
        )
        return [embedding.values for embedding in response.embeddings]

embed_fn = GeminiEmbeddingFunction()
