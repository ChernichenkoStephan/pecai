from langchain.prompts import PromptTemplate


info_response_prompt = PromptTemplate.from_template("""
Task:Generate responce based on question and additional info
# Instructions
+ Use provided information as much as possible
+ Answer in Russian
# Additional info
{additional_info}
# Question
{question}""")

if __name__ == "__main__":
    print(
        info_response_prompt.invoke(
            {v: "" for v in ["additional_info", "question"]}
        ).text
    )
