import asyncio
from src.websocket_app.app import ws_app_main
from src.ws_clients.client import run_ssh_client
import argparse


# Press the green button in the gutter to run the script.


class GracefulExit(SystemExit):
    code = 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='main.py',
        description='Reverse SSH client and server',
        epilog='Reverse SHH client and server with websocket support',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-v', '--verbose', action='store_true')  # on/off flag
    parser.add_argument("app_type", choices=["ws_app_server", "ws_ssh_client", "ws_web_client"],
                        help="Application type to run")
    # parser.print_help()

    args = parser.parse_args()

    if args.app_type == "ws_app_server":
        try:
            asyncio.run(ws_app_main())
        except GracefulExit:
            pass
    elif args.app_type == "ws_ssh_client":
        try:
            asyncio.run(run_ssh_client())
        except GracefulExit:
            pass
    elif args.app_type == "ws_web_client":
        print("not definet yet")

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
