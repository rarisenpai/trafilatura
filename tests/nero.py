import logging
from typing import Any, List
import requests
logger = logging.getLogger(__name__)

class NeroExtractLoader():

    def __init__(
        self, api_token: str, org_uuid: str, plain_text: str,url: str
    ):
        """Initialize with API token and other args

        Args:
            api_token: Nerobot API token.
            urls: List of URLs to load.
        """
        self.api_token = api_token
        self.org_uuid = org_uuid
        self.url = url
        self.plain_text = plain_text

    def _nerobot_api_url(self) -> str:
        return "https://api.nero.ai/v1/extract/data"

    def _get_nerobot_results(self) -> Any:
        payload = {
            "plain_text": str(self.plain_text),
            "url": self.url,
            }
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
            "org_uuid": self.org_uuid,
            }
        nerobot_url = self._nerobot_api_url()
        response = requests.post(nerobot_url, json=payload, headers=headers)
        return response.json() if response.ok else response.raise_for_status() 

    def extract(self):
        try:
            data = self._get_nerobot_results()
        except Exception as e:
            logger.error(f"Error fetching or processing, exception: {e}")
            data = ''
        return data