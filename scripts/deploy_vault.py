import click
from brownie import (MockVault, MockStrategy, accounts, network, web3, interface)

from config import *


def connect_account():
    click.echo(f"You are using the '{network.show_active()}' network")
    dev = accounts.load(click.prompt(
        "Account", type=click.Choice(accounts.load())))
    click.echo(f"You are using: 'dev' [{dev.address}]")
    return dev



def main():
    dev = connect_account()

    # vault_impl = MockVault.deploy({"from": dev}, publish_source=True)
    vaults = ['0x7835ac81B1d6B90b0f19479bd561c19A8Aa490E9', '0xe1AeB5F4916579136f358469e909bE21EF4dcBD6', '0xAf8bdD7eBf2e3B7E7d641aE025e41EBFCa94DDdC']

    for v in vaults:
        vault = interface.IVault(v)

        # deploy mock strategy
        strategy = MockStrategy.deploy({"from": dev})
        strategy.setTestRewardToken(btc, {"from": dev})
        
        vault.setStrategy(strategy, {"from": dev})
        strategy.initialize(vault, wftm, dev, {"from": dev})