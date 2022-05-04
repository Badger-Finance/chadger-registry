from brownie import (
    accounts,
    interface,
    Contract,
    PriceCalculator,
    OnChainPriceFetcher
)
from config import *
from brownie import *
import brownie

def test_price_calc(deployer):
    dev = deployer
    quote_usd_token = "0x04068DA6C83AFCFA0e13ba15A6696662335D5B75" #usdc ftm
    # deploy pricing calculator
    pricingCalculator = PriceCalculator.deploy({"from": dev})

    pricingCalculator.initialize(dev, "0x6a1122A449f3A4cB7203A49fa6Af32B97d329E73", {"from": dev})

    price = pricingCalculator.tokenPriceInUSD(wftm, 1e18)
    price = price / 1e18
    # price of ftm $0.8 currently
    assert price > 0
    assert price < 10