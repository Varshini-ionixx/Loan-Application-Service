import os

import httpx


class LoanApiClient:
    def __init__(self):
        self.http = httpx.Client(base_url=os.environ["LOAN_API_BASE_URL"], timeout=10)
        self.token = None

    def login(self):
        response = self.http.post(
            "/api/auth/login",
            data={
                "username": os.environ["LOAN_API_USERNAME"],
                "password": os.environ["LOAN_API_PASSWORD"],
            },
        )
        response.raise_for_status()
        self.token = response.json()["access_token"]

    def _get(self, path: str) -> httpx.Response:
        if self.token is None:
            self.login()
        response = self.http.get(path, headers={"Authorization": f"Bearer {self.token}"})
        if response.status_code == 401:
            self.login()
            response = self.http.get(path, headers={"Authorization": f"Bearer {self.token}"})
        return response

    def get_customer(self, customer_id: int) -> dict | None:
        response = self._get(f"/api/customers/{customer_id}")
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()
