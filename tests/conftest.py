import pytest
from brownie import (
  accounts,
  interface,
  ChadgerRegistry,
  MockPriceCalculator, 
  MockVault,
  OnChainPriceFetcher)

from config import *

@pytest.fixture
def deployer():
  return accounts[0]

@pytest.fixture
def user1():
  return accounts[1]

@pytest.fixture
def user2():
  return accounts[2]

@pytest.fixture
def keeper():
    return accounts[3]

@pytest.fixture
def guardian():
    return accounts[4]

@pytest.fixture
def treasury():
    return accounts[5]

@pytest.fixture
def badgerTree():
    return accounts[6]

@pytest.fixture
def stablecoin():
    return "0x04068DA6C83AFCFA0e13ba15A6696662335D5B75" # usdc (fantom)

@pytest.fixture
def vaultImplementation(deployer):
   vaultImplementation = MockVault.deploy({"from": deployer})
   return vaultImplementation

@pytest.fixture
def registry(deployer, vaultImplementation):
    registry = ChadgerRegistry.deploy({'from': deployer})
    priceCalculator = MockPriceCalculator.deploy({'from': deployer})
    registry.initialize(deployer, vaultImplementation.address, priceCalculator.address, {"from": deployer})
    yield registry


## Fund the account
@pytest.fixture
def token1(user1, user2):
    WANT = "0x658b0c7613e890EE50B8C4BC6A3f41ef411208aD" #feth (fantom)
    WHALE_ADDRESS = "0x10f9a2b600f169f2425f9f28e7ba39773d167f7b"
    token = interface.IERC20(WANT)
    whaleBalance = token.balanceOf(accounts.at(WHALE_ADDRESS, force=True))
    token.transfer(user1, whaleBalance / 2, {"from": WHALE_ADDRESS})
    token.transfer(user2, whaleBalance - token.balanceOf(user1), {"from": WHALE_ADDRESS})
    return token

@pytest.fixture
def token2(user1, user2):
    WETH = "0x21be370D5312f44cB42ce377BC9b8a0cEF1A4C83" # wftm (fantom)
    WHALE_ADDRESS = "0x51D493C9788F4b6F87EAe50F555DD671c4Cf653E"
    token = interface.IERC20(WETH)
    whaleBalance = token.balanceOf(accounts.at(WHALE_ADDRESS, force=True))
    token.transfer(user1, whaleBalance / 3, {"from": WHALE_ADDRESS})
    token.transfer(user2, whaleBalance / 3, {"from": WHALE_ADDRESS})
    return token

@pytest.fixture
def onchain_pricer(deployer, stablecoin):
  onchain_pricer = OnChainPriceFetcher.deploy(stablecoin, wftm, CURVE_ROUTER, SOLIDLY_ROUTER, SPOOKYSWAP_ROUTER, SUSHISWAP_ROUTER, {'from':deployer})
  return onchain_pricer

## Forces reset before each test
@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass
