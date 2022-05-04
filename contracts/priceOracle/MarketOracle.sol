// SPDX-License-Identifier: MIT
pragma solidity 0.6.12;
pragma experimental ABIEncoderV2;

import "../../interfaces/erc20/IERC20.sol";
import "../../interfaces/IMarketOracle.sol";

import "../libraries/UniswapV2OracleLibrary.sol";
import "../libraries/access/AccessControl.sol";

/// @notice contract to get the price of a token in USD using UniswapV2 oracle
/// mainly used by the PriceCalculator contract
contract MarketOracle is IMarketOracle, AccessControl {
    using FixedPoint for FixedPoint.uq112x112;
    using FixedPoint for FixedPoint.uq144x112;

    struct TokenPrice {
        uint256 price0CumulativeLast;
        uint256 price1CumulativeLast;
        uint256 tokenValueInUSDAverage;
        uint32 timestampLast;
    }

    bytes32 public constant CONFIGURATOR_ROLE = keccak256("CONFIGURATOR_ROLE");
    bytes32 public constant KEEPER_ROLE = keccak256("KEEPER_ROLE");

    // USD  (USDC / MIM / 3CRV)
    address public immutable QUOTE_USD_TOKEN;
    uint256 public immutable QUOTE_USD_DECIMAL;

    mapping(address => TokenPrice) public priceList;
    mapping(address => IUniv2LikePair) public tokenLP;

    address public controller;

    constructor(address _QUOTE_USD_TOKEN) public {
        QUOTE_USD_TOKEN = _QUOTE_USD_TOKEN;
        QUOTE_USD_DECIMAL = IERC20(_QUOTE_USD_TOKEN).decimals();
        _setupRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _setupRole(CONFIGURATOR_ROLE, msg.sender);
        _setupRole(KEEPER_ROLE, msg.sender);
    }

    function _setTokenLP(address _token, address _tokenLP) private {
        tokenLP[_token] = IUniv2LikePair(_tokenLP);
        require(
            tokenLP[_token].token0() == QUOTE_USD_TOKEN ||
                tokenLP[_token].token1() == QUOTE_USD_TOKEN,
            "no_usd_token"
        );

        uint256 price0CumulativeLast = tokenLP[_token].price0CumulativeLast();
        uint256 price1CumulativeLast = tokenLP[_token].price1CumulativeLast();

        (, , uint32 timestampLast) = tokenLP[_token].getReserves();

        delete priceList[_token]; // reset
        TokenPrice storage tokenPriceInfo = priceList[_token];

        tokenPriceInfo.timestampLast = timestampLast;
        tokenPriceInfo.price0CumulativeLast = price0CumulativeLast;
        tokenPriceInfo.price1CumulativeLast = price1CumulativeLast;
        tokenPriceInfo.tokenValueInUSDAverage = 0;

        _update(_token);
    }

    /// @notice set the lp/pair address of the token for Token/QUOTE_USD_Token Liquidity pool on UniswapV2
    function setTokenLP(address[] memory tokenLPPairs)
        external
        onlyRole(CONFIGURATOR_ROLE)
    {
        require(tokenLPPairs.length % 2 == 0);
        uint256 length = tokenLPPairs.length;
        for (uint256 i = 0; i < length; i = i + 2) {
            _setTokenLP(tokenLPPairs[i], tokenLPPairs[i + 1]);
        }
    }

    function getTokenPrice(address tokenAddress)
        public
        view
        returns (
            uint256,
            uint256,
            uint32,
            uint256
        )
    {
        (
            uint256 price0Cumulative,
            uint256 price1Cumulative,
            uint32 _blockTimestamp
        ) = UniswapV2OracleLibrary.currentCumulativePrices(
                address(tokenLP[tokenAddress])
            );
        if (_blockTimestamp == priceList[tokenAddress].timestampLast) {
            return (
                priceList[tokenAddress].price0CumulativeLast,
                priceList[tokenAddress].price1CumulativeLast,
                priceList[tokenAddress].timestampLast,
                priceList[tokenAddress].tokenValueInUSDAverage
            );
        }

        uint32 timeElapsed = (_blockTimestamp -
            priceList[tokenAddress].timestampLast);

        FixedPoint.uq112x112 memory tokenValueInUSDAverage = tokenLP[
            tokenAddress
        ].token1() == QUOTE_USD_TOKEN
            ? FixedPoint.uq112x112(
                uint224(
                    (1e18 *
                        (price0Cumulative -
                            priceList[tokenAddress].price0CumulativeLast)) /
                        timeElapsed
                )
            )
            : FixedPoint.uq112x112(
                uint224(
                    (1e18 *
                        (price1Cumulative -
                            priceList[tokenAddress].price1CumulativeLast)) /
                        timeElapsed
                )
            );

        return (
            price0Cumulative,
            price1Cumulative,
            _blockTimestamp,
            tokenValueInUSDAverage.mul(1).decode144()
        );
    }

    function _update(address tokenAddress) private {
        (
            uint256 price0CumulativeLast,
            uint256 price1CumulativeLast,
            uint32 timestampLast,
            uint256 tokenValueInUSDAverage
        ) = getTokenPrice(tokenAddress);

        TokenPrice storage tokenPriceInfo = priceList[tokenAddress];

        tokenPriceInfo.timestampLast = timestampLast;
        tokenPriceInfo.price0CumulativeLast = price0CumulativeLast;
        tokenPriceInfo.price1CumulativeLast = price1CumulativeLast;
        tokenPriceInfo.tokenValueInUSDAverage = tokenValueInUSDAverage;
    }

    function scalePriceTo1e18(uint256 rawPrice)
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

    // Update "last" state variables to current values
    function update(address[] memory tokenAddress)
        external
        onlyRole(KEEPER_ROLE)
    {
        uint256 length = tokenAddress.length;
        for (uint256 i = 0; i < length; ++i) {
            _update(tokenAddress[i]);
        }
    }

    /// @notice Return the average usd price (1e18) since last update
    /// @param tokenAddress address of the token to get the price for
    /// @dev the LP address for the token must be updated using setTokenLP() method
    function getData(address tokenAddress)
        external
        view
        override
        returns (uint256)
    {
        (, , , uint256 tokenValueInUSDAverage) = getTokenPrice(tokenAddress);
        return scalePriceTo1e18(tokenValueInUSDAverage);
    }
}
