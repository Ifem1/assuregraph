"""Live Studionet lifecycle proof for AssureGraph.

Target network: stable Studionet only — https://studio.genlayer.com/api, chain ID 61999.

Before the final submission, replace FIXTURE_COMMIT_PLACEHOLDER with the immutable
commit SHA that contains the four files under fixtures/. This prevents validators
from reading mutable main-branch evidence.
"""

from gltest import get_contract_factory, get_default_account
from gltest.assertions import tx_execution_failed, tx_execution_succeeded


ASSUREGRAPH = "assuregraph.py"
ASSURANCE_GATE = "assurance_gate.py"
TX_KW = {"consensus_max_rotations": 3, "wait_interval": 10000, "wait_retries": 30}

FIXTURE_COMMIT = "FIXTURE_COMMIT_PLACEHOLDER"
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
    assert FIXTURE_COMMIT != "FIXTURE_COMMIT_PLACEHOLDER", (
        "pin the fixture commit before running the live Studionet test"
    )

    account = get_default_account()
    primitive_factory = get_contract_factory(contract_file_path=ASSUREGRAPH)
    primitive = primitive_factory.deploy(account=account, **TX_KW)
    assert primitive.address

    assert_success(tx(primitive.create_case(args=[
        "Production Release Assurance",
        "A reusable assurance case proving authentication, rollback and incident-readiness properties before a protected release action.",
    ])))
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
    assert_success(tx(primitive.seal_case(args=[case_id])))

    definition_hash = primitive.current_definition_hash(args=[case_id]).call()
    assert len(definition_hash) == 64
    assert primitive.get_case_status(args=[case_id]).call()["status_name"] == "INCOMPLETE"

    for claim_id, url in (
        (auth, AUTH_URL),
        (rollback, ROLLBACK_URL),
        (runbook, RUNBOOK_URL),
    ):
        receipt = tx(primitive.assess_leaf(args=[claim_id, url]))
        assert_success(receipt)
        claim = primitive.get_claim(args=[claim_id]).call()
        assessment = primitive.get_assessment(args=[claim["current_assessment_id"]]).call()
        assert assessment["verdict_name"] == "PASS"
        assert assessment["evidence"]

    status = primitive.get_case_status(args=[case_id]).call()
    assert status["status_name"] == "ASSURED"
    assert primitive.is_assured(args=[case_id, definition_hash]).call() is True
    assert_success(tx(primitive.refresh_case(args=[case_id])))
    assert len(primitive.get_case(args=[case_id]).call()["snapshot_hash"]) == 64

    gate_factory = get_contract_factory(contract_file_path=ASSURANCE_GATE)
    gate = gate_factory.deploy(args=[primitive.address], account=account, **TX_KW)
    assert gate.address

    good_action = "11" * 32
    assert_success(tx(gate.execute(args=[case_id, definition_hash, good_action])))
    assert gate.was_executed(args=[good_action]).call() is True

    wrong_hash_action = "22" * 32
    denied = tx(gate.execute(args=[case_id, "00" * 32, wrong_hash_action]))
    assert tx_execution_failed(denied), denied
    assert gate.was_executed(args=[wrong_hash_action]).call() is False
