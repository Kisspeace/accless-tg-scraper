from accless_tg_scraper.classes import *
from copy import deepcopy

class TgEntityRuleSet():
    class EntityRule():
        def __init__(self, ent_type: TgMessageEntity, prefix: str, postfix: str):
            self.prefix: str = prefix
            self.postfix: str = postfix
            self.type = ent_type

        def convert(self, entity: TgMessageEntity, source: str):
            sub_str = source[entity.offset : entity.get_end()]
            return f'{self.prefix}{sub_str}{self.postfix}'

    def __init__(self):
        self.bold: self.EntityRule = None
        self.italic: self.EntityRule = None
        self.strikethrogh: self.EntityRule = None
        self.underlined: self.EntityRule = None
        self.url: self.EntityRule = None
        self.spoiler: self.EntityRule = None
        self.emoji: self.EntityRule = None
        # self.rules = []

    def get_rules(self) -> list:
        return [
            self.bold,
            self.italic,
            self.strikethrogh,
            self.underlined,
            self.url,
            self.spoiler,
            self.emoji
        ]

    def rule_by_type(self, ent_type: TgMessageEntity):
        for rule in self.get_rules():
            if rule.type is ent_type:
                return rule
        return None

    def get_converted(self, entity: TgMessageEntity, source: str):
        rule = self.rule_by_type(type(entity))
        return rule.convert(entity, source)

def dump_content(content: str, entities: list, rule_set: TgEntityRuleSet) -> str:
    """
    Args:
        content (str): text.
        entities (list): list of entities for given text.
        rule_set (TgEntityRuleSet): rule set.
    Returns:
        str: post.content converted to custom format with post.entities.
    """

    if len(entities) < 1:
        return content

    entities = deepcopy(entities)
    res: str = content

    def replace_with(offset: int, length: int, string: str):
        nonlocal res
        slice_a = res[0 : offset]
        slice_b = res[offset + length : len(res)]
        res = slice_a + string + slice_b

    # print('BEGIN MARK ______________________\n')
    l = len(entities)
    for i in range(0, l):
        ent = entities[i]
        rule = rule_set.rule_by_type(type(ent))
        converted = rule.convert(ent, res)
        replace_with(ent.offset, ent.length, converted)

        # now need to remap all next entities.
        for n in range(i + 1, l):
            next_ent = entities[n]

            # info about next entity.
            start_after = (next_ent.offset >= ent.get_end())
            start_inside = (not start_after) and (next_ent.offset >= ent.offset)

            # debug.
            # r = rule_set.rule_by_type(type(next_ent))
            # print(f'[{n}] {r.type.__name__} s_after:{start_after}, s_inside:{start_inside}')

            if start_after:
                next_ent.offset += (len(converted) - ent.length)
            elif start_inside:
                next_ent.offset += len(rule.prefix)

    # print('MARK END -----------------------\n')
    return res
