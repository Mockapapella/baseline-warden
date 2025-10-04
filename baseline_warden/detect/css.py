"""CSS detector that emits Baseline BCD keys for properties and selectors."""

from __future__ import annotations

from pathlib import Path
from typing import Any, List, Sequence

import tinycss2

from .common import Detection

SELECTOR_PREFIX = "css.selectors"
PROPERTY_PREFIX = "css.properties"
AT_RULE_PREFIX = "css.at-rules"


def detect_css(path: Path, *, encoding: str = "utf-8") -> List[Detection]:
    """Detect CSS properties, values, selectors, and at-rules."""

    try:
        text = path.read_text(encoding=encoding)
    except UnicodeDecodeError:
        text = path.read_text(encoding=encoding, errors="ignore")

    detections: List[Detection] = []
    seen: set[tuple[int, str]] = set()

    def add_detection(detection: Detection) -> None:
        key = (detection.line, detection.bcd_key)
        if key in seen:
            return
        seen.add(key)
        detections.append(detection)

    def process_nodes(nodes: Sequence[Any]) -> None:
        for node in nodes:
            line = getattr(node, "source_line", 1)
            node_type = getattr(node, "type", None)

            if node_type == "at-rule" and getattr(node, "lower_at_keyword", None):
                add_detection(Detection(path=path, line=line, bcd_key=f"{AT_RULE_PREFIX}.{node.lower_at_keyword}"))
                if getattr(node, "content", None):
                    decls = _filter_declarations(
                        tinycss2.parse_declaration_list(node.content, skip_comments=True, skip_whitespace=True)
                    )
                    for decl in decls:
                        for detection in _declaration_detections(path, decl, line_override=line):
                            add_detection(detection)
                    inner_rules = tinycss2.parse_rule_list(node.content, skip_comments=True, skip_whitespace=True)
                    if inner_rules:
                        process_nodes(inner_rules)
            elif node_type == "qualified-rule":
                for selector_key in _selector_keys(node.prelude):
                    add_detection(Detection(path=path, line=line, bcd_key=selector_key))
                if getattr(node, "content", None):
                    decls = _filter_declarations(
                        tinycss2.parse_declaration_list(node.content, skip_comments=True, skip_whitespace=True)
                    )
                    for decl in decls:
                        for detection in _declaration_detections(path, decl):
                            add_detection(detection)
            elif node_type == "declaration":
                for detection in _declaration_detections(path, node, line_override=line):
                    add_detection(detection)

    rules = tinycss2.parse_stylesheet(text, skip_comments=True, skip_whitespace=True)
    process_nodes(rules)

    # Fallback: parse as declaration list for loose CSS (inline styles, etc.)
    loose_decls = _filter_declarations(
        tinycss2.parse_declaration_list(text, skip_comments=True, skip_whitespace=True)
    )
    for decl in loose_decls:
        for detection in _declaration_detections(path, decl):
            add_detection(detection)

    return detections


def _filter_declarations(nodes: Sequence[Any]) -> List[Any]:
    return [node for node in nodes if getattr(node, "type", None) == "declaration"]


def _selector_keys(tokens: Sequence[Any]) -> List[str]:
    keys: List[str] = []
    pending_colons = 0
    for token in tokens:
        token_type = getattr(token, "type", None)
        if token_type == "colon" or (token_type == "literal" and getattr(token, "value", None) == ":"):
            pending_colons += 1
            continue
        if pending_colons:
            if token_type == "ident":
                name = token.value.lower()
                keys.append(f"{SELECTOR_PREFIX}.{name}")
            elif token_type == "function":
                name = token.lower_name
                keys.append(f"{SELECTOR_PREFIX}.{name}")
            pending_colons = 0
        else:
            pending_colons = 0
    return keys


def _property_value_idents(tokens: Sequence[Any]) -> List[str]:
    values: List[str] = []
    for token in tokens:
        token_type = getattr(token, "type", None)
        if token_type == "ident":
            values.append(token.value.lower())
        elif token_type == "function":
            values.append(token.lower_name)
    return values


def _declaration_detections(
    path: Path,
    declaration: Any,
    *,
    line_override: int | None = None,
) -> List[Detection]:
    if getattr(declaration, "type", None) != "declaration" or declaration.name is None:
        return []

    line = line_override or getattr(declaration, "source_line", 1)
    name = declaration.lower_name
    detections = [Detection(path=path, line=line, bcd_key=f"{PROPERTY_PREFIX}.{name}")]
    values = _property_value_idents(getattr(declaration, "value", []))
    for value in values:
        detections.append(Detection(path=path, line=line, bcd_key=f"{PROPERTY_PREFIX}.{name}.{value}"))
    return detections


__all__ = ["detect_css"]
