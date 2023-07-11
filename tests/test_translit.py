from textalign.translit import unidecode_ger


def test_unidecode_ger_01():
    token_in = "Olivenæſte"
    target = "Olivenäste"
    token_out = unidecode_ger(token_in)
    assert token_out == target


def test_unidecode_ger_02():
    token_in = "naͤrꝛiſchen"
    target = "närrischen"
    token_out = unidecode_ger(token_in)
    assert token_out == target
