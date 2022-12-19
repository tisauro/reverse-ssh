import asyncio
from src.websocket_app.app import ws_app_main
from src.ws_clients.client import run_ssh_client, SSHClientConnectionDetails
import argparse
import os


# Press the green button in the gutter to run the script.


class GracefulExit(SystemExit):
    code = 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='Reverse SSH',
        description='Reverse SSH client and server suite',
        epilog='Reverse SHH client and server with websocket support',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-v', '--verbose', action='store_true')  # on/off flag
    parser.add_argument("app_type", choices=["ws_app_server", "ws_ssh_client", "ws_web_client"],
                        help="Application type to run")

    parser.add_argument("ssh_ip_address", help="IP address off the remote ssh server")
    parser.add_argument("ssh_username", help="User name for the remote ssh server")
    parser.add_argument("ssh_password", help="Password the remote ssh server")
    parser.add_argument("ssh_port", help="Port the remote ssh server", default=22)

    parser.add_argument("ws_url", help="Websocket server url", default="ws://localhost")
    parser.add_argument("ws_port", help="Websocket server port", default=8001)
    parser.add_argument("device_uuid", help="Device Unique Identifier", default="random_uuid")

    args = parser.parse_args()

    if args.app_type == "ws_app_server":
        try:
            asyncio.run(ws_app_main())
        except GracefulExit:
            pass
    elif args.app_type == "ws_ssh_client":

        if args.ssh_ip_address is None or args.ssh_username is None or args.ssh_password is None:
            parser.error('ssh_ip_address, ssh_username and ssh_password are required')

        SSH_IP_ADDRESS = os.environ.get('SSH_IP_ADDRESS')
        SSH_USERNAME = os.environ.get('SSH_USERNAME')
        SSH_PASSWORD = os.environ.get('SSH_PASSWORD')

        conn_details = SSHClientConnectionDetails(
            ssh_ip_address=args.ssh_ip_address,
            ssh_username=args.ssh_username,
            ssh_password=args.ssh_password,
            ssh_port=args.ssh_port,
            ws_url=args.ws_url,
            ws_port=args.ws_port,
            device_uui=args.device_uuid,
        )

        try:
            asyncio.run(run_ssh_client(conn_details))
        except GracefulExit:
            pass
    elif args.app_type == "ws_web_client":
        print("not definet yet")

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
