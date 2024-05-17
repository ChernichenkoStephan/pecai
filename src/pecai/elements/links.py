class BaseLink:
    def __call__(self, params):
        return params

    def __or__(self, params):
        return self(params)

    def __ror__(self, params):
        return self(params)


class LimitSelector:
    def __init__(self, limit: int):
        self._limit = limit

    def __call__(self, nodes):
        return nodes[: self._limit]


class Getter(BaseLink):
    def __init__(self, getter=None):
        self.target = None
        self.getter = getter

    def __call__(self, params):
        if not self.target:
            return self.getter(params)
        return self.target(self.getter(params))

    def __or__(self, target):
        self.target = target
        return self


class Map(BaseLink):
    def __init__(self, key, runnable):
        self.runnable = runnable
        self.key = key

    def __call__(self, params):
        params[self.key] = self.runnable(params[self.key])
        return params


class OptionalMap:
    def __init__(self, key, runnable, criteria):
        self.key = key
        self.runnable = runnable
        self.criteria = criteria

    def __call__(self, params):
        if self.criteria(params):
            return self.runnable(params)
        return params[self.key]


class DoNothing(BaseLink):
    def __call__(self, params):
        return params
