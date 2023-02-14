
from abc import abstractclassmethod
from typing import Union,TypeAlias,Self

ExprTreeNode:TypeAlias = Union[None,"CfgTree","IntNode","FloatNode","StrNode"]

class CfgTree:
    def __init__(self, children,parent:ExprTreeNode, level:int) -> None:
        self.children = children
        self.parent = parent
        self.level = level

    def __str__(self: Self) -> str:
        return "test"

    @abstractclassmethod
    def from_dict(cfg_dict: dict, level:int, parent:ExprTreeNode) -> Self:
        children = 
        return CfgTree(children=children,parent=parent,level)


def dict_to_expr_tree(cfg_dict: dict) -> CfgTree:
    CfgTree(cfg_dict,None,level=0)
    pass
