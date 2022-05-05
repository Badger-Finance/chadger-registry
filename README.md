# Chadger Registry

The Registry Contract for Chadger Experimental Vaults // By Chad Strategists, For Chad Badgers

Repo for the Web UI: https://github.com/jack-the-pug/chager-web-ui

Demo: https://chadger.devpug.xyz/

## Design Decisions for Offchain Pricer

1. for the uniswapv2 like router's pricing, jtp created a mapping to store the router address and the best path for that swap and the price only updateable by the owner. I find this process not scalable, specially for an application like chadger where strategists can create strategies with any token. I agree with Alex's assumption of the tokenout to be wETh (or wFtm, the native token of that chain) as the most liquid pair for most tokens. So in the pricer, the path will be token=>wETh=>stableCoin for any of the uniswapv2 like routers.

2. Another difficult choice was if to make the quote USD token (stablecoin) updateable for future proofing or not. I chose to not to, to keep the Pricer contract owner-free.

3. For the uniswapv2 like routers, we could either store them in an array and loop through them for optimum price calculation. But If we assume that each chain would have max 2 uniswapv2 like routers where more than 80% of the chain swap volume takes place, we can store them as constant(or immutable) variables and have price calculated for just those two. Also with the loop method, with each new router added, it also heavily adds to the gas costs for each price calculation. (The more routers we add, the more accurate is the price but higher the gas costs, fewer routers, less accurate price, lower gas costs). Did the gas tests later, and keeping the uniswap routers in an array takes 5921 more gas then keeping them in constants (for 2 uniswap routers), on calling the getData method (& 62410 gas on contract deployment)

4. wanted to do the tests against a chainlink oracle but couldnt find chainlink for fantom chain. Is there any?

## Info

Chadger, a fully decentralized Registry and Website,that allows new Strategists to easily deploy new Badger1.5 vaults and display them for apes to try.

### Pricing Mechanism

The Chadger Contract uses the tokenPriceInUSD() method in the PriceCalculator.sol to get the token price in USD.

The PriceCalculator uses a combination of oracle & onchain dex pricing to calculate the usd price for a token.

The contract owner can call the addFeeds() method to add a oracle address for a token. If both the provided then the contract will select the best price from both. If not provided, then the contract will just use the onChainPriceFetcher.

<strong>oracleAddress</strong>: This needs to be an implementation of either the "MarketOracle.sol" or the "OffChainPriceOracle.sol" contracts.

<strong>onChainFetcher</strong>: This needs to be an implementation of the "OnChainPriceFetcher.sol" file.
However if the token is an LP token this needs to be an implementation of the "LPPriceCalculator.sol" file.

All the above mentioned pricing files implement the IPriceFeed.sol interface, since the PriceCalculator.sol contract calls the getData() method for each to get the price.

## Setup

If the tests fail due to rpc issues on fantom chain change the rpc url for the ftm-main network to "https://rpc.ftm.tools/" using

```
  brownie networks modify ftm-main host=https://rpc.ftm.tools/
```

## Deployment Mechanism

The idea was to deploy the chadger registry at the same address on multiple chains. Now the most efficient way to achieve this is to use the CREATE2 opcode for
deterministic deployment of contracts. But one problem of this is, that the CREATE2 opcode needs to be called using a factory contract and if the address of that factory contract is different on different chains then the resulting address of the contract deployed using CREATE2 will also be different.

So the first step was to ofcourse deploy this factory on multiple chains with the same address, and then any user can use this factory to deploy chadger registry on that chain. But I thought, well if I am deploying the factory contract on multiple chains anyway why just make it compatible to deploy the ChadgerRegistry? Why not make it compatible to be used for deterministically deploying any contract?

