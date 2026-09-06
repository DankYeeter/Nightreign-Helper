"""Cards that answer to more than a mouse.

Several tabs draw a card the reader presses: a Nightlord, a relic, an
armament slot. Each was a `QFrame` whose only trigger was `mousePressEvent`,
and that has three consequences a mouse never runs into.

**The accessibility interface reports success and does nothing.** Measured on
2026-09-06 on Windows under Fusion at 150 % scale, against the running window
with the .NET `UIAutomationClient`: 90 of 90 exposed elements reported
`InvokePattern` as supported, `Invoke` on the Nightlord card returned
`INVOKE_OK`, and the detail panel stayed on `Select a Nightlord` (QA-161). A
client cannot tell "it worked" from "there was nothing to do". Qt's UIA bridge
maps `Invoke` onto the accessible **Press** action, and a plain `QFrame` has
none -- so the fix is to give the card one, on the same call the mouse takes.

**There is no keyboard.** A card with `Qt.NoFocus` is not in the tab order,
and nothing else on the tab leads to it.

**A client cannot find the card.** The only element named `Fulghor` was the
`QLabel` inside the card; the card itself was `ControlType.Custom` with no
name at all.

`PressableFrame` fixes all three in one place, so a card cannot be given the
keyboard and left without a name, or the other way round. What a subclass owes
it is a single method: `press()`, the same call `mousePressEvent` makes.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QAccessible, QAccessibleActionInterface, QPainter
from PySide6.QtWidgets import (
    QAccessibleWidget, QFrame, QStyle, QStyleOptionFocusRect,
)

#: The keys that press a card. Return and Enter are the same gesture on two
#: keyboards; Space is what a button answers to everywhere else in Windows,
#: and a card that reads as a button to an assistive tool has to keep that
#: promise.
PRESS_KEYS = (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Space)


class CardAccessible(QAccessibleWidget):
    """A card as an assistive tool sees it: a button that can be pressed.

    The role matters as much as the action. Left to itself Qt reports a
    `QFrame` as `Role.Border` -- furniture, not a control -- so a reader
    looking for something to activate passes over it even once the action is
    there.
    """

    def __init__(self, widget: PressableFrame):
        super().__init__(widget, QAccessible.Button)

    def actionNames(self) -> list[str]:  # noqa: N802 - Qt naming
        """Press first, then whatever `QAccessibleWidget` already offers.

        First because Qt's Windows bridge takes the *first* name as the one
        `InvokePattern` invokes; behind it stays `SetFocus`, which is how a
        client moves the keyboard to the card without pressing it.
        """
        return [QAccessibleActionInterface.pressAction(), *super().actionNames()]

    def doAction(self, name: str) -> None:  # noqa: N802 - Qt naming
        if name == QAccessibleActionInterface.pressAction():
            self.widget().press()
            return
        super().doAction(name)

    def keyBindingsForAction(self, name: str) -> list[str]:  # noqa: N802
        """What a reader can type to do this without a pointer.

        Announced rather than merely working: a screen reader reads this list
        out, and a key that works but is never named is a key nobody presses.
        """
        if name == QAccessibleActionInterface.pressAction():
            return ["Enter", "Space"]
        return super().keyBindingsForAction(name)


def _accessible_for(_key: str, obj) -> QAccessible:
    return CardAccessible(obj) if isinstance(obj, PressableFrame) else None


_factory_installed = False


def _install_factory() -> None:
    """Register `CardAccessible` with Qt, once per process.

    Called from the constructor rather than from `main`, because a factory
    that some entry point has to remember to install is a factory that is
    missing wherever somebody forgot -- and the symptom would be exactly the
    finding this module exists for: a card that looks right and does nothing.
    """
    global _factory_installed
    if not _factory_installed:
        QAccessible.installFactory(_accessible_for)
        _factory_installed = True


class PressableFrame(QFrame):
    """A card the reader presses -- with a mouse, a keyboard or a screen reader.

    Subclasses say what a press *does* by implementing `press()`, and say what
    the card *is* by passing a name. Everything else -- the tab stop, the two
    keys, the focus rectangle, the accessible role and action -- is settled
    here, because the finding was not that one card lacked one of them but
    that a whole shape of card lacked all four.
    """

    def __init__(self, name: str = "", description: str = ""):
        super().__init__()
        _install_factory()
        # StrongFocus and not TabFocus: a card that answers to a press is a
        # button, and a button takes the keyboard when it is clicked. A
        # reader who clicks a card and then reaches for Tab expects to move on
        # from there and not from wherever the focus happened to be left.
        self.setFocusPolicy(Qt.StrongFocus)
        self.setAccessibleName(name)
        self.setAccessibleDescription(description)

    def press(self) -> None:
        """Do whatever pressing this card does. One call, every route."""
        raise NotImplementedError

    def mousePressEvent(self, event) -> None:  # noqa: N802 - Qt naming
        self.press()
        super().mousePressEvent(event)

    def keyPressEvent(self, event) -> None:  # noqa: N802 - Qt naming
        if event.key() in PRESS_KEYS:
            self.press()
            event.accept()
            return
        super().keyPressEvent(event)

    def paintEvent(self, event) -> None:  # noqa: N802 - Qt naming
        """Draw the card, then say where the keyboard is standing.

        The style's own focus rectangle rather than a fourth colour of this
        program's. The Nightlord grid already spends its three channels --
        fill for the chosen card, a second fill for the pointer, the edge for
        an Everdark twin (QA-150, QA-154) -- and a keyboard mark invented on
        top of those would have to be told apart from all three. The platform
        draws focus one way everywhere, and this is that way.
        """
        super().paintEvent(event)
        if not self.hasFocus():
            return
        option = QStyleOptionFocusRect()
        option.initFrom(self)
        # Inside the 1 px border and the 7 px corner radius, so the mark is
        # a mark of its own rather than a recolouring of the edge that
        # already means "Everdark twin".
        option.rect = self.rect().adjusted(4, 4, -4, -4)
        painter = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_FrameFocusRect, option, painter,
                                   self)
        painter.end()
