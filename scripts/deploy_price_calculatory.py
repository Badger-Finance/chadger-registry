# deploy instances of all pricing contracts
# deploy proxy for PriceCalculator.sol

import click
from brownie import (LPPriceCalculator, MarketOracle, OffChainPriceOracle, OnChainPriceFetcher,
                      PriceCalculator, DeterministicFactory, accounts, network, web3)

from config import *


def connect_account():
    click.echo(f"You are using the '{network.show_active()}' network")
    dev = accounts.load(click.prompt(
        "Account", type=click.Choice(accounts.load())))
    click.echo(f"You are using: 'dev' [{dev.address}]")
    return dev



def main():
    dev = connect_account()

    # for the fantom chain
    pricing_calculator_impl = ""
    deterministic_factory = "0xC497AD0000790cfE90F4aD107501eFE7c5762B36"
    assert len(deterministic_factory) != 0
    quote_usd_token = "0x04068DA6C83AFCFA0e13ba15A6696662335D5B75" #usdc ftm
    assert len(quote_usd_token) != 0

    # marketOracle = MarketOracle.deploy(quote_usd_token, {"from":dev}, publish_source=True)
    # print("MarketOracle deployed at", marketOracle.address)

    # offChainPriceOracle = OffChainPriceOracle.deploy({"from":dev}, publish_source=True)
    # print("OffChainPriceOracle deployed at", offChainPriceOracle.address)

    # onChainPriceFetcher = OnChainPriceFetcher.deploy(quote_usd_token, wftm, CURVE_ROUTER, SOLIDLY_ROUTER, SPOOKYSWAP_ROUTER, SUSHISWAP_ROUTER, {'from': dev}, publish_source=True)
    # print("OnChainPriceFetcher deployed at", onChainPriceFetcher.address)

    deterministic_factory = DeterministicFactory.at(deterministic_factory)

    if len(pricing_calculator_impl) == 0:
        # then deploy the Pricing Calculator impl
        pricing_calculator_impl = PriceCalculator.deploy({"from":dev})
        print("Pricing Calculator Impl deployed at", pricing_calculator_impl.address)
    else:
        pricing_calculator_impl = PriceCalculator.at(pricing_calculator_impl)

    salt = web3.keccak(text=pricing_calculator_salt)
    data = pricing_calculator_impl.initialize.encode_input(dev, "0x6a1122A449f3A4cB7203A49fa6Af32B97d329E73")
    tx = deterministic_factory.deploy(salt, 0, pricing_calculator_impl, "0xbf50C5ADBe89b8C61DF4e0D8aFC44CAF87343C00", data, {"from": dev})

    # print("Pricing Calculator Proxy deployed at", tx.return_value)

    # LPPriceCalculator.deploy(tx.return_value, {"from": dev}, publish_source=True)