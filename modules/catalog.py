import datetime

import requests
from argo_probe_onboarding.exceptions import CriticalException


def get_today():
    return datetime.datetime.now()


class CatalogAPI:
    def __init__(self, url, catalog_id, timeout):
        self.url = url
        self.catalog_id = catalog_id
        self.timeout = timeout
        self.data = self._get_data()

    def _get_data(self):
        if self.url.endswith("/"):
            url = f"{self.url}{self.catalog_id}"

        else:
            url = f"{self.url}/{self.catalog_id}"

        try:
            response = requests.get(url, timeout=self.timeout)

            response.raise_for_status()

            if response.ok:
                return response.json()

        except (
            requests.exceptions.HTTPError,
            requests.exceptions.ConnectionError,
            requests.exceptions.RequestException,
            requests.exceptions.Timeout,
            requests.exceptions.TooManyRedirects
        ) as e:
            raise CriticalException(e)

    def check_key_exists(self, key):
        return key in self.data and self.data[key]

    def check_url_valid(self, key):
        try:
            response = requests.get(self.data[key])
            response.raise_for_status()

            if response.ok:
                return True

        except (
                requests.exceptions.HTTPError,
                requests.exceptions.ConnectionError,
                requests.exceptions.RequestException,
                requests.exceptions.Timeout,
                requests.exceptions.TooManyRedirects
        ) as e:
            raise CriticalException(f"URL {self.data[key]} not valid: {str(e)}")

    def check_date_age(self, key, date_format):
        def age_month(d):
            today = get_today()
            return (today.year - d.year) * 12 + today.month - d.month

        datetime_object = datetime.datetime.strptime(
            self.data[key], date_format
        )

        return age_month(datetime_object)
