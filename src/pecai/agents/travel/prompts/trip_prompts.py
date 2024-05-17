from langchain.prompts import PromptTemplate


trip_response_prompt = PromptTemplate.from_template("""
# Context
I have data about places. I need to answer in question with context of this data
# Task
1. Based on the retrieved data, identify key locations and events that match the user's question.
2. Use provided information as much as possible
3. Generate a day-by-day itinerary that includes:
   - Morning, afternoon, and evening activities.
   - Recommendations for dining, highlighting local cuisine.
   - Any relevant cultural or seasonal events, especially related to cherry blossoms.
   - Links or references to articles for deeper exploration of each recommended site or activity.
4. Provide alternative suggestions for each day, considering weather, crowd levels, and user preferences for more relaxed or active days.
5. Summarize the trip plan, highlighting unique experiences and offering tips for transportation and accommodation, if available in the database.
6. Answer in Russian
# Retrieved data
{additional_info}
# Question
{question}""")

if __name__ == "__main__":
    print(trip_response_prompt.invoke({"additional_info": "", "question": ""}).text)
