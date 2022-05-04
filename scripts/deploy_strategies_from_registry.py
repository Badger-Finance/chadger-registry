import click
from brownie import (ChadgerRegistry, accounts, network, web3)

from config import *


def connect_account():
    click.echo(f"You are using the '{network.show_active()}' network")
    dev = accounts.load(click.prompt(
        "Account", type=click.Choice(accounts.load())))
    click.echo(f"You are using: 'dev' [{dev.address}]")
    return dev



def main():
    dev = connect_account()

    registry = ChadgerRegistry.at("0x83980cADe75375A32196E7219F3e578BFBb8F6a6")

    performanceFeeGovernance = 1000
    performanceFeeStrategist = 1000
    withdrawalFee = 50
    managementFee = 50

    feeConfig = [performanceFeeGovernance, performanceFeeStrategist, withdrawalFee, managementFee]

    for i in range(1,4):
        # deploy strategies
        registry.registerVault(
            wftm,
            dev,
            dev,
            dev,
            dev,
            f"Fantom WFTM Test 0{i}",
            f"FWT0{i}",
            feeConfig,
            {"from": dev}
        )
