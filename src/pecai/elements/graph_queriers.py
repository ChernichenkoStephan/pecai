from . import log
from . import links

logger = log.getLogger(__name__)


class GraphQuerier(links.BaseLink):
    def __init__(self, graph):
        self._graph = graph

    def unwrap_response(self, data: list[dict[dict]]) -> list[dict]:
        res = []
        for sub_resp in data:
            for k, v in sub_resp:
                res += v
        return res

    def _query(self, query: str, **kwargs) -> list:
        try:
            return [
                v for vv in self._graph.query(query, params=kwargs) for v in vv.values()
            ]
        except Exception as e:
            logger.error(f"GraphQuerier got: {e}")
            return []

    def query(self, query: str, **kwargs) -> list:
        resp = self._query(query, **kwargs)
        logger.info(f"GraphQuerier: {query}, {len(resp)=}")
        return resp

    def __call__(self, query: str, **kwargs) -> list:
        return self.query(query, **kwargs)


class VectorQuerier(links.BaseLink):
    def __init__(self, graph_querier, queries, score_threshold=0.75, limit=3):
        self._graph_querier = graph_querier
        self._queries = queries
        self._score_threshold = score_threshold
        self._limit = limit

    def _query(self, embeddings: list[float]) -> list:
        resp = [
            node
            for q in self._queries
            for node in self._graph_querier(
                q,
                embeddings=embeddings,
                limit=self._limit,
                score_threshold=self._score_threshold,
            )
        ]
        return resp

    def query(self, embeddings: list[float]) -> list:
        return self._query(embeddings)

    def query_many(self, embeddings: list[list[float]]) -> list:
        return [node for emb in embeddings for node in self._query(emb)]

    def __call__(self, embeddings: list[float]) -> list:
        return self._query(embeddings)


class HybridQuerier(links.BaseLink):
    def __init__(self, graph_querier, queries, score_threshold=0.75, limit=3):
        self._graph_querier = graph_querier
        self._queries = queries
        self._score_threshold = score_threshold
        self._limit = limit

    def _query(self, embeddings: list[float], keys: list) -> str:
        resp = list(
            [
                node
                for q in self._queries
                for node in self._graph_querier(
                    q,
                    embeddings=embeddings,
                    limit=self._limit,
                    score_threshold=self._score_threshold,
                    keys=keys,
                )
            ]
        )
        return resp

    def query(self, embeddings: list[float], keys: list) -> str:
        return self._query(embeddings, keys)

    def __call__(self, embeddings: list[float], keys: list) -> str:
        return self._query(embeddings, keys)
