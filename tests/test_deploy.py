from brownie import (
    accounts,
    interface,
    Contract,
    DeterministicFactory,
    ChadgerRegistry,
    PriceCalculator,
    AdminUpgradeabilityProxy
)
from config import *
from brownie import *


def test_deploy():
    dev = accounts[0]
    print("Deployer", dev)

    # deploy the _logic contract
    chadger_impl = ChadgerRegistry.deploy({"from": dev})
    deploy_factory = DeterministicFactory.deploy({"from": dev})

    salt = web3.keccak(text="ChadgerRegistry v0.001")

    vaultImpl = "0x2fB8c7117851f5A9Fb9FDD9A3C66F3D01CaA1223"
    priceCalculator = "0x897F0e332f5e4EA581C60a6726831B89c5352A8f"

    # data, initialzer code for chadger
    args = [dev.address, vaultImpl, priceCalculator]
    data = chadger_impl.initialize.encode_input(*args)

    print(deploy_factory.getDeployed(salt))

    tx = deploy_factory.deploy(salt, 0, chadger_impl, dev, data, {"from": dev})

    chadger = ChadgerRegistry.at(tx.return_value)

    assert(chadger.governance() == dev)
    assert(chadger.priceCalculator() == priceCalculator)

    print("Chadger Registry deployed at", tx.return_value)

    # another test with pricecalculator

    priceCalculator_impl = PriceCalculator.deploy({"from": dev})
    salt = web3.keccak(text="PriceCalculator v0.001")
    data = priceCalculator_impl.initialize.encode_input(dev)
    tx = deploy_factory.deploy(salt, 0, priceCalculator_impl, dev, data, {"from": dev})

    pc = PriceCalculator.at(tx.return_value)

    assert(pc.governance() == dev)