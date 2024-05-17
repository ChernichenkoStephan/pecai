from langchain.schema.runnable import RunnablePassthrough
from langchain_core.runnables import RunnableBranch
from operator import itemgetter

from pecai.elements import links
from pecai.agents.travel.prompts import places_prompts


assigner = RunnablePassthrough.assign


def place_response_chain(nodes_printer, llm):
    return (
        assigner(nodes=links.Getter(itemgetter("nodes")) | links.LimitSelector(10))
        | assigner(additional_info=links.Getter(itemgetter("nodes")) | nodes_printer)
        | assigner(response=places_prompts.places_response_prompt | llm)
    )


def place_response_branch(place_response_chain, no_data_chain):
    return RunnableBranch(
        (lambda v: len(v["nodes"]) > 0, place_response_chain),
        no_data_chain,
    )


def place_chain(
    llm,
    cypher_query_corrector,
    graph_querier,
    relevance_sorter,
    nodes_printer,
    no_data_chain,
):
    return (
        assigner(generated_query=places_prompts.places_query_prompt | llm)
        | assigner(
            query=links.Getter(itemgetter("generated_query")) | cypher_query_corrector
        )
        | assigner(nodes=links.Getter(itemgetter("query")) | graph_querier)
        | assigner(nodes=links.Getter(itemgetter("nodes")) | relevance_sorter)
        | place_response_branch(place_response_chain(nodes_printer, llm), no_data_chain)
    )
