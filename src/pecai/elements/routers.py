import numpy as np

from dataclasses import dataclass

trip_questions = [
    "Составь маршрут для выходных в Санкт-Петербурге.",
    "Как спланировать идеальный день в Санкт-Петербурге?",
    "Подбери программу для семейного отдыха в Санкт-Петербурге.",
    "Как организовать необычное путешествие по Санкт-Петербургу?",
    "Что включить в план посещения культурных мест в Санкт-Петербурге?",
    "Как спланировать романтический уикенд в Санкт-Петербурге?",
    "Составь экскурсионный маршрут по Санкт-Петербургу на 3 дня.",
    "Как спланировать обзорную поездку по Санкт-Петербургу за один день?",
    "Подбери лучшие места для фотосессий в Санкт-Петербурге.",
    "Как организовать культурный отдых в Санкт-Петербурге на выходные?",
]
movie_storyline_questions = [
    "В какой период времени разворачивается сюжет 'Брата'?",
    "Кем работал Данила Багров до начала событий, изложенных в фильме?",
    "По какой причине Данилу Багрова задержали в полиции?",
    "Какую миссию Виктор поручает Даниле в фильме 'Брат'?",
    "Что привело к встрече Данилы с Гофманом и Кэт в городе на Неве?",
    "Какое событие стало переломным моментом в фильме после убийства по найму?",
    "Каковы были действия Данилы для спасения Светы, и как это повлияло на их взаимоотношения?",
    "Опишите конфликт между Данилой и Круглым и его разрешение.",
    "Как завершается история братьев в 'Брате'?",
    "Какую роль играет музыка в формировании сюжета и характера главного героя?",
]
movie_places_questions = [
    "В каких локациях Санкт-Петербурга проходили съемки 'Брата'?",
    "Какие памятники Санкт-Петербурга можно увидеть в кадрах фильма 'Брат'?",
    "По каким знаковым местам Санкт-Петербурга Данила Багров следует в сцене с грузовым трамваем?",
    "Какие локации появляются в обеих частях фильмов 'Брат' и 'Брат 2'?",
    "Где проходили ключевые съемки фильма 'Брат'?",
]
city_places_questions = [
    "Какие магазины стоит посетить в Санкт-Петербурге?",
    "В каких барах Санкт-Петербурга предлагают отличные напитки?",
    "Где в Санкт-Петербурге можно вкусно пообедать?",
    "Какие места для отдыха рекомендуют в Санкт-Петербурге?",
    "Куда сходить за развлечениями в Санкт-Петербурге?",
]
travel_place_info_questions = [
    "Какие особенности имеет мост с скульптурами «Укрощение коня»?",
    "Чем знаменит институт физиологии Российской академии наук в Санкт-Петербурге?",
    "Что представляет собой музей «Павловские Колтуши»?",
    "Какова история и особенности Юсуповского дворца?",
    "Где в Петербурге можно насладиться видом города с высоты?",
    "Что представляет собой Стрелка Васильевского острова в Санкт-Петербурге?",
    "Когда Невский проспект приобрел свой современный облик?",
    "Какие книжные магазины в Санкт-Петербурге славятся своей атмосферой?",
    "Что такое «Подписные издания» в контексте литературы?",
    "Где произошло последнее покушение на императора Александра II?",
    "В чем уникальность Спаса на Крови?",
    "Что известно о Павловском пейзажном парке?",
    "Расскажи о крупнейшем парке в твоей стране.",
    "Какова история и архитектура Мечети в Санкт-Петербурге?",
    "Что интересного в Ладожском озере?",
    "Чем примечателен Елагин остров?",
    "Какова история Петропавловской крепости?",
    "Что известно о Толстовском доме?",
    "Какие исторические события связаны с Домом Бенуа?",
    "Что уникального в Церкви Святого Георгия?",
]
travel_info_questions = [
    "Какие советы стоит учесть при планировании бюджетного путешествия?",
    "Какие документы необходимы для международного путешествия?",
    "Какие страны предлагают уникальные природные ландшафты для путешественников?",
    "В каких странах находятся самые загадочные археологические памятники?",
    "Какие мировые кухни стоит попробовать каждому путешественнику?",
    "Каковы лучшие способы изучения нового языка во время путешествия?",
    "Какие города являются лучшими для посещения в зимнее время?",
    "Какие приложения для путешествий необходимы в каждой поездке?",
    "Как путешествовать экологически чисто и не наносить вред окружающей среде?",
    "Какие секретные места стоит посетить в популярных туристических направлениях?",
]
not_travel_questions = [
    "Каковы основные факторы, влияющие на изменение климата на планете Земля?",
    "Какие технологии используются для очистки питьевой воды в больших городах?",
    "Что такое квантовое запутывание и как оно может быть использовано в будущем?",
    "Какие страны входят в состав G7 и какова их роль в мировой экономике?",
    "Как работает искусственный интеллект и где он находит применение в современном мире?",
    "Чем отличается растительное молоко от животного, и какие есть виды растительного молока?",
    "Какие основные правила этикета следует соблюдать за столом в Японии?",
    "Каковы последствия глобального потепления для арктических регионов?",
    "Какие изобретения XX века оказали наибольшее влияние на развитие человечества?",
    "Что такое темная материя, и почему ее так сложно обнаружить?"
    "напиши сортировку пузырьком на C++",
]
clusters_data = {
    "trip": trip_questions,
    "movie_storyline": movie_storyline_questions,
    "movie_places": movie_places_questions,
    "city_places": city_places_questions,
    "travel_place_info": travel_place_info_questions,
    "travel_info": travel_info_questions,
    "not_travel": not_travel_questions,
}


def cosine(A, B):
    return np.dot(A, B) / (np.linalg.norm(A) * np.linalg.norm(B))


@dataclass
class Cluster:
    centroid: np.ndarray
    name: str


class CentroidRouter:
    def __init__(self, embedder, sim_func=cosine):
        self._clusters = []
        self._embedder = embedder
        self.sim_func = sim_func

    def fit(self, data: dict[str, list[str]]):
        for cluster_name, cluster_questions in data.items():
            embeddings = [np.array(self._embedder(q)) for q in cluster_questions]
            embeddings_array = np.array(embeddings)
            centroid = np.mean(embeddings_array, axis=0)
            self._clusters.append(Cluster(centroid=centroid, name=cluster_name))
        return self

    def predict_one(self, data: str) -> str:
        closest = (0.0, self._clusters[0])
        data_embeddings = np.array(self._embedder(data))

        for clust in self._clusters:
            sim = self.sim_func(data_embeddings, clust.centroid)
            if sim > closest[0]:
                closest = (sim, clust)
        return closest[1].name

    def predict(self, data: list[str]) -> list[str]:
        return list([self.predict_one(e) for e in data])

    def __call__(self, data: str) -> str:
        return self.predict([data])[0]
