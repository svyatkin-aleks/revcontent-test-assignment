import unittest
from unittest import mock
from api import RevcontentAuthenticator, RevcontentAPI, CampaignInfo, CampaignStats
from exceptions import (
    RevcontentAuthError,
    RevcontentCampaignError,
    RevcontentStatsError,
)


class TestRevcontentAPI(unittest.TestCase):
    @mock.patch("requests.post")
    def test_auth_success(self, mock_post: mock.Mock) -> None:
        mock_post.return_value = mock.Mock(
            status_code=200, json=lambda: {"access_token": "mock_token"}
        )
        authenticator = RevcontentAuthenticator("id", "secret")
        token = authenticator.get_token()
        print(f"Auth token: {token}")
        self.assertEqual(token, "mock_token")

    @mock.patch("requests.post")
    def test_auth_failure(self, mock_post: mock.Mock) -> None:
        mock_post.side_effect = Exception("Auth failed!")
        authenticator = RevcontentAuthenticator("id", "secret")
        with self.assertRaises(RevcontentAuthError):
            authenticator.get_token()
        print("Auth failure correctly raised RevcontentAuthError.")

    @mock.patch("requests.post")
    def test_create_campaign_success(self, mock_post: mock.Mock) -> None:
        mock_id = 12345
        mock_post.return_value = mock.Mock(
            status_code=200, json=lambda: {'success': True, 'campaign': {'id': mock_id}}
        )
        api = RevcontentAPI("mock_token")
        info = api.create_campaign("Test", 50, 0.1, ["US"], "click")
        print(f"Campaign ID: {info.id}, Success: {info.success}")

        self.assertIsInstance(info, CampaignInfo)
        self.assertEqual(info.id, mock_id)
        self.assertEqual(info.success, True)

    @mock.patch("requests.post")
    def test_create_campaign_failure(self, mock_post: mock.Mock) -> None:
        mock_post.side_effect = Exception("API error!")
        api = RevcontentAPI("mock_token")
        with self.assertRaises(RevcontentCampaignError):
            api.create_campaign("n", 50, 0.1, ["US"], "click")
        print("Campaign creation failure correctly raised RevcontentCampaignError.")

    @mock.patch("requests.get")
    def test_get_stats_success(self, mock_get: mock.Mock) -> None:
        mock_get.return_value = mock.Mock(
            status_code=200, json=lambda: {
                "success": True,
                "data": [
                    {
                        "date": "2016-03-01",
                        "impressions": "2615",
                        "clicks": "6",
                    },
                    {
                        "date": "2016-03-02",
                        "impressions": "5031",
                        "clicks": "36",
                    }, ]}
        )
        api = RevcontentAPI("mock_token")
        stats = api.get_campaign_stats("12345")

        for stat in stats:
            print(stat)
            self.assertIsInstance(stat, CampaignStats)

    @mock.patch("requests.get")
    def test_get_stats_failure(self, mock_get: mock.Mock) -> None:
        mock_get.side_effect = Exception("API error!")
        api = RevcontentAPI("mock_token")
        with self.assertRaises(RevcontentStatsError):
            api.get_campaign_stats("12345")
        print("Stats fetching failure correctly raised RevcontentStatsError.")

    @mock.patch("requests.post")
    @mock.patch("requests.get")
    def test_full_workflow_output(
            self,
            mock_get: mock.Mock,
            mock_post: mock.Mock
    ) -> None:
        mock_post.side_effect = [
            mock.Mock(status_code=200, json=lambda: {"access_token": "mock_token"}),
            mock.Mock(status_code=200, json=lambda: {
                "success": True,
                "campaign": {
                    "id": 12345,
                }
            })
        ]
        mock_get.return_value = mock.Mock(
            status_code=200, json=lambda: {
                "success": True,
                "data": [
                    {
                        "date": "2016-03-01",
                        "impressions": "2615",
                        "clicks": "6",
                    },
                    {
                        "date": "2016-03-02",
                        "impressions": "5031",
                        "clicks": "36",
                    }, ]}
        )

        authenticator = RevcontentAuthenticator("id", "secret")
        token = authenticator.get_token()
        api = RevcontentAPI(token)
        campaign_info = api.create_campaign("Test Campaign - UnitTest", 50, 0.1, ["US"], "click")
        stats = api.get_campaign_stats(campaign_info.id)

        self.assertIsInstance(campaign_info, CampaignInfo)
        print(campaign_info)

        for stat in stats:
            print(stat)
            self.assertIsInstance(stat, CampaignStats)
