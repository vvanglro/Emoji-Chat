from __future__ import annotations
import functools
import json
import random
from enum import IntEnum


class EmojiCategory(IntEnum):
    SMILEYS_AND_PEOPLE = 1  # 笑脸和情感
    PEOPLE_AND_BODY = 2  # 人类和身体
    ANIMALS_AND_NATURE = 3  # 动物和自然
    FOOD_AND_DRINK = 4  # 食物和饮料
    TRAVEL_AND_PLACES = 5  # 旅行和地点
    ACTIVITIES = 6  # 活动
    OBJECTS = 7  # 物品
    SYMBOLS = 8  # 符号


def random_select_unique_characters(emoji_list: list, num_characters: int) -> str:
    if len(emoji_list) < num_characters:
        raise ValueError("Input string must contain at least {} unique characters".format(num_characters))

    selected_chars = random.sample(emoji_list, num_characters)
    processed_chars = [char.encode().decode("unicode_escape") for char in selected_chars]
    return "".join(processed_chars)


@functools.lru_cache()
def get_emoji_data() -> dict:
    with open("emoji_chat/emoji.json", "r") as f:
        return json.loads(f.read())


def get_emoji(emoji_category: EmojiCategory | None = None) -> str:
    emoji_data = get_emoji_data()
    if not emoji_category:
        category = random.choice(list(EmojiCategory))
    else:
        category = emoji_category.value  # type: ignore[assignment]
    emoji_list = emoji_data.get(str(category))
    if not emoji_list:
        raise ValueError("Emoji category not found")
    return random_select_unique_characters(emoji_list, 65)
