from typing import Dict, List, Tuple, Union

import os

from dataclasses import dataclass


@dataclass
class Token:
    text: str
    initial_ws: bool = False


@dataclass
class AlignedPair:
    a: Union[int, None]
    b: Union[int, None]


def parse_waste_output(file_or_str: str) -> List[List[Token]]:
    """
    Parse the output of the WASTE tokenizer into sentences with tokens and whitespace information: List[List[Token]]

    WASTE output format:

    Dies	0 4
    iſt	5 4
    ein	10 3
    erſter	14 7
    -	22 1	[$(]
    hiſtorischer	24 13
    (	38 1	[$(]
    Sattz	39 5
    )	44 1	[$(]
    .	45 1	[$.]
    """

    # TODO: handle parsing errors

    if os.path.exists(file_or_str):
        with open(file_or_str, "r", encoding="utf-8") as f:
            full_text = f.read()
    else:
        full_text = file_or_str

    # split into sentences (at double newlines)
    sentences_str = full_text.split("\n\n")

    # read the first three fields (token text, offset, length)
    sentences_tok_tmp = [
        [line.split()[:3] for line in sentence_str.split("\n")]
        for sentence_str in sentences_str
    ]

    # convert offset and length from string to int
    sentences_tok = []
    # very first sentence is set to start without whitespace
    # initial_ws = False
    end_prev = 0
    for sent in sentences_tok_tmp:
        s = []
        for i, t in enumerate(sent):
            if not len(t):
                continue
            (text, offset, length) = t
            offset = int(offset)
            length = int(length)
            initial_ws = True if end_prev < offset else False
            token = Token(text, initial_ws)
            if i == 0:
                token.is_sent_start = True
            end_prev = offset + length
            s.append(token)
        sentences_tok.append(s)

    return sentences_tok


def get_sentence_start_idxs(doc: List[List[Token]]) -> List[int]:
    """
    Get a list of token indices where sentences start
    """
    sentence_start_idxs = []

    for i, token in enumerate([token for sent in doc for token in sent]):
        if hasattr(token, "is_sent_start"):
            if token.is_sent_start:
                sentence_start_idxs.append(i)

    return sentence_start_idxs


# def get_sentence_start_idxs(doc: List[List[Token]]) -> List[int]:
#     """
#     Get a list of token indices where sentences start
#     """
#     sentence_start_idxs = []

#     i = 0
#     for sent in doc:
#         for j, token in enumerate(token, start=i):
#             if j == sent_final_idx
#                 sentence_start_idxs.append(j)
#             # end becomes start
#             j = i
#         sent_final_idx = j
#     return sentence_start_idxs


def get_offset2tokidx_from_wastefile(path: str) -> Dict[int, int]:
    """
    Create a mapping: character offset -> token index

    TODO: currently we assume path is a WASTE-tokenized file
    """

    # reading in a WASTE file
    with open(path, "r", encoding="utf-8") as f:
        doc = f.read()
    # split into lines
    doc = doc.split("\n")
    # create mapping
    mapping = {}
    idx = 0
    offset = 0
    for line in doc:
        line = line.strip().split()
        # non-empty lines
        if len(line) >= 3:
            token = line[0]
            mapping[offset] = idx
            offset += len(line[0])  # len(token)
        idx += 1

    return mapping


def get_offset2tokidx_from_strlist(doc: List[str]) -> Dict[int, int]:
    """
    Create a mapping: character offset -> token index

    """
    # create mapping
    mapping = {}
    idx = 0
    offset = 0
    for token in doc:
        mapping[offset] = idx
        offset += len(token)
        idx += 1

    return mapping
