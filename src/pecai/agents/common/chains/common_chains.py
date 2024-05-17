from langchain.schema.runnable import RunnablePassthrough
from langchain_core.runnables import RunnableBranch
from operator import itemgetter

from pecai.elements import links
from pecai.agents.common.prompts import hyde_prompts


assigner = RunnablePassthrough.assign


def preprocessing_chain(extractor, keyworder, tagger, input_embedder):
    return (
        assigner(question=links.Getter(itemgetter("input")))
        | assigner(entities=lambda p: extractor(p["question"]))
        | assigner(keywords=lambda p: keyworder(p["entities"]))
        | assigner(tagged_question=lambda p: tagger(p["question"], p["entities"]))
        | assigner(embedds=links.Getter(itemgetter("question")) | input_embedder)
    )


def deepsearch_chain(hybrid_querier, vector_querier, hyde_chain):
    return (
        assigner(nodes=lambda p: hybrid_querier(p["embedds"], p["keywords"]))
        | assigner(
            nodes=links.OptionalMap(
                "nodes",
                runnable=lambda p: vector_querier(p["embedds"]),
                criteria=lambda p: len(p["nodes"]) == 0,
            )
        )
        | RunnableBranch(
            (lambda v: len(v["nodes"]) == 0, hyde_chain),
            links.DoNothing(),
        )
    )


def make_hyde_embeddings(answers_text, embedder):
    answers = answers_text.split(";")
    return [embedder(ans) for ans in answers]


def hyde_chain(llm, input_embedder, vector_querier):
    return (
        assigner(answers=hyde_prompts.hyde_query_prompt | llm)
        | assigner(
            hyde_embeddings=lambda p: make_hyde_embeddings(p["answers"], input_embedder)
        )
        | assigner(nodes=lambda p: vector_querier.query_many(p["hyde_embeddings"]))
    )
