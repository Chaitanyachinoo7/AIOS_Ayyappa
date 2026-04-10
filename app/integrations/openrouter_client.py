import requests

class OpenRouterClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = 'https://api.openrouter.com/v1/'

    def list_models(self):
        response = requests.get(self.base_url + 'models', headers=self._headers())
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def generate_response(self, model_name, prompt):
        data = {
            'model': model_name,
            'prompt': prompt
        }
        response = requests.post(self.base_url + 'generate', json=data, headers=self._headers())
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def stream_response(self, model_name, prompt):
        data = {
            'model': model_name,
            'prompt': prompt
        }
        response = requests.post(self.base_url + 'generate', json=data, headers=self._headers(), stream=True)
        if response.status_code == 200:
            for line in response.iter_lines():
                if line:
                    yield line.json()
        else:
            response.raise_for_status()

    def _headers(self):
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }