from langchain.prompts import PromptTemplate


not_travel_response_prompt = PromptTemplate.from_template("""
# Context
We have received a request outside the travel industry and cannot respond to it. 
# Task
+ Generate a polite refusal.
+ Be polite
+ Do not use name in answer
+ Answer in Russian
# Example
К сожалению, я могу дать вам подсказку. Я ее не понимаю. Но я могу рассказать вам кое-что о путешествиях!
""")

if __name__ == "__main__":
    print(not_travel_response_prompt.invoke({}).text)
