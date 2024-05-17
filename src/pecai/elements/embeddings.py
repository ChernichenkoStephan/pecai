import torch
from sentence_transformers import SentenceTransformer

from . import links
from . import log

logger = log.getLogger(__name__)


class BaseTextEmbedder:
    def embed(self, text: str) -> list[float]:
        return []

    def __call__(self, text: str) -> list[float]:
        return self.embed(text)


class MiniLMEmbedder(BaseTextEmbedder):
    def __init__(self, model=None):
        self._model = (
            model
            if model
            else SentenceTransformer(
                "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
            )
        )

    def embed(self, text: str) -> list[float]:
        device_name = "cuda" if torch.cuda.is_available() else "cpu"
        device_name = "mps" if torch.backends.mps.is_available() else "cpu"
        device = torch.device(device_name)
        self._model.to(device)
        return self._model.encode(text).tolist()


class InputEmbedder(links.BaseLink):
    def __init__(self, text_embedder):
        self._text_embedder = text_embedder

    def embed(self, text: str) -> list[float]:
        return self._text_embedder(text)

    def __call__(self, text: str) -> list[float]:
        return self.embed(text)


if __name__ == "__main__":
    mlm_model = SentenceTransformer(
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )
    miniLM_embedder = MiniLMEmbedder(mlm_model)
    input_embedder = InputEmbedder(miniLM_embedder)
    test_embedds = input_embedder("Составь маршрут для выходных в Санкт-Петербурге.")
    print(test_embedds[:10])
