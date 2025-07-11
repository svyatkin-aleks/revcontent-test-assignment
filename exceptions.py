class RevcontentError(Exception):
    """Base exception for all Revcontent API errors."""

    def __init__(self, message="Revcontent API error"):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return f"[RevcontentError] {self.message}"


class RevcontentAuthError(RevcontentError):
    """Raised for authentication errors."""

    def __str__(self):
        return f"[AuthError] {self.message}"


class RevcontentCampaignError(RevcontentError):
    """Raised for campaign creation errors."""

    def __str__(self):
        return f"[CampaignError] {self.message}"


class RevcontentStatsError(RevcontentError):
    """Raised for stats fetching errors."""

    def __str__(self):
        return f"[StatsError] {self.message}"
