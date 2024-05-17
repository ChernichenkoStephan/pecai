from . import links


class Tagger(links.BaseLink):
    def __call__(self, *args) -> str:
        text = args[0]
        entities = args[1]

        pairs = []
        for entity in entities:
            word = text[entity.start : entity.stop]
            tag = f"<{entity.type_}>{entity.identity}<{entity.type_}>"
            pairs.append((word, tag))

        for p in pairs:
            text = text.replace(p[0], p[1])
        return text
