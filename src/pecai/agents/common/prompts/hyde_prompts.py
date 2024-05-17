from langchain.prompts import PromptTemplate


hyde_query_prompt = PromptTemplate.from_template("""
# Context
A question has been asked.
Task
+ Generate few short answers
+ Generate only answers
+ The answers should be no more than one sentence
+ The answers should be separated by a ";" sign
+ Do not add any numeration
+ Answer in Russian
# Question
{question}""")

if __name__ == "__main__":
    print(hyde_query_prompt.invoke({v: "" for v in ["question"]}).text)
