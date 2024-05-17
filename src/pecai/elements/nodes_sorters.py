from . import log
from . import links

logger = log.getLogger(__name__)

default_config = {
    "raw": {
        "biased_rating": 100,
        "fill_score": 10,
        "review_count": 30,  # 20
        # 'worktime_is_24x7': 10, #5
        "is_accessable": 15,  # 5
        "is_modern": 10,  # 5
        "has_wifi": 15,  # 5
        "has_music": 5,
        "contact_social_len": 3,
        "phone_len": 2,
        "photos_len": 5,
        "has_website": 5,
    },
    "meta": {
        "category_weights": {
            "food": 7,
            "services": 6,
            "religious": 5,
            "shopping": 4,
            "recreation": 3,
            "entertainment": 2,
            "sports": 1,
        },
        "category": 10,
        "distance": 50,
    },
}


def opt_print(v, must):
    if must:
        logger.debug(v)


class RelevanceSorter(links.BaseLink):
    def __init__(self, config=None):
        self.config = config if config else default_config

    def get_score(self, node, verbose=False):
        score = 0.0

        # считаем по прямым фичам в форе
        for param_name, weight in self.config["raw"].items():
            opt_print(f"{param_name} {node[param_name] * weight}", verbose)
            score += node[param_name] * weight
        opt_print(f"raw {score=}", verbose)

        # считаем оценку с учетом цели поездки
        category_score = self.config["meta"]["category_weights"][node["category"]] / 7
        category_score *= self.config["meta"]["category"]
        opt_print(f"{category_score=}", verbose)

        # итоговая оценка это оценка "прямых" фич, расстояния и веса категории
        return sum([score, category_score])

    def select(self, nodes: list[dict]):
        nodes = map(
            lambda n: {
                "score": self.get_score(n),
                **n,
            },
            nodes,
        )
        return sorted(nodes, reverse=True, key=lambda n: n["score"])

    def __call__(self, nodes: list[dict]):
        return self.select(nodes)
