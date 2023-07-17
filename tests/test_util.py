from typing import List

from textalign import util


# fake test
def test_parse_waste() -> None:
    waste_output = """\
Dies	0 4
iſt	5 4
ein	10 3
erſter	14 7
-	22 1	[$(]
hiſtorischer	24 13
(	38 1	[$(]
Sattz	39 5
)	44 1	[$(]
.	45 1	[$.]"""

    #     waste_output = """\
    # Dies	0 4
    # iſt	5 4
    # ein	10 3
    # erſter	14 7
    # hiſtorischer	22 13
    # Sattz	36 5
    # .	41 1	[$.]

    # Hier	43 4
    # sind	48 4
    # beyde	53 5
    # Taͤxte	59 7
    # wieder	67 6
    # aliginieret	74 11
    # ,	85 1	[$,]
    # aber	87 4
    # in	92 2
    # der	95 3
    # Uebersetzung	99 12
    # iſt	112 4
    # eyn	117 3
    # Punckt	121 6
    # ,	127 1	[$,]
    # wo	129 2
    # ihm	132 3
    # Original	136 8
    # eyn	145 3
    # Koma	149 4
    # iſt	154 4
    # .	158 1	[$.]\
    # """

    for sent in util.parse_waste_output(waste_output):
        for tok in sent:
            print(tok)

    assert True


def test_get_sentence_start_idxs() -> None:
    waste_output = """\
Dies	0 4
iſt	5 4
ein	10 3
erſter	14 7
hiſtorischer	22 13
Sattz	36 5
.	41 1	[$.]

Hier	43 4
sind	48 4
beyde	53 5
Taͤxte	59 7
wieder	67 6
aliginieret	74 11
,	85 1	[$,]
aber	87 4
in	92 2
der	95 3
Uebersetzung	99 12
iſt	112 4
eyn	117 3
Punckt	121 6
,	127 1	[$,]
wo	129 2
ihm	132 3
Original	136 8
eyn	145 3
Koma	149 4
iſt	154 4
.	158 1	[$.]\
"""

    doc: List[List[util.Token]] = util.parse_waste_output(waste_output)
    output: List[int] = util.get_sentence_start_idxs(doc)
    target = [0, 7]
    assert output == target


def test_find_closest() -> None:
    # Driver code
    arr = [1, 2, 4, 5, 6, 7, 8, 9]
    target = 11
    closest = util.find_closest(arr, target)
    assert closest == 9
    target = 7
    closest = util.find_closest(arr, target)
    assert closest == 7
