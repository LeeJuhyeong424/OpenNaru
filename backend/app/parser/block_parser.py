"""2단계: 블록 파서 — 토큰 목록을 블록 AST 노드로 변환한다."""

from .tokens import Token, TokenType
from .nodes import (
    BaseNode, HeadingNode, ParagraphNode, TableNode,
    ListNode, ListItemNode, QuoteNode, HorizontalNode,
    CodeBlockNode, FoldingNode, CalloutNode, HtmlBlockNode,
    RedirectNode,
)


def parse_blocks(tokens: list[Token]) -> list[BaseNode]:
    """토큰 목록을 블록 노드 목록으로 변환한다."""
    nodes: list[BaseNode] = []
    i = 0

    while i < len(tokens):
        token = tokens[i]

        # ── 빈 줄 무시 ──────────────────────────────────────────────────────
        if token.type == TokenType.BLANK:
            i += 1
            continue

        # ── 넘겨주기 ────────────────────────────────────────────────────────
        if token.type == TokenType.REDIRECT:
            nodes.append(RedirectNode(target=token.meta["target"]))
            i += 1
            continue

        # ── 수평선 ──────────────────────────────────────────────────────────
        if token.type == TokenType.HORIZONTAL:
            nodes.append(HorizontalNode())
            i += 1
            continue

        # ── 제목 ────────────────────────────────────────────────────────────
        if token.type == TokenType.HEADING:
            nodes.append(HeadingNode(
                level=token.meta["level"],
                content=token.meta["content"],
            ))
            i += 1
            continue

        # ── 코드블록 ─────────────────────────────────────────────────────────
        if token.type == TokenType.CODE_BLOCK_OPEN:
            language = token.meta.get("language", "")
            body_lines: list[str] = []
            i += 1
            while i < len(tokens) and tokens[i].type != TokenType.CODE_BLOCK_CLOSE:
                body_lines.append(tokens[i].text)
                i += 1
            i += 1  # CODE_BLOCK_CLOSE 소비
            nodes.append(CodeBlockNode(language=language, content="\n".join(body_lines)))
            continue

        # ── 나무마크 블록 ({{{#!kind ...}}}) ─────────────────────────────────
        if token.type == TokenType.BLOCK_OPEN:
            kind = token.meta.get("kind", "")
            summary = token.meta.get("summary", "")
            body_lines = []
            i += 1
            while i < len(tokens) and tokens[i].type != TokenType.BLOCK_CLOSE:
                body_lines.append(tokens[i].text)
                i += 1
            i += 1  # BLOCK_CLOSE 소비
            inner_text = "\n".join(body_lines)

            if kind == "html":
                nodes.append(HtmlBlockNode(content=inner_text))
            elif kind == "folding":
                inner_nodes = parse_blocks(tokenize_text(inner_text))
                nodes.append(FoldingNode(summary=summary, children=inner_nodes))
            elif kind in ("note", "tip", "warning", "danger"):
                inner_nodes = parse_blocks(tokenize_text(inner_text))
                nodes.append(CalloutNode(kind=kind, children=inner_nodes))
            else:
                # 알 수 없는 블록 타입은 문단으로 fallback
                nodes.append(ParagraphNode(lines=[inner_text]))
            continue

        # ── 표 ──────────────────────────────────────────────────────────────
        if token.type == TokenType.TABLE_ROW:
            rows: list[list[str]] = []
            while i < len(tokens) and tokens[i].type == TokenType.TABLE_ROW:
                cells = _parse_table_row(tokens[i].text)
                rows.append(cells)
                i += 1
            nodes.append(TableNode(rows=rows))
            continue

        # ── 리스트 ──────────────────────────────────────────────────────────
        if token.type == TokenType.LIST_ITEM:
            items: list[ListItemNode] = []
            while i < len(tokens) and tokens[i].type == TokenType.LIST_ITEM:
                prefix = tokens[i].meta["prefix"]
                depth = len(prefix)
                ordered = prefix[-1] == '#'
                items.append(ListItemNode(
                    depth=depth,
                    ordered=ordered,
                    content=tokens[i].meta["content"],
                ))
                i += 1
            # 최상위 ordered 여부는 첫 항목 기준
            nodes.append(ListNode(ordered=items[0].ordered, items=items))
            continue

        # ── 인용문 ──────────────────────────────────────────────────────────
        if token.type == TokenType.QUOTE:
            lines: list[str] = []
            while i < len(tokens) and tokens[i].type == TokenType.QUOTE:
                lines.append(tokens[i].meta["content"])
                i += 1
            nodes.append(QuoteNode(lines=lines))
            continue

        # ── 일반 문단 ────────────────────────────────────────────────────────
        if token.type == TokenType.PARAGRAPH:
            lines = []
            while i < len(tokens) and tokens[i].type == TokenType.PARAGRAPH:
                lines.append(tokens[i].text)
                i += 1
            nodes.append(ParagraphNode(lines=lines))
            continue

        i += 1

    return nodes


def _parse_table_row(text: str) -> list[str]:
    """|| 셀1 || 셀2 || 형식의 줄을 셀 목록으로 파싱한다."""
    # 앞뒤 || 제거 후 || 로 분리
    stripped = text.strip()
    if stripped.startswith('||'):
        stripped = stripped[2:]
    if stripped.endswith('||'):
        stripped = stripped[:-2]
    cells = [cell.strip() for cell in stripped.split('||')]
    return cells


def tokenize_text(text: str) -> list[Token]:
    """재귀 블록 파싱용 — 내부에서 import 순환을 피하기 위해 지연 import."""
    from .tokenizer import tokenize
    return tokenize(text)
