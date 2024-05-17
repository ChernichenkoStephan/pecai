import requests
import time
import jwt
import json
import typing

from langchain_core.language_models.llms import LLM
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from pydantic import BaseModel, Field
from langchain_core.callbacks.manager import CallbackManagerForLLMRun

from pecai.elements import log

logger = log.getLogger(__name__)


def light_model_url(folder_id):
    return f"gpt://{folder_id}/yandexgpt-lite/latest"


def big_model_url(folder_id):
    return f"gpt://{folder_id}/yandexgpt/latest"


def summary_model_url(folder_id):
    return f"gpt://{folder_id}/summarization/latest"


class Base(BaseModel):
    class Config:
        populate_by_name = True
        protected_namespaces = ()


class Message(Base):
    role: str
    text: str


class CompletionOptions(Base):
    stream: bool
    temperature: float
    max_tokens: str = Field(alias="maxTokens")


class RequestBody(Base):
    model_uri: str = Field(alias="modelUri")
    completion_options: CompletionOptions = Field(alias="completionOptions")
    messages: typing.List[Message]


class Alternative(Base):
    message: Message
    status: str


class Usage(Base):
    input_text_tokens: str = Field(alias="inputTextTokens")
    completion_tokens: str = Field(alias="completionTokens")
    totalTokens: str


class Result(Base):
    alternatives: typing.List[Alternative]
    usage: Usage
    model_version: str = Field(alias="modelVersion")


class ResponseBody(Base):
    result: Result


class YaGPTAPI:
    """https://cloud.yandex.com/en/docs/yandexgpt/quickstart#api_1"""

    bad_response_text: str = "Сервис временно не доступен"

    def __init__(
        self,
        folder_id,
        service_account_id,
        key_file,
        iam_token="",
        iam_token_expires_at=0,
    ):
        self.__folder_id = folder_id
        self.__service_account_id = service_account_id
        self.__key_file = key_file
        self.__iam_token_expires_at = (
            time.time() - 10 if iam_token_expires_at == 0 else iam_token_expires_at
        )
        self.__iam_token = iam_token

    def refresh_iam_token(self):
        now = time.time()
        exp = (now) + (60 * 60)

        if self.__iam_token_expires_at > now:
            return

        key = {}
        with open(self.__key_file, "r") as f:
            key = json.loads(f.read())
        key_id = key["id"]
        private_key = key["private_key"]

        payload = {
            "aud": "https://iam.api.cloud.yandex.net/iam/v1/tokens",
            "iss": self.__service_account_id,
            "iat": now,
            "exp": exp,
        }
        encoded_token = jwt.encode(
            payload, private_key, algorithm="PS256", headers={"kid": key_id}
        )

        response = requests.post(
            "https://iam.api.cloud.yandex.net/iam/v1/tokens",
            headers={"Content-Type": "application/json; charset=utf-8"},
            data=json.dumps(
                {
                    "jwt": encoded_token,
                }
            ),
        )

        if response.status_code == 200:
            self.__iam_token_expires_at = now
            self.__iam_token = response.json()["iamToken"]
        else:
            logger.error(f"Error. code: {response.status_code} text: {response.text}")
            return

    def _post(self, url, modelUri, messages, stream, temperature):
        self.refresh_iam_token()
        if self.__iam_token == "":
            raise Exception("Bad IAM Token update")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.__iam_token}",
            "x-folder-id": self.__folder_id,
        }
        request_body = RequestBody(
            model_uri=modelUri,
            completion_options=CompletionOptions(
                stream=stream, temperature=temperature, max_tokens="2000"
            ),
            messages=messages,
        )

        response = requests.post(
            url,
            headers=headers,
            data=request_body.model_dump_json(by_alias=True).encode("utf-8"),
        )
        time.sleep(1)
        if response.status_code == 200:
            return ResponseBody.parse_raw(response.text)
        else:
            raise Exception(f"[{response.status_code}] {response.text}")

    def light(self, messages: typing.List[Message], stream=False, temperature=0.6):
        return self._post(
            "https://llm.api.cloud.yandex.net/foundationModels/v1/completion",
            light_model_url(self.__folder_id),
            messages,
            stream,
            temperature,
        )

    def big(self, messages: typing.List[Message], stream=False, temperature=0.6):
        return self._post(
            "https://llm.api.cloud.yandex.net/foundationModels/v1/completion",
            big_model_url(self.__folder_id),
            messages,
            stream,
            temperature,
        )

    def summarize(self, messages: typing.List[Message], stream=False, temperature=0.6):
        return self._post(
            "https://llm.api.cloud.yandex.net/foundationModels/v1/completion",
            summary_model_url(self.__folder_id),
            messages,
            stream,
            temperature,
        )


class YaLLM(LLM):
    api: YaGPTAPI
    model_type: str = "BIG"

    @property
    def _llm_type(self) -> str:
        return "custom"

    def _call(
        self,
        prompt: str,
        stop: typing.Optional[typing.List[str]] = None,
        run_manager: typing.Optional[CallbackManagerForLLMRun] = None,
        **kwargs: typing.Any,
    ) -> str:
        if stop is not None:
            raise ValueError("stop kwargs are not permitted.")
        logger.info(prompt)

        messages = [
            Message(role="system", text="You are professional data analyst"),
            Message(role="user", text=prompt),
        ]
        resp = None
        match self.model_type:
            case "BIG":
                resp = self.api.big(messages)
            case "SUMMARY":
                resp = self.api.summarize(messages)
            case _:
                resp = self.api.light(messages)
        model_resp = "\n".join(
            [alternative.message.text for alternative in resp.result.alternatives]
        )
        logger.info(model_resp)
        return model_resp

    @property
    def _identifying_params(self) -> typing.Mapping[str, typing.Any]:
        """Get the identifying parameters."""
        return {
            "api": self.api,
            "model_type": self.model_type,
        }


if __name__ == "__main__":
    api = YaGPTAPI(
        folder_id="FOLDER_ID",
        service_account_id="ajemmjvk65g0fn6cacg1",
        key_file="./sa4pecai-key.json",
    )

    resp = api.big(
        [
            Message(role="system", text="You are data analyst"),
            Message(role="user", text="tell me a joke"),
        ]
    )
    print(resp)

    time.sleep(1)

    yallm = YaLLM(api=api)

    template = "What is the capital of {country}?"
    prompt = PromptTemplate.from_template(template)
    llm_chain = LLMChain(prompt=prompt, llm=yallm)
    country = "Russia"
    print(llm_chain.invoke(country))
