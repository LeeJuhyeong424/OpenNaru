"""토크나이저 토큰 타입 및 Token 클래스 정의"""

from dataclasses import dataclass
from enum import Enum


class TokenType(Enum):
    HEADING = "HEADING"              # = 제목 =
    TABLE_ROW = "TABLE_ROW"          # || 셀1 || 셀2 ||
    LIST_ITEM = "LIST_ITEM"          # * 항목 또는 # 항목
    QUOTE = "QUOTE"                  # > 인용문
    HORIZONTAL = "HORIZONTAL"        # ----
    BLANK = "BLANK"                  # 빈 줄
    CODE_BLOCK_OPEN = "CODE_BLOCK_OPEN"    # ```언어
    CODE_BLOCK_CLOSE = "CODE_BLOCK_CLOSE"  # ```
    CODE_BLOCK_BODY = "CODE_BLOCK_BODY"    # 코드블록 내부 줄
    BLOCK_OPEN = "BLOCK_OPEN"        # {{{#!타입 ...
    BLOCK_CLOSE = "BLOCK_CLOSE"      # }}}
    BLOCK_BODY = "BLOCK_BODY"        # 블록 내부 줄
    REDIRECT = "REDIRECT"            # #넘겨주기 또는 #redirect
    PARAGRAPH = "PARAGRAPH"          # 위 어디에도 해당 안 되는 줄


@dataclass
class Token:
    type: TokenType
    text: str       # 원문 줄 텍스트
    line_no: int    # 디버깅용 줄 번호
    meta: dict = None   # 추가 메타데이터 (heading level 등)

    def __post_init__(self):
        if self.meta is None:
            self.meta = {}
