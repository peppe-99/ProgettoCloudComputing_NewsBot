import requests

from config import DefaultConfig


class ContactOCR:
    def __init__(self, default_config: DefaultConfig):
        self._default_config = default_config

    def send_request(self, image_data):
        OCR_URL = self._default_config.COMPUTER_VISION_URL + "vision/v3.1/ocr"
        headers = {
            'Ocp-Apim-Subscription-Key': self._default_config.COMPUTER_VISION_KEY,
            'Content-Type': 'application/octet-stream'
        }
        params = {'language': 'unk', 'detectOrientation': 'true'}
        response = requests.post(OCR_URL, headers=headers, params=params, data=image_data)
        response.raise_for_status()

        analysis = response.json()
        line_infos = [region["lines"] for region in analysis["regions"]]
        frase = ""
        for line in line_infos:
            for word_metadata in line:
                for word_info in word_metadata["words"]:
                    frase += f"{word_info['text']} "
        return frase
