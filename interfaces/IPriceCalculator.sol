// SPDX-License-Identifier: MIT
pragma solidity >=0.6.12;

interface IPriceCalculator {
    function tokenPriceInUSD(address tokenAddress, uint256 amount)
        external
        view
        returns (uint256);
}
