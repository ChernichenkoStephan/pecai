from . import links


class Printer(links.BaseLink):
    def _parse_unsupported(self, vals: dict) -> str:
        return ""

    def _print_place(self, vals: dict) -> str:
        return f"{vals['title']}, находится по адресу: {vals['address']} \n"

    def _print_doc(self, vals: dict) -> str:
        text = vals["text"]
        if len(text) > 2000:
            text = ""
        return f"{vals['title']}\n{text}"

    def _print_span(self, vals: dict) -> str:
        return f"{vals['text']}"

    def __call__(self, vals: dict) -> str:
        resp = ""
        for ent in vals:
            match ent:
                case {"address": _}:
                    resp += self._print_place(ent)
                case {"link": _}:
                    resp += self._print_doc(ent)
                case {"text": _}:
                    resp += self._print_span(ent)
                case _:
                    resp += self._parse_unsupported(ent)
        return resp
