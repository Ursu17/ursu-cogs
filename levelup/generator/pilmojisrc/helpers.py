from __future__ import annotations

import re
from enum import Enum
from typing import TYPE_CHECKING, Dict, Final, List, NamedTuple, Tuple

import emoji
import emoji.core
from emoji import unicode_codes
from PIL import ImageFont

if TYPE_CHECKING:
    from .core import FontT

# This is actually way faster than it seems
if emoji.__version__ >= "2.12.0":
    language_pack = {
        v["en"]: k for k, v in emoji.EMOJI_DATA.items() if "en" in v and v["status"] <= emoji.STATUS["fully_qualified"]
    }
else:
    language_pack: Dict[str, str] = unicode_codes.get_emoji_unicode_dict("en")


_UNICODE_EMOJI_REGEX = "|".join(map(re.escape, sorted(language_pack.values(), key=len, reverse=True)))
_DISCORD_EMOJI_REGEX = "<a?:[a-zA-Z0-9_]{2,32}:[0-9]{17,22}>"

EMOJI_REGEX: Final[re.Pattern[str]] = re.compile(f"({_UNICODE_EMOJI_REGEX}|{_DISCORD_EMOJI_REGEX})")

__all__ = ("EMOJI_REGEX", "Node", "NodeType", "to_nodes", "getsize")


class NodeType(Enum):
    """|enum|

    Represents the type of a :class:`~.Node`.

    Attributes
    ----------
    text
        This node is a raw text node.
    emoji
        This node is a unicode emoji.
    discord_emoji
        This node is a Discord emoji.
    """

    text = 0
    emoji = 1
    discord_emoji = 2


class Node(NamedTuple):
    """Represents a parsed node inside of a string.

    Attributes
    ----------
    type: :class:`~.NodeType`
        The type of this node.
    content: str
        The contents of this node.
    """

    type: NodeType
    content: str

    def __repr__(self) -> str:
        return f"<Node type={self.type.name!r} content={self.content!r}>"


def _parse_line(line: str, /) -> List[Node]:
    nodes = []

    for i, chunk in enumerate(EMOJI_REGEX.split(line)):
        if not chunk:
            continue

        if not i % 2:
            nodes.append(Node(NodeType.text, chunk))
            continue

        if len(chunk) > 18:  # This is guaranteed to be a Discord emoji
            node = Node(NodeType.discord_emoji, chunk.split(":")[-1][:-1])
        else:
            node = Node(NodeType.emoji, chunk)

        nodes.append(node)

    return nodes


def to_nodes(text: str, /) -> List[List[Node]]:
    """Parses a string of text into :class:`~.Node`s.

    This method will return a nested list, each element of the list
    being a list of :class:`~.Node`s and representing a line in the string.

    The string ``'Hello\nworld'`` would return something similar to
    ``[[Node('Hello')], [Node('world')]]``.

    Parameters
    ----------
    text: str
        The text to parse into nodes.

    Returns
    -------
    List[List[:class:`~.Node`]]
    """
    return [_parse_line(line) for line in text.splitlines()]


def getsize(text: str, font: FontT = None, *, spacing: int = 4, emoji_scale_factor: float = 1) -> Tuple[int, int]:
    """Return the width and height of the text when rendered.
    This method supports multiline text.

    Parameters
    ----------
    text: str
        The text to use.
    font
        The font of the text.
    spacing: int
        The spacing between lines, in pixels.
        Defaults to `4`.
    emoji_scale_factor: float
        The rescaling factor for emojis.
        Defaults to `1`.
    """
    if font is None:
        font = ImageFont.load_default()

    x, y = 0, 0
    nodes = to_nodes(text)

    for line in nodes:
        this_x = 0
        for node in line:
            content = node.content

            if node.type is not NodeType.text:
                width = int(emoji_scale_factor * font.size)
            else:
                width = int(font.getlength(content))
                # try:
                #     width, _ = font.getsize(content)
                # except AttributeError:
                #     width = int(font.getlength(content))

            this_x += width

        y += spacing + int(font.size)

        if this_x > x:
            x = this_x

    return x, y - spacing
