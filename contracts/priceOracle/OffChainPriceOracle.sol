// SPDX-License-Identifier: MIT
pragma solidity 0.6.12;

import "@openzeppelin/contracts/access/Ownable.sol";
import "../../interfaces/IPriceFeed.sol";

/// @notice used by the PriceCalculator.sol file for offchain price feeds to get the price of a token
contract OffChainPriceOracle is Ownable, IPriceFeed {
    mapping(address => uint256) tokenPriceInUSD;

    /// @notice udpates the usd price for a token. only callable by owner
    /// @param token array containing the token addreses
    /// @param price array containing the usd price for each token
    function update(address[] memory token, uint256[] memory price)
        external
        onlyOwner
    {
        require(token.length == price.length);
        uint256 len = token.length;

        for (uint256 i = 0; i < len; ++i) {
            tokenPriceInUSD[token[i]] = price[i];
        }
    }

    /// @notice called by the PriceCalculator.sol contract to get the offchain price for a token
    /// @param token address of the token to get the usd price of
    function getData(address token) external view override returns (uint256) {
        return tokenPriceInUSD[token];
    }
}
