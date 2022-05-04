import click
from brownie import (
                     MarketOracle, PriceCalculator, AdminUpgradeabilityProxy,  accounts, network, web3)

from config import *

def connect_account():
    click.echo(f"You are using the '{network.show_active()}' network")
    dev = accounts.load(click.prompt(
        "Account", type=click.Choice(accounts.load())))
    click.echo(f"You are using: 'dev' [{dev.address}]")
    return dev

def main():
    dev = connect_account()

    price_calculator = PriceCalculator.at("0xe11a79B9bE49402AB783e4DE57CE859f94AbAB78")

    price_calculator.addFeeds(
        [wftm, btc, avax, feth, link],
        [
            [ zero_address, "0x6a1122A449f3A4cB7203A49fa6Af32B97d329E73"],
            [ zero_address, "0x6a1122A449f3A4cB7203A49fa6Af32B97d329E73"],
            [ zero_address, "0x6a1122A449f3A4cB7203A49fa6Af32B97d329E73"],
            [ zero_address, "0x6a1122A449f3A4cB7203A49fa6Af32B97d329E73"],
            [ zero_address, "0x6a1122A449f3A4cB7203A49fa6Af32B97d329E73"],
        ], {"from": dev}
    )