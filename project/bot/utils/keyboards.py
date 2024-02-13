from typing import List, Tuple, Optional

from aiogram.utils.keyboard import InlineKeyboardBuilder as Builder
from aiogram.utils.keyboard import InlineKeyboardMarkup as Markup

from project.bot.utils.texts.buttons import TextButton, ButtonCode
from project.config import BOUNTIES_CREATOR_BOT_URL


async def main(text_button: TextButton) -> Markup:
    return Markup(
        inline_keyboard=[
            [await text_button.get_button(ButtonCode.MAIN)],
        ]
    )


async def main_menu(text_button: TextButton) -> Markup:
    return Markup(
        inline_keyboard=[
            [await text_button.get_button(ButtonCode.ISSUES_LIST)],
            [await text_button.get_button(ButtonCode.CREATE_BOUNTY, url=BOUNTIES_CREATOR_BOT_URL)],
        ]
    )


async def issues_list(text_button: TextButton, items: List[Tuple], page: int, total_pages: int) -> Markup:
    paginator = InlineKeyboardPaginator(
        items=items,
        current_page=page,
        total_pages=total_pages,
        after_reply_markup=await back(text_button),
    )
    return paginator.as_markup()


async def issue_info(text_button: TextButton, issue_url: str) -> Markup:
    return Markup(
        inline_keyboard=[
            [await text_button.get_button(ButtonCode.ISSUE_INFO, url=issue_url)],
            [await text_button.get_button(ButtonCode.BACK)],
        ]
    )


async def back(text_button: TextButton) -> Markup:
    return Markup(
        inline_keyboard=[
            [await text_button.get_button(ButtonCode.BACK)],
        ]
    )


class InlineKeyboardPaginator:
    """
    A class that generates an inline keyboard for paginated data.

    Args:
        items (List[Tuple]): A list of tuples containing the data to be displayed in the keyboard.
        row_width (int): The number of buttons to be displayed per row.
        total_pages (int): The total number of pages.
        current_page (int): The current page number.
        data_pattern (str): The pattern to be used for the callback data.
        before_reply_markup (InlineKeyboardMarkup): A builder to be attached before the items and navigation.
        after_reply_markup (InlineKeyboardMarkup): A builder to be attached after the items and navigation.
    """

    first_page_label = "« {}"
    previous_page_label = "‹ {}"
    current_page_label = "· {} ·"
    next_page_label = "{} ›"
    last_page_label = "{} »"

    def __init__(
            self,
            items: List[Tuple],
            current_page: int = 1,
            total_pages: int = 1,
            row_width: int = 1,
            data_pattern: str = "page:{}",
            before_reply_markup: Optional[Markup] = None,
            after_reply_markup: Optional[Markup] = None,
    ) -> None:
        self.items = items
        self.current_page = current_page
        self.total_pages = total_pages
        self.row_width = row_width
        self.data_pattern = data_pattern

        self.builder = Builder()
        self.before_reply_markup = before_reply_markup
        self.after_reply_markup = after_reply_markup

    def _items_builder(self) -> Builder:
        builder = Builder()

        for key, val in self.items:
            builder.button(text=str(key), callback_data=str(val))
        builder.adjust(self.row_width)

        return builder

    def _navigation_builder(self) -> Builder:
        builder = Builder()
        keyboard_dict = {}

        if self.total_pages > 1:
            if self.total_pages <= 5:
                for page in range(1, self.total_pages + 1):
                    keyboard_dict[page] = page
            else:
                if self.current_page <= 3:
                    page_range = range(1, 4)
                    keyboard_dict[4] = self.next_page_label.format(4)
                    keyboard_dict[self.total_pages] = self.last_page_label.format(self.total_pages)
                elif self.current_page > self.total_pages - 3:
                    keyboard_dict[1] = self.first_page_label.format(1)
                    keyboard_dict[self.total_pages - 3] = self.previous_page_label.format(self.total_pages - 3)
                    page_range = range(self.total_pages - 2, self.total_pages + 1)
                else:
                    keyboard_dict[1] = self.first_page_label.format(1)
                    keyboard_dict[self.current_page - 1] = self.previous_page_label.format(self.current_page - 1)
                    keyboard_dict[self.current_page + 1] = self.next_page_label.format(self.current_page + 1)
                    keyboard_dict[self.total_pages] = self.last_page_label.format(self.total_pages)
                    page_range = [self.current_page]
                for page in page_range:
                    keyboard_dict[page] = page
            keyboard_dict[self.current_page] = self.current_page_label.format(self.current_page)

            for key, val in sorted(keyboard_dict.items()):
                builder.button(text=str(val), callback_data=str(self.data_pattern.format(key)))
            builder.adjust(5)

        return builder

    def as_markup(self) -> Markup:
        if self.before_reply_markup:
            self.builder.attach(Builder(markup=self.before_reply_markup.inline_keyboard))

        self.builder.attach(self._items_builder())
        self.builder.attach(self._navigation_builder())

        if self.after_reply_markup:
            self.builder.attach(Builder(markup=self.after_reply_markup.inline_keyboard))

        return self.builder.as_markup()
