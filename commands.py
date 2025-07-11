import os
from dotenv import load_dotenv
from api import RevcontentAuthenticator, RevcontentAPI, CampaignManager
from exceptions import RevcontentError


class ICommand:
    """
    Interface for commands.
    """

    def execute(self):
        raise NotImplementedError


class RunWorkflowCommand(ICommand):
    """
    Command to execute the campaign creation and stats workflow.
    """

    def show_welcome(self):
        print("=" * 60)
        print("Revcontent Campaign API Integration")
        print("By default: creates a campaign and fetches stats.")
        print("Use --test argument to run unit tests instead.")
        print("For help: python main.py --help")
        print("=" * 60)
        print()

    def execute(self):
        self.show_welcome()
        load_dotenv()
        client_id = os.getenv("CLIENT_ID")
        client_secret = os.getenv("CLIENT_SECRET")

        if not client_id or not client_secret:
            print(
                "CLIENT_ID or CLIENT_SECRET not set! Please create a .env file with these variables.")
            print("Example .env content:")
            print("CLIENT_ID=your_real_client_id")
            print("CLIENT_SECRET=your_real_client_secret")
            return

        try:
            authenticator = RevcontentAuthenticator(client_id, client_secret)
            access_token = authenticator.get_token()
            api = RevcontentAPI(access_token)
            manager = CampaignManager(api)
            manager.run()
        except RevcontentError as e:
            print(e)
        except Exception as e:
            print("[Fatal error]", e)


class RunTestsCommand(ICommand):
    """
    Command to run unit tests.
    """

    def execute(self):
        import unittest
        import tests  # Required for test discovery
        unittest.main(module='tests', argv=['first-arg-is-ignored'], exit=False)


class CommandFactory:
    """
    Factory to create command instances based on arguments.
    """

    @staticmethod
    def create_command(args) -> ICommand:
        if args.test:
            return RunTestsCommand()
        return RunWorkflowCommand()
