import argparse
from commands import CommandFactory


def main():
    parser = argparse.ArgumentParser(
        description="Revcontent Campaign API Integration\n\n"
                    "By default runs the campaign workflow. Use --test to run unit tests.",
        epilog="Example:\n"
               "  python main.py         # Run workflow\n"
               "  python main.py --test  # Run tests",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('--test', action='store_true', help='Run unit tests')
    args = parser.parse_args()
    command = CommandFactory.create_command(args)
    command.execute()


if __name__ == "__main__":
    main()
