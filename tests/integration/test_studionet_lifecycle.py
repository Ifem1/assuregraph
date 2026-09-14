"""Live Studionet lifecycle proof for AssureGraph.

Target network: stable Studionet only — https://studio.genlayer.com/api, chain ID 61999.
Fixture URLs are pinned to the immutable repository commit below.
"""

import json
import re

from gltest import get_contract_factory, get_default_account
from gltest.assertions import tx_execution_failed, tx_execution_succeeded
from gltest.utils import extract_contract_address


ASSUREGRAPH = "assuregraph.py"
ASSURANCE_GATE = "assurance_gate.py"
TX_KW = {"consensus_max_rotations": 3, "wait_interval": 10000, "wait_retries": 30}

FIXTURE_COMMIT = "a952b299019d3df75ff5fde2197f4450cf27d4e3"
RAW = f"https://raw.githubusercontent.com/Ifem1/assuregraph/{FIXTURE_COMMIT}/fixtures"
PREFIX = f"{RAW}/"
AUTH_URL = f"{RAW}/auth_pass.txt"
ROLLBACK_URL = f"{RAW}/rollback_pass.txt"
RUNBOOK_URL = f"{RAW}/runbook_pass.txt"


def assert_success(receipt):
    assert tx_execution_succeeded(receipt), receipt


def tx(function):
    return function.transact(**TX_KW)


def test_assurance_graph_and_cross_contract_gate_on_studionet():
    assert re.fullmatch(r"[0-9a-f]{40}", FIXTURE_COMMIT), "fixture commit must be immutable"

    account = get_default_account()
    primitive_factory = get_contract_factory(contract_file_path=ASSUREGRAPH)
    primitive_deploy = primitive_factory.deploy_contract_tx(account=account, **TX_KW)
    assert_success(primitive_deploy)
    primitive = primitive_factory.build_contract(
        contract_address=extract_contract_address(primitive_deploy), account=account
    )
    assert primitive.address

    case_create = tx(primitive.create_case(args=[
        "Production Release Assurance",
        "A reusable assurance case proving authentication, rollback and incident-readiness properties before a protected release action.",
    ]))
    assert_success(case_create)
    case_id = 1

    assert_success(tx(primitive.add_leaf(args=[
        case_id,
        "Authentication control",
        "Production authentication rejects invalid sessions and requires an approved credential.",
        "The source materially establishes that an invalid session was rejected and an approved credential was required.",
        PREFIX,
        86400,
    ])))
    auth = 1

    assert_success(tx(primitive.add_leaf(args=[
        case_id,
        "Rollback readiness",
        "The current release can be rolled back using the tested production procedure.",
        "The source materially establishes that the documented production rollback procedure completed successfully.",
        PREFIX,
        86400,
    ])))
    rollback = 2

    assert_success(tx(primitive.add_leaf(args=[
        case_id,
        "Incident readiness",
        "The incident runbook has been exercised for the current operational period.",
        "The source materially establishes that the incident-response runbook was exercised successfully.",
        PREFIX,
        86400,
    ])))
    runbook = 3

    assert_success(tx(primitive.add_threshold(args=[
        case_id,
        "Recovery assurance",
        "At least two recovery-readiness claims must currently hold.",
        2,
    ])))
    recovery = 4
    assert_success(tx(primitive.add_child(args=[recovery, rollback])))
    assert_success(tx(primitive.add_child(args=[recovery, runbook])))

    assert_success(tx(primitive.add_all(args=[
        case_id,
        "Release assurance",
        "Authentication assurance and recovery assurance must both hold before release execution.",
    ])))
    root = 5
    assert_success(tx(primitive.add_child(args=[root, auth])))
    assert_success(tx(primitive.add_child(args=[root, recovery])))
    assert_success(tx(primitive.set_root(args=[case_id, root])))
    case_seal = tx(primitive.seal_case(args=[case_id]))
    assert_success(case_seal)

    definition_hash = primitive.current_definition_hash(args=[case_id]).call()
    assert re.fullmatch(r"[0-9a-fA-F]{64}", definition_hash)
    assert primitive.get_case_status(args=[case_id]).call()["status_name"] == "INCOMPLETE"

    assessment_receipts = []
    for claim_id, url in (
        (auth, AUTH_URL),
        (rollback, ROLLBACK_URL),
        (runbook, RUNBOOK_URL),
    ):
        receipt = tx(primitive.assess_leaf(args=[claim_id, url]))
        assert_success(receipt)
        assessment_receipts.append(receipt)
        claim = primitive.get_claim(args=[claim_id]).call()
        assessment = primitive.get_assessment(args=[claim["current_assessment_id"]]).call()
        assert assessment["verdict_name"] == "PASS"
        assert assessment["evidence"]

    status = primitive.get_case_status(args=[case_id]).call()
    assert status["status_name"] == "ASSURED"
    assert primitive.is_assured(args=[case_id, definition_hash]).call() is True
    snapshot_receipt = tx(primitive.refresh_case(args=[case_id]))
    assert_success(snapshot_receipt)
    snapshot_hash = primitive.get_case(args=[case_id]).call()["snapshot_hash"]
    assert re.fullmatch(r"[0-9a-fA-F]{64}", snapshot_hash)

    gate_factory = get_contract_factory(contract_file_path=ASSURANCE_GATE)
    gate_deploy = gate_factory.deploy_contract_tx(
        args=[primitive.address], account=account, **TX_KW
    )
    assert_success(gate_deploy)
    gate = gate_factory.build_contract(
        contract_address=extract_contract_address(gate_deploy), account=account
    )
    assert gate.address

    good_action = "11" * 32
    allowed_action = tx(gate.execute(args=[case_id, definition_hash, good_action]))
    assert_success(allowed_action)
    assert gate.was_executed(args=[good_action]).call() is True

    replayed_action = tx(gate.execute(args=[case_id, definition_hash, good_action]))
    assert tx_execution_failed(replayed_action), replayed_action

    wrong_hash_action = "22" * 32
    denied = tx(gate.execute(args=[case_id, "00" * 32, wrong_hash_action]))
    assert tx_execution_failed(denied), denied
    assert gate.was_executed(args=[wrong_hash_action]).call() is False

    def tx_id(receipt):
        return receipt.get("tx_id") or receipt.get("hash")

    evidence = {
        "network": "studionet",
        "chain_id": 61999,
        "assuregraph_address": primitive.address,
        "assuregraph_deploy_tx": tx_id(primitive_deploy),
        "assurance_gate_address": gate.address,
        "assurance_gate_deploy_tx": tx_id(gate_deploy),
        "case_create_tx": tx_id(case_create),
        "case_seal_tx": tx_id(case_seal),
        "leaf_assessment_txs": [tx_id(receipt) for receipt in assessment_receipts],
        "snapshot_tx": tx_id(snapshot_receipt),
        "allowed_gate_tx": tx_id(allowed_action),
        "replay_rejected_tx": tx_id(replayed_action),
        "wrong_hash_rejected_tx": tx_id(denied),
        "definition_hash": definition_hash,
        "snapshot_hash": snapshot_hash,
        "root_status": status["status_name"],
    }
    print("STUDIONET_LIFECYCLE_EVIDENCE=" + json.dumps(evidence, sort_keys=True))
