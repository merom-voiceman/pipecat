from contextvars import ContextVar
from typing import Optional

run_id_var: ContextVar[Optional[int]] = ContextVar("run_id_var", default=None)
_org_id_var: ContextVar[Optional[int]] = ContextVar("org_id_var", default=None)
turn_var: ContextVar[Optional[int]] = ContextVar("turn_var", default=None)


def set_current_run_id(run_id: int) -> None:
    run_id_var.set(run_id)


def set_current_org_id(org_id: int) -> None:
    _org_id_var.set(org_id)


def get_current_org_id() -> Optional[int]:
    return _org_id_var.get()
