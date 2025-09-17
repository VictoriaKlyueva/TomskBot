import jwt
import requests
import time

from logger import logger, log_model_interaction
from constants import *
from validator.heuristic_validator import HeuristicValidator
from validator.yandex_gpt_validator import YandexGPTValidator
from validator.constants import *


class YandexGPTBot:
    def __init__(self):
        self.iam_token = None
        self.token_expires = 0
        self.heuristic_validator = HeuristicValidator()
        self.yandex_gpt_validator = YandexGPTValidator()

    def get_iam_token(self):
        """Получение IAM-токена (с кэшированием на 1 час)"""
        if self.iam_token and time.time() < self.token_expires:
            return self.iam_token

        try:
            now = int(time.time())
            payload = {
                'aud': GET_IAM_REQUEST,
                'iss': SERVICE_ACCOUNT_ID,
                'iat': now,
                'exp': now + 3600
            }

            encoded_token = jwt.encode(
                payload,
                PRIVATE_KEY,
                algorithm='PS256',
                headers={'kid': KEY_ID}
            )

            response = requests.post(
                GET_IAM_REQUEST,
                json={'jwt': encoded_token},
                timeout=10
            )

            if response.status_code != 200:
                raise Exception(f"Ошибка генерации токена: {response.text}")

            token_data = response.json()
            self.iam_token = token_data['iamToken']
            self.token_expires = now + 3500  # На 100 секунд меньше срока действия

            logger.info("IAM token generated successfully")
            return self.iam_token

        except Exception as e:
            logger.error(f"Error generating IAM token: {str(e)}")
            raise

    def ask_gpt(self, question):
        """Запрос к Yandex GPT API"""

        # Validation
        is_blocked_heuristic = self.heuristic_validator.detect_injection(question)
        is_blocked_by_model = not self.yandex_gpt_validator.validate(question, is_blocked_heuristic)['is_valid']
        logger.info(is_blocked_by_model)
        
        if is_blocked_by_model:
            # Logging
            logger.info(f"prompt={question}, response={None}, blocked={False}")
            log_model_interaction(
                tg_nickname="unknown",
                prompt=question,
                response="",
                blocked=True
            )

            return MOCK_RESPONSE

        try:
            iam_token = self.get_iam_token()

            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {iam_token}',
                'x-folder-id': FOLDER_ID
            }

            data = {
                "modelUri": MODEL_URI,
                "completionOptions": {
                    "stream": False,
                    "temperature": TEMPERATURE,
                    "maxTokens": MAX_TOKENS
                },
                "messages": [
                    {
                        "role": "system",
                        "text": SYSTEM_PROMPT
                    },
                    {
                        "role": "user",
                        "text": question
                    }
                ]
            }

            response = requests.post(
                GENERATE_REQUEST,
                headers=headers,
                json=data,
                timeout=30
            )

            if response.status_code != 200:
                logger.error(f"Yandex GPT API error: {response.text}")
                raise Exception(f"Ошибка API: {response.status_code}")

            result = response.json()['result']['alternatives'][0]['message']['text']

            # Logging
            logger.info(f"prompt={question}, response={result}, blocked={False}")
            log_model_interaction(
                tg_nickname="unknown",
                prompt=question,
                response=result,
                blocked=False
            )

            return result

        except Exception as e:
            logger.error(f"Error in ask_gpt: {str(e)}")
            raise

