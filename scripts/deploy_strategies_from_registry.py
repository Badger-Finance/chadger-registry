import click
from brownie import (ChadgerRegistry, accounts, network, web3, MockStrategy, MockVault)

from config import *


def connect_account():
    click.echo(f"You are using the '{network.show_active()}' network")
    dev = accounts.load(click.prompt(
        "Account", type=click.Choice(accounts.load())))
    click.echo(f"You are using: 'dev' [{dev.address}]")
    return dev



def main():
    dev = connect_account()

    # registry = ChadgerRegistry.at("0x0B5CB2aED6d52171222cb6Ef078148714C712776")

    # performanceFeeGovernance = 1000
    # performanceFeeStrategist = 1000
    # withdrawalFee = 50
    # managementFee = 50

    # feeConfig = [performanceFeeGovernance, performanceFeeStrategist, withdrawalFee, managementFee]

    # for i in range(1,4):
    #     # deploy strategies
    #     registry.registerVault(
    #         wftm,
    #         dev,
    #         dev,
    #         dev,
    #         dev,
    #         f"Fantom WFTM Test 0{i}",
    #         f"FWT0{i}",
    #         feeConfig,
    #         {"from": dev}
    #     )

    vaults = [
        # "0x44C75432817dD8ef862443005344b408e3cF06e2", 
        # "0xf47f45E320F089696fDE87888Dd60454533A24E0", 
        "0x2661C12bBC67cd8aAB0fb79246528DC6B6c8bC2f"]

    usdc = "0x04068DA6C83AFCFA0e13ba15A6696662335D5B75"

    for v in vaults:
        vault = MockVault.at(v)
        # strategy = MockStrategy.deploy({"from": dev})
        strategy = MockStrategy.at("0xa8C35031339006dBc2AE23f09CA65530b4F4e6a3")
        strategy.setTestRewardToken(usdc, {"from": dev})
        vault.setStrategy(strategy, {"from": dev})
        strategy.initialize(vault, wftm, dev, {"from": dev})
