from typing import Dict


def dict_merge(base_dict: Dict, extra_dict: Dict) -> Dict:
    """
    Dict 元素并集
    :example merge({a:1,b:2},{b:3,c:4}) -> {a:1,b:3,c:4}
    :param base_dict:
    :param extra_dict:
    :return:
    """
    if not extra_dict:
        return base_dict
    return {k: extra_dict.get(k, base_dict.get(k)) for k in set(base_dict) | set(extra_dict)}


def dict_differential(base_dict: Dict, minus_dict: Dict) -> Dict:
    """
    Dict 元素差集
    :example diff({a:1,b:2},{b:3,c:4}) -> {a:1}
    :param base_dict:
    :param minus_dict:
    :return:
    """
    return {k: base_dict[k] for k in base_dict.keys() - minus_dict.keys()}


def dict_symmetric_difference(base_dict: Dict, minus_dict: Dict) -> Dict:
    """
    Dict 对称差集
    :example symmetric_diff({a:1,b:2},{b:3,c:4}) -> {a:1,c:4}
    :param base_dict:
    :param minus_dict:
    :return:
    """
    return {k: base_dict.get(k, minus_dict.get(k)) for k in base_dict.keys() ^ minus_dict.keys()}


def dict_intersection(a: Dict, b: Dict) -> Dict:
    """
    Dict 元素交集
    :example intersection({a:1,b:2},{b:3,c:4}) -> {b:2}
    :param a:
    :param b:
    :return:
    """
    return {k: a[k] for k in a.keys() & b.keys()}


if __name__ == '__main__':
    print("dict_merge", dict_merge({"a": 1, "b": 2}, {"b": 3, "c": 4}))
    print("dict_differential", dict_differential({"a": 1, "b": 2}, {"b": 3, "c": 4}))
    print("dict_symmetric_difference", dict_symmetric_difference({"a": 1, "b": 2}, {"b": 3, "c": 4}))
    print("dict_intersection", dict_intersection({"a": 1, "b": 2}, {"b": 3, "c": 4}))
