// SPDX-License-Identifier: GPL-3.0
pragma solidity 0.6.12;
pragma experimental ABIEncoderV2;

import "../../interfaces/erc20/IERC20.sol";
import "../../interfaces/IPriceFeed.sol";
import "../../interfaces/routers/IBaseV1Router01.sol";
import "../../interfaces/routers/IUniv2LikeRouter01.sol";
import "../../interfaces/routers/ICurveRouter.sol";

/// @title Onchain pricer for calculating the price onchain of a token by taking the best from multipler routers
/// @author Modified from the work already done by @GalloDaSballo & @jack-the-pug
contract OnChainPriceFetcher is IPriceFeed {
    // Assumption #1 Most tokens liquid pair is WETH (WETH is tokenized ETH for that chain)
    // e.g on Fantom, WETH would be wFTM
    address public immutable WETH; // WFTM

    // Curve / Doesn't revert on failure
    address public immutable CURVE_ROUTER;
    address public immutable SOLIDLY_ROUTER;

    /// == Uni V2 Like Routers || These revert on non-existent pair == //
    address public immutable UNIV2_ROUTER_1; // Spookyswap
    address public immutable UNIV2_ROUTER_2; // Sushiswap

    // USD  (USDC / USDT / MIM / 3CRV)
    address public immutable QUOTE_USD_TOKEN;
    uint256 public immutable QUOTE_USD_DECIMAL;

    constructor(
        address _quote_usd_token,
        address _weth,
        address _curveRouter,
        address _solidlyRouter,
        address _uniRouter1,
        address _uniRouter2
    ) public {
        QUOTE_USD_TOKEN = _quote_usd_token;
        QUOTE_USD_DECIMAL = IERC20(_quote_usd_token).decimals();

        WETH = _weth;
        CURVE_ROUTER = _curveRouter;
        SOLIDLY_ROUTER = _solidlyRouter;
        UNIV2_ROUTER_1 = _uniRouter1;
        UNIV2_ROUTER_2 = _uniRouter2;
    }

    /// @notice public method to get the best onchain price of a token in terms of the quote_usd_token
    /// @param _token contract address of the token for which the price is to be calculated
    /// @return priceInUSD price of the _token in `QUOTE_USD_TOKEN` terms
    function getData(address _token)
        public
        view
        override
        returns (uint256 priceInUSD)
    {
        uint256 amount = 10**uint256(IERC20(_token).decimals()); // 1 unit of the token
        uint256 quote;

        // Check Solidly
        quote = getSolidlyQuote(_token, amount, QUOTE_USD_TOKEN);
        if (quote > priceInUSD) priceInUSD = quote;
        // Check Curve
        quote = getCurveQuote(_token, amount, QUOTE_USD_TOKEN);
        if (quote > priceInUSD) priceInUSD = quote;

        // uniswapv2s
        quote = getUniV2Quote(UNIV2_ROUTER_1, _token, QUOTE_USD_TOKEN, amount);
        if (quote > priceInUSD) priceInUSD = quote;

        quote = getUniV2Quote(UNIV2_ROUTER_2, _token, QUOTE_USD_TOKEN, amount);
        if (quote > priceInUSD) priceInUSD = quote;
    }

    /// @dev Given the address of the UniV2Like Router, the input amount, and the path, returns the quote for it
    function getUniV2Quote(
        address router,
        address tokenIn,
        address tokenOut,
        uint256 amountIn
    ) public view returns (uint256) {
        address[] memory path = new address[](3);
        path[0] = address(tokenIn);
        path[1] = WETH;
        path[2] = address(tokenOut);

        uint256 quote; //0

        // TODO: Consider doing check before revert to avoid paying extra gas
        // Specifically, test gas if we get revert vs if we check to avoid it
        try IUniv2LikeRouter01(router).getAmountsOut(amountIn, path) returns (
            uint256[] memory amounts
        ) {
            quote = amounts[amounts.length - 1]; // Last one is the outToken
        } catch (bytes memory) {
            // We ignore as it means it's zero
        }

        return _scalePriceTo1e18(quote);
    }

    /// @notice returns the solidly quote of fromToken in terms of toToken for given amount
    function getSolidlyQuote(
        address fromToken,
        uint256 amount,
        address toToken
    ) public view returns (uint256) {
        if (SOLIDLY_ROUTER == address(0)) return 0;

        (uint256 solidlyQuote, ) = IBaseV1Router01(SOLIDLY_ROUTER).getAmountOut(
            amount,
            fromToken,
            toToken
        );

        return _scalePriceTo1e18(solidlyQuote);
    }

    /// @notice returns the curve quote of fromToken in terms of toToken for given amount
    function getCurveQuote(
        address fromToken,
        uint256 amount,
        address toToken
    ) public view returns (uint256) {
        if (CURVE_ROUTER == address(0)) return 0;

        (, uint256 curveQuote) = ICurveRouter(CURVE_ROUTER).get_best_rate(
            fromToken,
            toToken,
            amount
        );

        return _scalePriceTo1e18(curveQuote);
    }

    /// @notice scales the given quote to 18 decimals
    function _scalePriceTo1e18(uint256 rawPrice)
        internal
        view
        returns (uint256)
    {
        if (QUOTE_USD_DECIMAL <= 18) {
            return rawPrice * (10**(18 - QUOTE_USD_DECIMAL));
        } else {
            return rawPrice / (10**(QUOTE_USD_DECIMAL - 18));
        }
    }
}
