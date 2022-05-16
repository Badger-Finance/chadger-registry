import click
from brownie import (
                     ChadgerRegistry, DeterministicFactory, accounts, network, web3)

from config import *

def connect_account():
    click.echo(f"You are using the '{network.show_active()}' network")
    dev = accounts.load(click.prompt(
        "Account", type=click.Choice(accounts.load())))
    click.echo(f"You are using: 'dev' [{dev.address}]")
    return dev


def main():
    if click.confirm("Deploy New Registry"):
        dev = connect_account()

        vault_impl = "0xeCd8b51542CeE782d964bf25E2D0Ae1A99B2b96A"
        assert len(vault_impl) != 0

        deterministic_factory = "0xC497AD0000790cfE90F4aD107501eFE7c5762B36"
        assert len(deterministic_factory) != 0

        chadger_registry_logic = ""
        if len(chadger_registry_logic) == 0:
            # deploy the logic contract
            chadger_registry_logic = ChadgerRegistry.deploy({"from": dev}, publish_source=True)
        else:
            chadger_registry_logic = ChadgerRegistry.at(chadger_registry_logic)

        deterministic_factory = DeterministicFactory.at(deterministic_factory)

        args = [dev.address, vault_impl]
        data = chadger_registry_logic.initialize.encode_input(*args)
        salt = web3.keccak(text=chadger_registry_salt)
        # deterministic deploy chadger registry using factory
        deterministic_factory.deploy(salt, 0, chadger_registry_logic, "0xbf50C5ADBe89b8C61DF4e0D8aFC44CAF87343C00",data, {"from": dev} )