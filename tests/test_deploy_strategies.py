from brownie import (
    accounts,
    interface,
    Contract,
    ChadgerRegistry
)
from config import *
from brownie import *


def test_deploy_strategies():
    registry = ChadgerRegistry.at("0x83980cADe75375A32196E7219F3e578BFBb8F6a6")
    gov = "0xFF352a9A13f333A1d193c2C3B68A16ed8535c8E2"

    # performanceFeeGovernance = 1000
    # performanceFeeStrategist = 1000
    # withdrawalFee = 50
    # managementFee = 50

    # feeConfig = [performanceFeeGovernance, performanceFeeStrategist, withdrawalFee, managementFee]

    # # deploy strategies
    # registry.registerVault(
    #     wftm,
    #     gov,
    #     gov,
    #     gov,
    #     gov,
    #     "Fantom WFTM Test 01",
    #     "FWT01",
    #     feeConfig,
    #     {"from": gov}
    # )

    vaults = registry.getStrategistVaults(gov)

    # vault = interface.IVault(vaults[0])

    print(vaults)

    print(registry.amountInUSD((wftm, 1e18)))



