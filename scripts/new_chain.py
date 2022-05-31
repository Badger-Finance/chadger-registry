import brownie
from brownie import *
"""
  Run this script on each chain, each time you want to deploy a new version of the registry
  NOTE: Use a new account each time to ensure nonce align getting you same destination address
"""

## Account that will set up vault later
GOVERNANCE = "0x283C857BA940A61828d9F4c09e3fceE2e7aEF3f7"

## Vault Contract
VAULT_LOGIC = "0x30319434Ea8F3CC1bD5c922Dec8938b27E301B82"

def main():
  dev = accounts.load("chadger") ## TODO: Change name based on account name

  ChadgerRegistry.deploy(GOVERNANCE, VAULT_LOGIC, {"from": dev})
