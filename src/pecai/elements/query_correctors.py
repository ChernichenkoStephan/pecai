from langchain.chains.graph_qa import cypher_utils

from . import links
from . import log


logger = log.getLogger(__name__)


class CypherQueryCorrector(links.BaseLink):
    def __init__(self, graph):
        self._graph = graph
        self._query_corrector = None
        self._set_or_update_query_corrector()

    def _set_or_update_query_corrector(self):
        corrector_schema = [
            cypher_utils.Schema(element["start"], element["type"], element["end"])
            for element in self._graph.structured_schema.get("relationships")
        ]
        self._query_corrector = cypher_utils.CypherQueryCorrector(corrector_schema)

    def __call__(self, query: str) -> str:
        logger.info(f"CypherQueryCorrector: {query=}")
        query = query.replace("`", "").strip()
        return self._query_corrector(query)
