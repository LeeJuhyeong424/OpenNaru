"""1단계: 토크나이저 — 입력 텍스트를 줄 단위로 읽어 토큰으로 분류한다."""

import re
from .tokens import Token, TokenType


# 제목 패턴: = 텍스트 = (1~5단계)
_RE_HEADING = re.compile(r'^(={1,5})\s+(.+?)\s+\1\s*$')

# 리스트 패턴: *, **, ***, #, ##, ###
_RE_LIST = re.compile(r'^([*#]+)\s+(.*)')

# 인용문 패턴: > 텍스트
_RE_QUOTE = re.compile(r'^>\s*(.*)')

# 코드블록 열기: ```언어 (언어는 선택)
_RE_CODE_OPEN = re.compile(r'^```(\w*)$')

# 나무마크 블록 열기: {{{#!타입 [제목]
_RE_BLOCK_OPEN = re.compile(r'^\{\{\{#!(\w+)(?:\s+(.*))?$')

# 넘겨주기
_RE_REDIRECT = re.compile(r'^#(넘겨주기|redirect)\s+\[\[(.+?)\]\]', re.IGNORECASE)


def tokenize(text: str) -> list[Token]:
    """입력 텍스트를 토큰 목록으로 변환한다."""
    tokens: list[Token] = []
    lines = text.splitlines()

    in_code_block = False
    in_block = False
    block_depth = 0     # 중첩 블록 처리용

    for line_no, line in enumerate(lines, start=1):

        # ── 코드블록 내부 ───────────────────────────────────────────────────
        if in_code_block:
            if line.rstrip() == '```':
                tokens.append(Token(TokenType.CODE_BLOCK_CLOSE, line, line_no))
                in_code_block = False
            else:
                tokens.append(Token(TokenType.CODE_BLOCK_BODY, line, line_no))
            continue

        # ── 나무마크 블록 내부 ──────────────────────────────────────────────
        if in_block:
            if line.rstrip() == '}}}':
                block_depth -= 1
                if block_depth == 0:
                    tokens.append(Token(TokenType.BLOCK_CLOSE, line, line_no))
                    in_block = False
                else:
                    tokens.append(Token(TokenType.BLOCK_BODY, line, line_no))
            elif _RE_BLOCK_OPEN.match(line):
                block_depth += 1
                tokens.append(Token(TokenType.BLOCK_BODY, line, line_no))
            else:
                tokens.append(Token(TokenType.BLOCK_BODY, line, line_no))
            continue

        stripped = line.strip()

        # ── 빈 줄 ──────────────────────────────────────────────────────────
        if not stripped:
            tokens.append(Token(TokenType.BLANK, line, line_no))
            continue

        # ── 넘겨주기 ────────────────────────────────────────────────────────
        m = _RE_REDIRECT.match(stripped)
        if m:
            tokens.append(Token(TokenType.REDIRECT, stripped, line_no,
                                meta={"target": m.group(2)}))
            continue

        # ── 수평선 ──────────────────────────────────────────────────────────
        if stripped == '----':
            tokens.append(Token(TokenType.HORIZONTAL, stripped, line_no))
            continue

        # ── 제목 ────────────────────────────────────────────────────────────
        m = _RE_HEADING.match(stripped)
        if m:
            level = len(m.group(1))
            tokens.append(Token(TokenType.HEADING, stripped, line_no,
                                meta={"level": level, "content": m.group(2)}))
            continue

        # ── 코드블록 열기 ────────────────────────────────────────────────────
        m = _RE_CODE_OPEN.match(stripped)
        if m:
            tokens.append(Token(TokenType.CODE_BLOCK_OPEN, stripped, line_no,
                                meta={"language": m.group(1)}))
            in_code_block = True
            continue

        # ── 나무마크 블록 열기 ───────────────────────────────────────────────
        m = _RE_BLOCK_OPEN.match(stripped)
        if m:
            tokens.append(Token(TokenType.BLOCK_OPEN, stripped, line_no,
                                meta={"kind": m.group(1), "summary": m.group(2) or ""}))
            in_block = True
            block_depth = 1
            continue

        # ── 표 행 ────────────────────────────────────────────────────────────
        if stripped.startswith('||'):
            tokens.append(Token(TokenType.TABLE_ROW, stripped, line_no))
            continue

        # ── 리스트 ──────────────────────────────────────────────────────────
        m = _RE_LIST.match(stripped)
        if m:
            tokens.append(Token(TokenType.LIST_ITEM, stripped, line_no,
                                meta={"prefix": m.group(1), "content": m.group(2)}))
            continue

        # ── 인용문 ──────────────────────────────────────────────────────────
        m = _RE_QUOTE.match(stripped)
        if m:
            tokens.append(Token(TokenType.QUOTE, stripped, line_no,
                                meta={"content": m.group(1)}))
            continue

        # ── 일반 문단 ────────────────────────────────────────────────────────
        tokens.append(Token(TokenType.PARAGRAPH, line, line_no))

    return tokens
