import os
import csv
import ast
import yaml
from langchain.chat_models import ChatOpenAI
from langchain.prompts import BasePromptTemplate
from langchain.prompts import load_prompt
from openai.error import InvalidRequestError

from tenacity import retry, RetryError
from tenacity import stop_after_attempt, retry_if_exception_type, wait_fixed


class AITemplateResolver:
    class NotExpectedResponse(Exception):
        """Raised when a response is not as expected"""

        pass

    class NotExpectedResponseValue(Exception):
        pass

    def __init__(self) -> None:
        self.openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
        self.chat_model = ChatOpenAI(openai_api_key=self.openai_api_key)
        self.prompts_dir: str = os.getenv("PROMPTS_TEMPLATES_PATH", "app/prompts")
        self.template_extension: str = ".yaml"
        self.retry_attempt_qty: int = 7
        self.wait_after_attempt: int = 5

    def _get_all_templates(self) -> list:
        yaml_files = []
        for filename in os.listdir(self.prompts_dir):
            if filename.endswith(self.template_extension):
                yaml_files.append(os.path.splitext(filename)[0])
        return yaml_files

    def _get_prompt_template_path(self, template_name: str) -> str:
        file_path = os.path.join(
            self.prompts_dir, template_name + self.template_extension
        )
        if not os.path.isfile(file_path):
            raise FileNotFoundError(
                "Prompt template not found: {}".format(template_name)
            )
        return file_path

    def _get_template(self, template_name: str) -> BasePromptTemplate:
        template = load_prompt(self._get_prompt_template_path(template_name))
        return template

    def _shrink_prompt(self, prompt_text: str) -> str:
        prompt_text = (
            prompt_text.strip().replace("\n", "").replace("\t", "").replace("  ", "")
        )
        return prompt_text

    def _load_template_from_file(self, template_name: str) -> dict:
        template = self._get_prompt_template_path(template_name)
        with open(template, "r") as template_file:
            data = yaml.safe_load(template_file)
        return data

    def _ensure_all_variables_are_set(
        self, template_name: str, variables_key="input_variables", **kwargs
    ) -> bool:
        input_variables = set(kwargs)
        template_variables = self._load_template_from_file(template_name)[variables_key]
        missing_variables = input_variables - kwargs.keys()

        if missing_variables:
            raise ValueError(
                f"The following input variables are missing: {missing_variables}"
            )

        return True

    @retry(
        stop=stop_after_attempt(7),
        wait=wait_fixed(5),
        retry=retry_if_exception_type(
            (NotExpectedResponse, NotExpectedResponseValue, ValueError, SyntaxError)
        ),
    )
    def openai_get_response(self, template: str, **kwargs) -> dict:
        ensure_variables = self._ensure_all_variables_are_set(template)
        prompt = self._get_template(template).format(**kwargs)
        response = self.chat_model.predict(prompt)

        try:
            response = self.chat_model.predict(prompt)
        except InvalidRequestError:
            raise InvalidRequestError

        try:
            converted_dict = ast.literal_eval(response)
            if not isinstance(converted_dict, dict):
                raise self.NotExpectedResponse("The result is not a dictionary")

            for key, value in converted_dict.items():
                if value == 0:
                    raise self.NotExpectedResponseValue(
                        f"The value for {key} is 0. Response: {response}"
                    )

            return converted_dict

        except (
            self.NotExpectedResponse,
            self.NotExpectedResponseValue,
            ValueError,
            SyntaxError,
        ) as e:
            raise e
        except RetryError as e:
            raise e


if __name__ == "__main__":
    ai = AITemplateResolver()
    print(ai.openai_get_response("invest", ticker="ALALA", days=3, csv_data="no data"))
