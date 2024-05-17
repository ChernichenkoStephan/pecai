from langchain.schema.runnable import RunnablePassthrough
from langchain_core.runnables import RunnableBranch
from langchain_community.graphs import Neo4jGraph
import pymystem3
from operator import itemgetter

from pecai.agents.common.chains import common_chains

from pecai.elements import query_correctors
from pecai.elements import nodes_printers
from pecai.elements import nodes_sorters
from pecai.elements import graph_queriers
from pecai.elements import disambiguators
from pecai.elements import embeddings
from pecai.elements import extractors
from pecai.elements import keyworders
from pecai.elements import taggers
from pecai.elements import routers
from pecai.elements import links
from pecai.elements import log

from pecai.agents.travel.queries import (
    hybrid_queries,
    vector_queries,
)
from pecai.agents.travel.chains import (
    bad,
    info,
    place,
    trip,
)
from pecai.agents.travel.prompts import places_prompts


assigner = RunnablePassthrough.assign

logger = log.getLogger(__name__)


class Agent:
    def __init__(
        self,
        graph: Neo4jGraph,
        lemmatizer: pymystem3.mystem.Mystem,
        nlp,
        llm,
        embeddings_model=None,
    ):
        self.__graph = graph
        graph.refresh_schema()
        graph_querier = graph_queriers.GraphQuerier(graph)

        hybrid_querier = graph_queriers.HybridQuerier(
            graph_querier,
            [hybrid_queries.span_hybrid_query, hybrid_queries.doc_hybrid_query],
            score_threshold=0.2,
        )

        vector_querier = graph_queriers.VectorQuerier(
            graph_querier,
            [
                vector_queries.doc_embeddings_query,
                vector_queries.place_embeddings_query,
                vector_queries.span_embeddings_query,
            ],
            score_threshold=0.75,
        )
        logger.info("queriers init done.")

        disambiguator = disambiguators.Disambiguator(
            {
                "санкт-петербург": ["петербург", "питер"],
                "российский федерация": ["рф", "россия"],
                "российский академия наука": ["ран"],
            },
            lemmatizer=lemmatizer,
        )

        spacy_extractor = extractors.SpacyExtractor([disambiguator], nlp)
        keyworder = keyworders.Keyworder()
        tagger = taggers.Tagger()
        logger.info("entity workers init done.")

        miniLM_embedder = embeddings.MiniLMEmbedder(embeddings_model)
        input_embedder = embeddings.InputEmbedder(miniLM_embedder)
        centroid_router = routers.CentroidRouter(miniLM_embedder)
        centroid_router.fit(routers.clusters_data)
        logger.info("embeddings workers init done.")

        cypher_query_corrector = query_correctors.CypherQueryCorrector(graph)
        nodes_printer = nodes_printers.Printer()
        relevance_sorter = nodes_sorters.RelevanceSorter()
        logger.info("node workers init done.")

        preprocessing_chain = common_chains.preprocessing_chain(
            spacy_extractor,
            keyworder,
            tagger,
            input_embedder,
        )

        hyde_chain = common_chains.hyde_chain(
            llm,
            input_embedder,
            vector_querier,
        )

        deepsearch_chain = common_chains.deepsearch_chain(
            hybrid_querier,
            vector_querier,
            hyde_chain,
        )

        no_data_chain = bad.no_data_chain(llm)
        not_travel_chain = bad.not_travel_chain(llm)

        info_chain = info.info_chain(
            deepsearch_chain, no_data_chain, nodes_printer, llm
        )
        place_chain = place.place_chain(
            llm,
            cypher_query_corrector,
            graph_querier,
            relevance_sorter,
            nodes_printer,
            no_data_chain,
        )
        trip_chain = trip.trip_chain(
            graph_querier, relevance_sorter, nodes_printer, llm
        )

        routes_branch = RunnableBranch(
            (lambda v: v["topic"] in ["place", "city_places"], place_chain),
            (
                lambda v: v["topic"]
                in [
                    "info",
                    "travel_info",
                    "movie_storyline",
                    "movie_places",
                    "travel_place_info",
                ],
                info_chain,
            ),
            (lambda v: v["topic"] in ["trip"], trip_chain),
            not_travel_chain,
        )

        self.__chain = (
            assigner(question=links.Getter(itemgetter("input")))
            | preprocessing_chain
            | assigner(topic=links.Getter(itemgetter("question")) | centroid_router)
            | routes_branch
            | links.Getter(itemgetter("response"))
        )
        logger.info("chains setup done.")

    def run(self, user_input: str) -> str:
        try:
            return self.__chain.invoke(
                {
                    "input": user_input,
                    "graph_schema": self.__graph.schema,
                    "options": places_prompts.PLACES_OPTIONS,
                }
            )
        except Exception as e:
            logger.error(str(e))
            return "Ой, что-то случилось. Попробуйте повторить запрос или прийти позже."

    def __call__(self, user_input: str) -> str:
        return self.run(user_input)
