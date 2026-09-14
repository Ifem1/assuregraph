# v0.1.0
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

from genlayer import *

import typing
from dataclasses import dataclass


@gl.contract_interface
class IAssureGraph:
    class View:
        def is_assured(self, case_id: u256, expected_definition_hash: str) -> bool: ...
        def current_definition_hash(self, case_id: u256) -> str: ...

    class Write:
        pass


@allow_storage
@dataclass
class GateReceipt:
    caller: Address
    case_id: u256
    definition_hash: str
    action_hash: str


class AssuranceGate(gl.Contract):
    """Minimal consumer proving live IC-to-IC reuse of AssureGraph assurance."""

    assuregraph_address: Address
    executions: TreeMap[str, GateReceipt]
    execution_count: u256

    def __init__(self, assuregraph_address: Address):
        self.assuregraph_address = assuregraph_address
        self.execution_count = u256(0)

    @gl.public.write
    def execute(
        self,
        case_id: u256,
        expected_definition_hash: str,
        action_hash: str,
    ) -> None:
        definition_hash = str(expected_definition_hash).strip().lower()
        action = str(action_hash).strip().lower()

        for value, label in ((definition_hash, "definition_hash"), (action, "action_hash")):
            if len(value) != 64:
                raise gl.vm.UserError(f"EXPECTED: {label} must be a 32-byte lowercase hex digest")
            for char in value:
                if char not in "0123456789abcdef":
                    raise gl.vm.UserError(f"EXPECTED: {label} must be lowercase hex")

        if action in self.executions:
            raise gl.vm.UserError("EXPECTED: action was already executed")

        primitive = IAssureGraph(self.assuregraph_address)
        if not primitive.view().is_assured(case_id, definition_hash):
            raise gl.vm.UserError("EXPECTED: assurance case is not currently ASSURED")

        self.executions[action] = GateReceipt(
            caller=gl.message.sender_address,
            case_id=case_id,
            definition_hash=definition_hash,
            action_hash=action,
        )
        self.execution_count = u256(int(self.execution_count) + 1)

    @gl.public.view
    def was_executed(self, action_hash: str) -> bool:
        return str(action_hash).strip().lower() in self.executions

    @gl.public.view
    def get_execution(self, action_hash: str) -> dict[str, typing.Any]:
        key = str(action_hash).strip().lower()
        if key not in self.executions:
            raise gl.vm.UserError("EXPECTED: unknown execution")
        item = self.executions[key]
        return {
            "caller": str(item.caller),
            "case_id": int(item.case_id),
            "definition_hash": str(item.definition_hash),
            "action_hash": str(item.action_hash),
        }
