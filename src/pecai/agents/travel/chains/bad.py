from langchain.schema.runnable import RunnablePassthrough

from pecai.agents.travel.prompts import (
    no_data_prompts,
    not_travel_prompts,
)

assigner = RunnablePassthrough.assign


def no_data_chain(llm):
    return assigner(response=no_data_prompts.no_data_response_prompt | llm)


def not_travel_chain(llm):
    return assigner(response=not_travel_prompts.not_travel_response_prompt | llm)
