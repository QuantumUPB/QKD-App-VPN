# This work has been implemented by Alin-Bogdan Popa and Bogdan-Calin Ciobanu,
# under the supervision of prof. Pantelimon George Popescu, within the Quantum
# Team in the Computer Science and Engineering department,Faculty of Automatic
# Control and Computers, National University of Science and Technology
# POLITEHNICA Bucharest (C) 2024. In any type of usage of this code or released
# software, this notice shall be preserved without any changes.

"""Command line interface for the Quantum VPN application."""

import json
import os
import subprocess
import sys
from importlib import import_module

import click


def _load_qkdgkt():
    """Dynamically import the qkdgkt module."""
    qkdgkt_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', 'QKD-Infra-GetKey')
    )
    if qkdgkt_path not in sys.path:
        sys.path.append(qkdgkt_path)
    try:
        return import_module('qkdgkt')
    except Exception as exc:  # pragma: no cover - import errors
        raise click.ClickException("qkdgkt module not found") from exc


def generate_wireguard_keys() -> tuple[str, str]:
    """Generate a WireGuard key pair."""
    private_key = subprocess.check_output(["wg", "genkey"]).strip()
    public_key = subprocess.check_output(["wg", "pubkey"], input=private_key).strip()
    private_key_str = private_key.decode("utf-8")
    public_key_str = public_key.decode("utf-8")
    click.echo(f"Public Key: {public_key_str}")
    return private_key_str, public_key_str


def acquire_qkd_key() -> tuple[str, str]:
    """Acquire a QKD key using the qkdgkt module."""
    qkdgkt = _load_qkdgkt()
    destinations = qkdgkt.get_destinations()
    destination = destinations[0] if destinations else None
    if destination is None:
        raise click.ClickException("No QKD destinations available")
    key_data = qkdgkt.get_key(destination)
    key_data = json.loads(key_data)
    key = key_data["keys"][0]["key"]
    key_id = key_data["keys"][0]["key_ID"]
    click.echo(f"QKD Key ID: {key_id}")
    return key, key_id


def acquire_peer_qkd_key(key_id: str) -> str:
    """Retrieve a QKD key for a peer based on its key id."""
    qkdgkt = _load_qkdgkt()
    destinations = qkdgkt.get_destinations()
    destination = destinations[0] if destinations else None
    if destination is None:
        raise click.ClickException("No QKD destinations available")
    key_data = qkdgkt.get_key_with_id(destination, key_id)
    key_data = json.loads(key_data)
    return key_data["keys"][0]["key"]


def generate_wg_config_client(
    private_key: str,
    qkd_key: str,
    server_public_key: str,
    server_ip: str,
    server_port: str,
    peer_ip: str,
    path: str,
) -> None:
    """Write the WireGuard client configuration to *path*."""
    config_data = f"""[Interface]
PrivateKey = {private_key}
Address = {peer_ip}/24

[Peer]
PublicKey = {server_public_key}
AllowedIPs = 0.0.0.0/0
Endpoint = {server_ip}:{server_port}
PresharedKey = {qkd_key}
"""
    with open(path, "w", encoding="utf-8") as file:
        file.write(config_data)
    click.echo(f"WireGuard client configuration written to {path}")


def generate_wg_config_server(
    private_key: str,
    server_ip: str,
    server_port: str,
    peers: list[dict],
    path: str,
) -> None:
    """Write the WireGuard server configuration to *path*."""
    config_data = f"""[Interface]
PrivateKey = {private_key}
ListenPort = {server_port}
Address = {server_ip}/24
"""
    for peer in peers:
        config_data += f"""
[Peer]
PublicKey = {peer['public_key']}
PresharedKey = {peer['qkd_key']}
AllowedIPs = {peer['ip']}/32
"""
    with open(path, "w", encoding="utf-8") as file:
        file.write(config_data)
    click.echo(f"WireGuard server configuration written to {path}")


def open_wireguard() -> None:
    """Open the WireGuard application."""
    subprocess.Popen(["wireguard.exe"])  # noqa: PLW1510


def launch_videocall() -> None:
    """Launch the Linphone videocall application."""
    subprocess.Popen(["C:\\Program Files\\Linphone\\bin\\linphone.exe"])  # noqa: PLW1510


@click.command()
@click.option(
    "role",
    "--role",
    type=click.Choice(["client", "server"]),
    prompt="Run as client or server",
    help="Run the application as a client or a server.",
)
def cli(role: str) -> None:
    """Run the Quantum VPN workflow from the command line."""
    private_key, public_key = generate_wireguard_keys()

    if role == "client":
        if click.confirm("Acquire QKD key automatically?", default=True):
            qkd_key, key_id = acquire_qkd_key()
            click.echo(f"QKD key acquired with ID: {key_id}")
        else:
            qkd_key = click.prompt("QKD key")
            key_id = click.prompt("QKD key ID")
            click.echo(f"QKD key provided with ID: {key_id}")
        server_public_key = click.prompt("Server public key")
        server_ip = click.prompt("Server IP")
        server_port = click.prompt("Server port")
        peer_ip = click.prompt("Peer IP")
        path = click.prompt(
            "Path to save client WireGuard config", default="wg_client.conf"
        )
        generate_wg_config_client(
            private_key,
            qkd_key,
            server_public_key,
            server_ip,
            server_port,
            peer_ip,
            path,
        )
        if click.confirm("Open WireGuard now?", default=False):
            open_wireguard()
        if click.confirm("Launch video call?", default=False):
            launch_videocall()
    else:
        peers: list[dict] = []
        while click.confirm("Add a peer?", default=not peers):
            peer_ip = click.prompt("Peer IP")
            peer_public_key = click.prompt("Peer public key")
            if click.confirm("Acquire peer QKD key automatically?", default=True):
                peer_qkd_key_id = click.prompt("Peer QKD key ID")
                peer_qkd_key = acquire_peer_qkd_key(peer_qkd_key_id)
                click.echo(
                    f"Peer QKD key acquired with ID: {peer_qkd_key_id}"
                )
            else:
                peer_qkd_key = click.prompt("Peer QKD key")
                peer_qkd_key_id = click.prompt("Peer QKD key ID")
                click.echo(
                    f"Peer QKD key provided with ID: {peer_qkd_key_id}"
                )
            peers.append(
                {
                    "ip": peer_ip,
                    "public_key": peer_public_key,
                    "qkd_key": peer_qkd_key,
                }
            )
        if len(peers) < 2:
            raise click.ClickException("At least two peers are required.")
        server_ip = click.prompt("Server internal IP")
        server_port = click.prompt("Server listen port")
        path = click.prompt(
            "Path to save server WireGuard config", default="wg_server.conf"
        )
        generate_wg_config_server(private_key, server_ip, server_port, peers, path)
        if click.confirm("Open WireGuard now?", default=False):
            open_wireguard()


if __name__ == "__main__":
    cli()
