"""Popup action ordering and visibility for Bragi."""

from typing import Any, Dict, Iterable, List, Sequence, Tuple


BUILTIN_POPUP_ACTION_ORDER = (
    "grammar_check",
    "rewrite",
    "professional",
    "summarize",
    "translate",
)

POPUP_ACTION_ORDER_KEY = "popup.actions.order"
POPUP_ACTION_HIDDEN_KEY = "popup.actions.hidden"


def get_available_popup_actions(prompt_manager) -> List[Dict[str, Any]]:
    """Return all popup-capable actions in their natural default order."""
    actions: List[Dict[str, Any]] = []
    seen = set()

    for prompt_key in BUILTIN_POPUP_ACTION_ORDER:
        prompt = prompt_manager.get_prompt_info(prompt_key)
        if not prompt:
            continue
        actions.append(
            {
                "key": prompt_key,
                "name": str(prompt.get("name", prompt_key)),
                "builtin": True,
            }
        )
        seen.add(prompt_key)

    for action in prompt_manager.get_custom_actions():
        prompt_key = str(action.get("key", "")).strip()
        if not prompt_key or prompt_key in seen:
            continue
        actions.append(
            {
                "key": prompt_key,
                "name": str(action.get("name", prompt_key)),
                "builtin": False,
            }
        )
        seen.add(prompt_key)

    return actions


def normalize_popup_layout(
    order: Any,
    hidden: Any,
    available_keys: Sequence[str],
) -> Tuple[List[str], List[str]]:
    """Drop stale keys, de-duplicate state and append newly available actions."""
    available = [str(key) for key in available_keys]
    available_set = set(available)

    normalized_order: List[str] = []
    seen = set()
    if isinstance(order, (list, tuple)):
        for raw_key in order:
            key = str(raw_key)
            if key in available_set and key not in seen:
                normalized_order.append(key)
                seen.add(key)

    for key in available:
        if key not in seen:
            normalized_order.append(key)
            seen.add(key)

    hidden_set = set()
    if isinstance(hidden, (list, tuple, set)):
        hidden_set = {str(key) for key in hidden if str(key) in available_set}

    normalized_hidden = [
        key for key in normalized_order if key in hidden_set
    ]
    return normalized_order, normalized_hidden


def get_popup_action_layout(config_manager, prompt_manager) -> Tuple[List[str], List[str]]:
    """Load and normalize the persisted popup layout.

    Bragi v2.1 stored Custom Action visibility inside each prompt. If no unified
    popup layout has been saved yet, preserve those legacy hidden states once.
    """
    actions = get_available_popup_actions(prompt_manager)
    available_keys = [action["key"] for action in actions]

    stored_order = config_manager.get(POPUP_ACTION_ORDER_KEY, None)
    stored_hidden = config_manager.get(POPUP_ACTION_HIDDEN_KEY, None)
    has_saved_layout = isinstance(stored_order, list) or isinstance(
        stored_hidden, list
    )

    if not has_saved_layout:
        stored_order = available_keys
        stored_hidden = [
            action["key"]
            for action in prompt_manager.get_custom_actions()
            if not bool(action.get("show_in_popup", True))
        ]

    return normalize_popup_layout(
        stored_order,
        stored_hidden,
        available_keys,
    )


def get_visible_popup_actions(config_manager, prompt_manager) -> List[Dict[str, str]]:
    """Return popup actions in user-selected order, excluding hidden actions."""
    actions = get_available_popup_actions(prompt_manager)
    action_by_key = {action["key"]: action for action in actions}
    order, hidden = get_popup_action_layout(config_manager, prompt_manager)
    hidden_set = set(hidden)

    return [
        {
            "key": key,
            "name": str(action_by_key[key]["name"]),
        }
        for key in order
        if key in action_by_key and key not in hidden_set
    ]


def restore_builtin_defaults(
    order: Iterable[str],
    hidden: Iterable[str],
    prompt_manager,
) -> Tuple[List[str], List[str]]:
    """Restore built-in order/visibility while preserving Custom Action choices."""
    actions = get_available_popup_actions(prompt_manager)
    available_keys = [action["key"] for action in actions]
    available_set = set(available_keys)
    custom_keys = {
        action["key"] for action in actions if not bool(action.get("builtin"))
    }

    current_order, current_hidden = normalize_popup_layout(
        list(order),
        list(hidden),
        available_keys,
    )

    builtins = [
        key
        for key in BUILTIN_POPUP_ACTION_ORDER
        if key in available_set
    ]
    customs = [key for key in current_order if key in custom_keys]
    restored_order = builtins + customs
    restored_hidden = [
        key for key in current_hidden if key in custom_keys
    ]

    return restored_order, restored_hidden
