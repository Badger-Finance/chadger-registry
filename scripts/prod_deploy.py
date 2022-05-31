from brownie import *
import time

sleep_between_tx = 1

"""
  Prod Deployment of Chadger Registry for a new Chain
  NOTE: Use once per chain on the same address to get deterministic results
"""

def main():
  dev = accounts.load("deterministic")

  factory = DeterministicFactory.deploy({"from": dev})
  time.sleep(sleep_between_tx)
  DeterministicFactory.publish_source(factory)


  hash = 'chad'.encode('utf-8')

  logic = ChadgerRegistry.deploy({"from": dev})
  time.sleep(sleep_between_tx)
  ChadgerRegistry.publish_source(logic)


  vault_logic = MockVault.deploy({"from": dev})
  time.sleep(sleep_between_tx)
  MockVault.publish_source(vault_logic)


  args = [dev.address, vault_logic.address]

  tx = factory.deploy(hash, 0, logic, dev, logic.initialize.encode_input(*args), {"from": dev})
  time.sleep(sleep_between_tx)

  print("Deployed at: " + tx.events["NewContractDeployed"]["proxy"])
