// SPDX-License-Identifier: MIT
pragma solidity 0.6.12;
pragma experimental ABIEncoderV2;

import "@openzeppelin-contracts-upgradeable/proxy/Initializable.sol";
import "@openzeppelin/contracts/token/ERC20/SafeERC20.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/math/Math.sol";
import "@openzeppelin/contracts/math/SafeMath.sol";

import "../../interfaces/IPriceFeed.sol";

// ERRORS:
// 1. ER1 => Cannot be the zero address

/// @notice Primary contract to get the token price in USD
/// uses a combination of oracle & onchain pricing to calculate the token price
/// @dev the PriceFeed struct for the token must be updated beforehand using the addFeeds() method
contract PriceCalculator {
    using SafeMath for uint256;
    using SafeERC20 for IERC20;

    address public governance;

    modifier onlyGov() {
        require(msg.sender == governance, "!gov");
        _;
    }

    address public onChainFetcher;
    // tokenAddress => oracleAddress
    mapping(address => address) public oracles;

    function initialize(address _governance, address _onChainFetcher) external {
        require(governance == address(0), "initialized");
        require(_onChainFetcher != address(0), "ER1");
        governance = _governance;
        onChainFetcher = _onChainFetcher;
    }

    function setOnChainFetcher(address _onChainFetcher) external onlyGov {
        require(_onChainFetcher != address(0), "ER1");
        onChainFetcher = _onChainFetcher;
    }

    /// @notice add the oracle address for the token for better price calculation
    /// @dev the oracle address will be an instance of the MarketOracle.sol or OffChainPriceOracle.sol contract
    function addFeeds(address[] memory tokens, address[] memory oracleAddresses)
        external
        onlyGov
    {
        uint256 n = tokens.length;
        require(n == oracleAddresses.length, "bad_args");

        for (uint256 i = 0; i < n; ++i) {
            oracles[tokens[i]] = oracleAddresses[i];
        }
    }

    function oracleValueOf(
        address oracleAddress,
        address tokenAddress,
        uint256 amount
    ) internal view returns (uint256 valueInUSD) {
        uint256 price = IPriceFeed(oracleAddress).getData(tokenAddress);
        valueInUSD = price.mul(amount).div(
            10**uint256(ERC20(tokenAddress).decimals())
        );
    }

    function tokenPriceInUSD(address tokenAddress, uint256 amount)
        external
        view
        returns (uint256)
    {
        address oracle = oracles[tokenAddress];

        uint256 pairPrice = oracleValueOf(onChainFetcher, tokenAddress, amount);

        if (oracle == address(0)) {
            return pairPrice;
        } else {
            uint256 oraclePrice = oracleValueOf(oracle, tokenAddress, amount);

            return Math.min(oraclePrice, pairPrice);
        }
    }

    function transferGovernance(address _newGov) external onlyGov {
        require(_newGov != address(0), "governance cannot be 0 addr");
        governance = _newGov;
    }
}
