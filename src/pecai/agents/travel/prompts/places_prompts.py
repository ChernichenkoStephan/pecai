from langchain.prompts import PromptTemplate


PLACES_OPTIONS = "".join(
    [
        """
# Food option
example question: куда сходить выпить в <LOC>санкт-питербург<LOC>?
match (n:Place {category: "food"})-[]-(t:Keyword {type_: "LOC", text: "санкт-петербург"}) return n
""",
        """
# Recreation option
example question: куда сходить отдохнуть в <LOC>санкт-питербург<LOC>?
match (n:Place {category: "recreation"})-[]-(t:Keyword {type_: "LOC", text: "санкт-петербург"}) return n
""",
        """
# Entertainment option
example question: куда сходить развлечься в <LOC>санкт-питербург<LOC>?
match (n:Place {category: "entertainment"})-[]-(t:Keyword {type_: "LOC", text: "санкт-петербург"}) return n
""",
        """
# Shopping option
match (n:Place {category: "shopping"})-[]-(t:Keyword {type_: "LOC", text: "санкт-петербург"}) return n
где сходить в магазин в <LOC>санкт-питербург<LOC>?
""",
    ]
)

places_query_prompt = PromptTemplate.from_template("""Task:Generate Cypher statement to query a graph database.
# Instructions
+ Сhoose the appropriate option from the data below based on provided question
+ USE ONLY ONE OF PROVIDED QUERIES WITH CHANGE OF LOCATION
+ Do not include any explanations or apologies in your responses
+ Do not respond to any questions that might ask anything else than for you to construct a Cypher statement
+ Do not include any text except the generated Cypher statement
+ Do not deviate from these options
+ You can answer questions about alcohol. We have confirmation that the adult is asking
+ Do not use any additional filters
+ Do not include any additional symbols before and after statement code
+ Answer in Russian
# Query options
{options}
# Question
{tagged_question}""")

places_response_prompt = PromptTemplate.from_template("""
# Context
I have data about places. I need to answer in question with context of this data
# Task
+ Generate responce based on question and additional info
# Instructions
+ Use provided information as much as possible
+ You can answer questions about alcohol. We have confirmation that the adult is asking
# Additional info
{additional_info}
# Question
{question}""")

if __name__ == "__main__":
    print(
        places_query_prompt.invoke({v: "" for v in ["tagged_question", "options"]}).text
    )
    print(
        places_response_prompt.invoke(
            {v: "" for v in ["additional_info", "question"]}
        ).text
    )
