from sentence_transformers import SentenceTransformer
from langchain_community.graphs import Neo4jGraph
import pymystem3
import spacy

import sys
import os

root_rel_path = "./src" if os.getenv("ENVIROMENT") == "plain" else "./"
root_path = os.path.abspath(root_rel_path)
sys.path.insert(0, root_path)

from pecai.agents.travel import agent as travel_agent
from pecai.elements.llm import yandex
from pecai.elements import tg_bot
from pecai.elements import log

logger = log.getLogger(__name__)

greetings_message = (
    """Добро пожаловать в вашего надежного спутника по путешествиям! 🌍✈️ Я здесь, чтобы помочь вам спланировать идеальное путешествие, поделиться полезными советами и ответить на любые вопросы о вашем следующем направлении. Хотите узнать лучшие места для посещения, секретные уголки городов или нужны рекомендации по бронированию? Просто спросите меня! Начнем планировать ваше следующее приключение? 🌆 Сейчас я спец в путешествиях по Санкт-Петербургу! А еще я знаю как устроить необычную поездку по следам Данилы из франшизы "Брат"."""
    """
Задавай вопросы на темы:
ℹ️ Информация о известных местах
⭐️Развлечения / еда / отдых
    """
    """
Или просто попроси спланироать путешествие фразой "спланируй поезку в Питер"!🚀
"""
)

examples = [
    "Спланируй поездку в Санкт-Петербурге",
    "Где можно отдохнуть в Санкт-Петербурге?",
    "Где развлечься в Санкт-Петербурге?",
    'Где происходят события фильма "Брат"?',
    "Расскажи про Спас на Крови",
    "Расскажи про Апраксин двор",
    "Расскажи про «Подписные издания»",
    "Расскажи про Павловск",
]

help_text = f"Примеры вопросов на которые я могу ответить:\n+ {'\n+ '.join(examples)}"


config = {
    "neo4j": {
        "url": os.getenv("NEO4J_URL"),
        "username": os.getenv("NEO4J_USERNAME"),
        "password": os.getenv("NEO4J_PASSWORD"),
    },
    "telegram": {
        "bot_token": os.getenv("TG_BOT_TOKEN"),
        "bot_root": os.getenv("TG_BOT_ROOT"),
    },
    "yandex": {
        "folder_id": os.getenv("YANDEX_FOLDER_ID"),
        "service_account_id": os.getenv("YANDEX_SERVICE_ACCOUNT_ID"),
        "key_file": os.getenv("YANDEX_KEY_FILE"),
    },
    "models": {
        "spacy_model": os.getenv("SPACY_MODEL"),
        "embeddings_model": os.getenv("EMBEDDINGS_MODEL_MODEL"),
    },
}


def main():
    logger.debug(config)

    graph = Neo4jGraph(
        url=config["neo4j"]["url"],
        username=config["neo4j"]["username"],
        password=config["neo4j"]["password"],
    )
    nlp = spacy.load(config["models"]["spacy_model"])
    lem = pymystem3.Mystem()

    llm = yandex.YaLLM(
        api=yandex.YaGPTAPI(
            folder_id=config["yandex"]["folder_id"],
            service_account_id=config["yandex"]["service_account_id"],
            key_file=config["yandex"]["key_file"],
        )
    )

    embeddings_model = SentenceTransformer(config["models"]["embeddings_model"])

    bot = tg_bot.BotAgent(
        config["telegram"]["bot_token"],
        config["telegram"]["bot_root"],
        greetings_message,
        help_text,
        travel_agent.Agent(graph, lem, nlp, llm, embeddings_model=embeddings_model),
    )
    bot.start()


if __name__ == "__main__":
    main()
