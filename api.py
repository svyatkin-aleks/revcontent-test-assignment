from dataclasses import dataclass
from typing import Optional, List
from errors import api_error_handler
from exceptions import (
    RevcontentAuthError,
    RevcontentCampaignError,
    RevcontentStatsError,
)


@dataclass
class CampaignInfo:
    id: str
    success: bool

    def __str__(self):
        return f"Campaign ID: {self.id}\nSuccess: {self.success}"


@dataclass
class CampaignStats:
    date: str
    impressions: int
    clicks: int

    def __str__(self):
        return f"Date: {self.date} Impressions: {self.impressions} Clicks: {self.clicks}\n"


class RevcontentAuthenticator:
    """
    Handles authentication with the Revcontent API and retrieves access tokens.
    """
    AUTH_URL = "https://api.revcontent.io/oauth/token"

    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret

    @api_error_handler(RevcontentAuthError)
    def get_token(self) -> Optional[str]:
        import requests
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        response = requests.post(self.AUTH_URL, data=data)
        response.raise_for_status()
        return response.json()["access_token"]


class RevcontentAPI:
    """
    Provides methods to interact with Revcontent Campaign and Stats API.
    """
    CAMPAIGN_URL = "https://api.revcontent.io/stats/api/v1.0/boosts/add"
    STATS_URL = "https://api.revcontent.io/stats/api/v1.0/boosts/performance"

    def __init__(self, access_token: str):
        self.headers = {"Authorization": f"Bearer {access_token}"}

    @api_error_handler(RevcontentCampaignError)
    def create_campaign(self, name: str, budget: float, bid: float, countries: List[str],
                        traffic_type: str) -> Optional[CampaignInfo]:
        import requests
        payload = {
            "name": name,
            "budget": budget,
            "bid_amount": bid,
            "country_targeting": "include",
            "country_codes": countries,
            # "traffic_type": traffic_type
        }
        response = requests.post(self.CAMPAIGN_URL, json=payload, headers=self.headers)
        response.raise_for_status()
        data = response.json()
        return CampaignInfo(id=data["campaign"]["id"], success=data["success"])

    @api_error_handler(RevcontentStatsError)
    def get_campaign_stats(self, campaign_id: str) -> List[CampaignStats]:
        import requests
        params = {"boost_id": campaign_id}
        response = requests.get(self.STATS_URL, params=params, headers=self.headers)
        response.raise_for_status()
        data = response.json()
        stats_list: List[CampaignStats] = []
        if data.get("success"):
            for stat in data.get("data", []):
                stats_list.append(
                    CampaignStats(
                        date=stat.get("date", ""),
                        impressions=int(float(stat.get("impressions", 0))),
                        clicks=int(float(stat.get("clicks", 0))),
                    )
                )
            return stats_list
        raise RevcontentStatsError(f"Failed to get stats: {data}")


class CampaignManager:
    """
    Manages the campaign creation and statistics retrieval workflow.
    """

    def __init__(self, api: RevcontentAPI):
        self.api = api
        self.campaign: Optional[CampaignInfo] = None
        self.stats: List[CampaignStats] = []

    def create_campaign(self, name: str, budget: float, bid: float, countries: List[str],
                        traffic_type: str) -> None:
        self.campaign = self.api.create_campaign(name, budget, bid, countries, traffic_type)
        print("Campaign created!\n" + str(self.campaign))

    def fetch_stats(self) -> None:
        if not self.campaign:
            raise ValueError("No campaign to fetch stats for.")
        self.stats = self.api.get_campaign_stats(self.campaign.id)

    def print_results(self) -> None:
        if self.campaign and self.stats:
            print("RESULTS:")
            print(self.campaign)
            for stat in self.stats:
                print(stat)

    def run(self):
        name = "Test Campaign - YourName"
        budget = 50.00
        bid = 0.10
        countries = ["US"]
        traffic_type = "click"
        self.create_campaign(name, budget, bid, countries, traffic_type)
        self.fetch_stats()
        self.print_results()
