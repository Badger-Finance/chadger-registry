from brownie import (
    accounts,
    interface,
    Contract
)
from config import *
from brownie import *


def test_pricing_logic(onchain_pricer, deployer):
    stableCoin =  interface.IERC20(onchain_pricer.QUOTE_USD_TOKEN())
    wftm = interface.IERC20(onchain_pricer.WETH())

    fBtc = interface.IERC20("0x321162Cd933E2Be498Cd2267a90534A804051b11")
    fEth = interface.IERC20("0x658b0c7613e890EE50B8C4BC6A3f41ef411208aD")
    link = interface.IERC20("0xb3654dc3D10Ea7645f8319668E8F54d2574FBdC8")
    mim = interface.IERC20("0x82f0B8B456c1A451378467398982d4834b6829c1")
    aave = interface.IERC20("0x6a07A792ab2965C72a5B8088d3a069A7aC3a993B")

    tokens = [fBtc, fEth, link, mim, aave]

    for i in range(len(tokens)):
        completeTest(onchain_pricer, stableCoin, tokens[i], wftm)

   

def completeTest(onchain_pricer, stableCoin, want, wftm):
    solidly_router = onchain_pricer.SOLIDLY_ROUTER()
    curve_router = onchain_pricer.CURVE_ROUTER()
    spookyswap_router = onchain_pricer.UNIV2_ROUTER_1()
    sushiswap_router = onchain_pricer.UNIV2_ROUTER_2()

    
    # test each individual quote methods for normal token one by one first
    uniswap_quote = uniswapV2QuoteTest(onchain_pricer, stableCoin, want, wftm, spookyswap_router)
    sushi_quote = uniswapV2QuoteTest(onchain_pricer, stableCoin, want, wftm, sushiswap_router)
    solidly_quote  =solidlyQuoteTest(onchain_pricer, stableCoin, want, solidly_router)
    curve_quote = curveQuoteTest(onchain_pricer, stableCoin, want, curve_router)

    quotes = [uniswap_quote, sushi_quote, solidly_quote, curve_quote]
    # test the optimal price code
    optimalPriceTest(onchain_pricer, want, quotes)
    
def optimalPriceTest(onchain_pricer, want, quotes):
    expected_optimal_quote = max(quotes)
    acutal_optimal_quote = onchain_pricer.getData(want)

    assert acutal_optimal_quote > 0

    assert (expected_optimal_quote == acutal_optimal_quote)


def scalePriceTo1e18(quote, decimals):
    if (decimals <= 18):
        return quote * (10** (18-decimals))
    else:
        return quote / (10**(decimals - 18)) 

def uniswapV2QuoteTest(onchain_pricer, stableCoin, want, wftm, router_address):
    if router_address != zero_address:
        router = interface.IUniv2LikeRouter01(router_address)
        amount = 10 ** want.decimals()
        path = [want, wftm, stableCoin]
        stableDecimals = stableCoin.decimals()

        try:
            expected_quotes = router.getAmountsOut(amount, path)
            expected_quote = scalePriceTo1e18(expected_quotes[-1], stableDecimals)
        except:
            expected_quote = 0
        actual_quote = onchain_pricer.getUniV2Quote(router_address, want, stableCoin, amount)

        assert (expected_quote == actual_quote)

        print("Uniswap Quote", actual_quote)
        return actual_quote

def solidlyQuoteTest(onchain_pricer, stableCoin, want, router):
    if (router != zero_address):
        router = interface.IBaseV1Router01(router)
        amount = 10 ** want.decimals()
        stableDecimals = stableCoin.decimals()

        expected_quote = router.getAmountOut(amount, want, stableCoin)[0]
        expected_quote = scalePriceTo1e18(expected_quote, stableDecimals)
        actual_quote = onchain_pricer.getSolidlyQuote(want,  amount, stableCoin)

        assert (expected_quote == actual_quote)

        print("Solidly Quote", actual_quote)

        return actual_quote

def curveQuoteTest(onchain_pricer, stableCoin, want, router):
    if (router != zero_address):
        router = interface.ICurveRouter(router)
        amount = 10 ** want.decimals()
        stableDecimals = stableCoin.decimals()

        expected_quote = router.get_best_rate(want, stableCoin, amount)[1]
        expected_quote = scalePriceTo1e18(expected_quote, stableDecimals)
        actual_quote = onchain_pricer.getCurveQuote(want, amount, stableCoin)

        assert (expected_quote == actual_quote)
        
        print("Curve Quote", actual_quote)

        return actual_quote