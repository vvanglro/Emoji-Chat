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
    FLAGS = 9  # 旗帜


def random_select_unique_characters(input_string, num_characters):
    if len(input_string) < num_characters:
        raise ValueError("Input string must contain at least {} unique characters".format(num_characters))

    selected_chars = random.sample(input_string, num_characters)

    return "".join(selected_chars)


@functools.lru_cache()
def get_emoji_data():
    with open("emoji.json", "r") as f:
        return json.loads(f.read())


data = get_emoji_data()
