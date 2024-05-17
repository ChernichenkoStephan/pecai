from langchain.schema.runnable import RunnablePassthrough
from langchain_core.runnables import RunnableBranch
from operator import itemgetter

from pecai.elements import links
from pecai.agents.travel.prompts import info_prompts


assigner = RunnablePassthrough.assign


def info_response_chain(nodes_printer, llm):
    return (
        assigner(nodes=links.Getter(itemgetter("nodes")) | links.LimitSelector(3))
        | assigner(additional_info=links.Getter(itemgetter("nodes")) | nodes_printer)
        | assigner(response=info_prompts.info_response_prompt | llm)
    )


def info_response_branch(info_response_chain, no_data_chain):
    return RunnableBranch(
        (lambda v: len(v["nodes"]) > 0, info_response_chain),
        no_data_chain,
    )


def info_chain(deepsearch_chain, no_data_chain, nodes_printer, llm):
    return deepsearch_chain | info_response_branch(
        info_response_chain(nodes_printer, llm), no_data_chain
    )
