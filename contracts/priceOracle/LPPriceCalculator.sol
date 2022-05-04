// SPDX-License-Identifier: MIT
pragma solidity 0.6.12;
pragma experimental ABIEncoderV2;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/SafeERC20.sol";
import "@openzeppelin/contracts/math/Math.sol";
import "@openzeppelin/contracts/math/SafeMath.sol";
import "../libraries/HomoraMath.sol";
import "../../interfaces/routers/IUniv2LikePair.sol";
import "../../interfaces/IPriceCalculator.sol";
import "../../interfaces/IPriceFeed.sol";

/// @notice contract to get the price of a LP token in usd
/// mainly called by the PriceCalculator.sol contract to get the LP token price
contract LPPriceCalculator is IPriceFeed {
    using SafeMath for uint256;
    using HomoraMath for uint256;

    /// address of the PriceCalculator contract used to get the individual price of the underlying tokens for the lp
    address public immutable priceCalculatorAddress;

    constructor(address _priceCalculatorAddress) public {
        priceCalculatorAddress = _priceCalculatorAddress;
    }

    /// @notice called by the PriceCalculator.sol contract to get lp price in usd
    /// @param pair address of the lp token
    function getData(address pair) external view override returns (uint256) {
        address token0 = IUniv2LikePair(pair).token0();
        address token1 = IUniv2LikePair(pair).token1();
        uint256 totalSupply = IUniv2LikePair(pair).totalSupply();
        (uint256 r0, uint256 r1, ) = IUniv2LikePair(pair).getReserves();

        uint256 sqrtK = HomoraMath.sqrt(r0.mul(r1)).fdiv(totalSupply); // in 2**112
        uint256 px0 = IPriceCalculator(priceCalculatorAddress).tokenPriceInUSD(
            token0,
            1e18
        );
        uint256 px1 = IPriceCalculator(priceCalculatorAddress).tokenPriceInUSD(
            token1,
            1e18
        );
        uint256 fairPriceInUSD = sqrtK
            .mul(2)
            .mul(HomoraMath.sqrt(px0))
            .div(2**56)
            .mul(HomoraMath.sqrt(px1))
            .div(2**56);

        return fairPriceInUSD;
    }
}
