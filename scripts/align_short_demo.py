import textalign

from typing import List

# 1. Algin with aligner
f_hist = "tests/testdata/simplicissimus_hist.txt"
f_norm = "tests/testdata/simplicissimus_norm.txt"
with open(f_hist, "r", encoding="utf-8") as f:
    hist = f.read()
with open(f_norm, "r", encoding="utf-8") as f:
    norm = f.read()

hist = [line.split()[0] for line in hist.split("\n") if len(line.split())]
norm = [line.split()[0] for line in norm.split("\n") if len(line.split())]

aligner = textalign.Aligner(hist, norm)
kwargs = {
    "similarity_func": textalign.aligner.jaro_rescored,
    "gap_cost_func": textalign.aligner.decreasing_gap_cost,
    "gap_cost_initial": 1,
}
aligner.get_bidirectional_alignments(translit_func=textalign.translit.unidecode_ger, **kwargs)

aligned_pairs = aligner.get_aligned_pairs()



# 2. Create a representation where the bitext is
#   (1) aligned by sentence
#   (2) serialized

doc_hist = textalign.util.parse_waste_output(f_hist)
doc_norm = textalign.util.parse_waste_output(f_norm)

start_idxs_hist = textalign.util.get_sentence_start_idxs(doc_hist)

sents_aligned_tokidxs = textalign.sentences.split_alignment_into_sentences(aligned_pairs, start_idxs_hist)

# flatten from List[List[Token]] to List[Token]
doc_hist = [tok for sent in doc_hist for tok in sent ] 
doc_norm = [tok for sent in doc_norm for tok in sent ] 

aligned_sents = textalign.sentences.serialize_sentence_alignments(
    sents_aligned_tokidxs,
    doc_hist,
    doc_norm,
    drop_unaligned = True
)

import pprint
pprint.pprint(aligned_sents)