Therefore, I added a [DeterministicFactory.sol](https://github.com/0xdhan/chadger-registry/blob/main/contracts/deployment/DeterministicFactory.sol) contract which deploys a proxy contract using CREATE2 opcode for any implementation contract. The implementation contract adddress is a param on the deploy method, so you can use this factory to deploy basically any contract. You can use the getDeployed() method to view in advance the address of the contract by just providing a salt. Keep the salt same on other chains and you will get the exact same contract address on multiple chains.

For the CREATE2 logic, we are using [CREATE3.sol](https://github.com/0xdhan/chadger-registry/blob/main/contracts/libraries/CREATE3.sol) library contract from the [solmate](https://github.com/Rari-Capital/solmate) repo but with a slight modification to work with solidity v0.6.12

We are using deterministic deploy factory to [deploy the ChadgerRegistry](https://github.com/0xdhan/chadger-registry/blob/main/scripts/deploy_chadger_registry.py) & [also the PriceCalculator contract](https://github.com/0xdhan/chadger-registry/blob/main/scripts/deploy_price_calculatory.py) at the same address on multiple chains.

## Deployments

1. <strong>Deterministic Factory</strong> (deployed at the same address on all chains) :

Chains deployed:

| Chain            |                                                         Address                                                          |
| ---------------- | :----------------------------------------------------------------------------------------------------------------------: |
| Fantom           |   [0xC497AD0000790cfE90F4aD107501eFE7c5762B36](https://ftmscan.com/address/0xC497AD0000790cfE90F4aD107501eFE7c5762B36)   |
| Polygon          | [0xC497AD0000790cfE90F4aD107501eFE7c5762B36](https://polygonscan.com/address/0xC497AD0000790cfE90F4aD107501eFE7c5762B36) |
| Bsc Mainnet      |   [0xC497AD0000790cfE90F4aD107501eFE7c5762B36](https://bscscan.com/address/0xC497AD0000790cfE90F4aD107501eFE7c5762B36)   |
| Arbitrum Mainnet |   [0xC497AD0000790cfE90F4aD107501eFE7c5762B36](https://arbiscan.io/address/0xC497AD0000790cfE90F4aD107501eFE7c5762B36)   |

2. <strong>Pricing Contracts</strong> (FTM Main)

| Contract              | Address                                                                                                              |
| --------------------- | -------------------------------------------------------------------------------------------------------------------- |
| MarketOracle          | [0x1e6485E6cff4777291e27c5b2653649A811E3c12](https://ftmscan.com/address/0x1e6485E6cff4777291e27c5b2653649A811E3c12) |
| OffChainPriceOracle   | [0xD94b716eF115b2BEaf988a0f7E9390C39459c572](https://ftmscan.com/address/0xD94b716eF115b2BEaf988a0f7E9390C39459c572) |
| OnChainPriceFetcher   | [0x6a1122A449f3A4cB7203A49fa6Af32B97d329E73](https://ftmscan.com/address/0x6a1122A449f3A4cB7203A49fa6Af32B97d329E73) |
| PriceCalculator Logic | [0xb9Ba04eEcAb6Bb6e2b18c3DC39fF58387ca4CadA](https://ftmscan.com/address/0xb9Ba04eEcAb6Bb6e2b18c3DC39fF58387ca4CadA) |
| PriceCalculator Proxy | [0x71c3BE0B98726318Fd6A3f0901e8d0B9a01fceEb](https://ftmscan.com/address/0x71c3BE0B98726318Fd6A3f0901e8d0B9a01fceEb) |
| LPPriceCalculator     | [0xC80755D8eCa309FD241621e86216bCb6cC6f5849](https://ftmscan.com/address/0xC80755D8eCa309FD241621e86216bCb6cC6f5849) |

3. <strong>Chadger Registry</strong> (FTM Main)

   | Contract               | Address                                                                                                              |
   | ---------------------- | -------------------------------------------------------------------------------------------------------------------- |
   | Chadger Registry Proxy | [0x70e7126140acB38E3943FE29B20C6C44c436A7D0](https://ftmscan.com/address/0x70e7126140acB38E3943FE29B20C6C44c436A7D0) |
   | Chadger Registry Logic | [0xe9559a6645aF7C3cE9D7925F9C73DA00FA1904B2](https://ftmscan.com/address/0xe9559a6645aF7C3cE9D7925F9C73DA00FA1904B2) |
   | Vault Logic            | [0xeCd8b51542CeE782d964bf25E2D0Ae1A99B2b96A](https://ftmscan.com/address/0xeCd8b51542CeE782d964bf25E2D0Ae1A99B2b96A) |
