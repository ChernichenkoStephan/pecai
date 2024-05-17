from langchain.schema.runnable import RunnablePassthrough
from operator import itemgetter

from pecai.elements import links
from pecai.agents.travel.queries import trip_queries
from pecai.agents.travel.prompts import trip_prompts


assigner = RunnablePassthrough.assign


def trip_chain(graph_querier, relevance_sorter, nodes_printer, llm):
    return (
        assigner(nodes=lambda _: graph_querier(trip_queries.trip_query))
        | assigner(nodes=links.Getter(itemgetter("nodes")) | relevance_sorter)
        | assigner(nodes=links.Getter(itemgetter("nodes")) | links.LimitSelector(10))
        | assigner(additional_info=links.Getter(itemgetter("nodes")) | nodes_printer)
        | assigner(response=trip_prompts.trip_response_prompt | llm)
    )
