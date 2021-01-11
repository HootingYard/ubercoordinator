"""
Handy miscellaneous functions.
"""

__all__ = ['sift']

from typing import List, TypeVar, Tuple, Callable, Iterable

A = TypeVar('A')

def sift(sequence: Iterable[A],
         condition: Callable[[A], bool]) -> Tuple[List[A], List[A]]:
    """
    Sift an iterable into two lists: one for elements that match a condition
    and one for elements that do not.
    :param sequence: the iterable
    :param condition: the condition
    :return: thw two lists, matching list first
    """
    gold = []
    dross = []
    for element in sequence:
        if condition(element):
            gold.append(element)
        else:
            dross.append(element)
    return gold, dross
