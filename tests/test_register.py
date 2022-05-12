from time import time
from brownie import (
    interface,
    MockStrategy,
    chain,
)

from pytest import approx


def test_user_can_register_vault(user2, registry, user1, token1, token2, keeper, guardian, treasury, badgerTree):
    performanceFeeGovernance = 0
    performanceFeeStrategist = 0
    withdrawalFee = 0
    managementFee = 0
    tx = registry.registerVault(
        token1,
        keeper,
        guardian,
        treasury,
        badgerTree,
        "Vault",
        "VAULT",
        [
            performanceFeeGovernance,
            performanceFeeStrategist,
            withdrawalFee,
            managementFee,
        ], {"from": user1}
    )

    strategists = registry.getStrategists()
    assert len(strategists) == 1
    assert strategists[0] == user1
    event = tx.events["NewVault"][0]
    assert event["author"] == user1
    
    user1Vaults = registry.getStrategistVaults(user1)
    assert len(user1Vaults) == 1
    user1Vault = interface.IVault(user1Vaults[0])
    assert user1Vault.strategist() == user1
    assert user1Vault.governance() == user1

    strategy = MockStrategy.deploy({"from": user1})
    strategy.setTestRewardToken(token2, {"from": user1})
    user1Vault.setStrategy(strategy, {"from": user1})
    strategy.initialize(user1Vault, token1, user1, {"from": user1})
    user1Deposits = 10 * 1e18
    user2Deposits =8 * 1e18
    token1.approve(user1Vault.address, user1Deposits, {"from": user1})
    user1Vault.deposit(user1Deposits, {"from": user1})
    token1.approve(user1Vault.address, user2Deposits, {"from": user2})
    user1Vault.deposit(user2Deposits, {"from": user2})

    
    chain.sleep(10000)
    chain.mine()

    tx = strategy.harvest({"from": user1})
    yields = tx.return_value
    # harvest amounts were hard coded in `MockStrategy.harvest`
    assert yields[0][0] == token1
    assert yields[0][1] == 2 * 10**18
    assert yields[1][0] == token2
    assert yields[1][1] == 1 * 10**18
    
    t1 = 2 * 86400
    chain.sleep(t1)
    chain.mine()

    (vaultAddr, strategist, strategyAddr, name, version, tokenAddress, tokenName, _performanceFeeGovernance, _performanceFeeStrategist,
     _withdrawalFee, _managementFee, lastHarvestedAt, tvl, actualExpectedYields) = registry.getVaultData(user1Vault, yields)
    
    expectedYieldToken1 = yields[0][1] * ((365 * 86400) / t1)
    expectedYieldToken2 = yields[1][1] * ((365 * 86400) / t1)

    assert actualExpectedYields[0][0] == token1
    assert approx(actualExpectedYields[0][1], expectedYieldToken1)
    assert actualExpectedYields[1][0] == token2
    assert approx(actualExpectedYields[1][1], expectedYieldToken2)

    assert strategist == user1
    assert strategyAddr == strategy.address
    assert name == "Vault"
    assert version == "1.5"
    assert tokenName == "fETH"
    assert vaultAddr == user1Vault.address
    assert tvl == user1Deposits + user2Deposits
    assert tokenAddress == token1

    deposits = registry.getVaultDepositorData(user1Vault, user1)
    assert deposits == user1Deposits
    deposits = registry.getVaultDepositorData(user1Vault, user2)
    assert deposits == user2Deposits