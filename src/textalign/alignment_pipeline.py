from typing import List, Dict

from .aligner import Aligner

from . import sentences
from .docsplit import DocSplitter
from . import util

import itertools


class AlignmentPipeline:
    def __init__(self, config: Dict = {}):
        self.config: Dict = config
        self.source_file: str
        self.target_file: str
        # self.source_doc: List[util.Token]
        # self.target_doc: List[util.Token]
        self.aligner: Aligner
        self.docsplitter: DocSplitter

    def __call__(
        self, source_file: str, target_file: str
    ) -> List[sentences.AlignedSentence]:
        # 0. Load config
        # TODO 3 versions of the document text -> not good

        # 1. Load files to documents
        self.source_file = source_file
        self.target_file = target_file

        # TODO: generalize for non-WASTE input
        self.source_doc = util.parse_waste_output(self.source_file)
        self.target_doc = util.parse_waste_output(self.target_file)

        # Flat versions of documents (no sentences)
        # TODO should this be an instance variable or not?
        self.source_doc_flat = [tok for sent in self.source_doc for tok in sent]
        self.target_doc_flat = [tok for sent in self.target_doc for tok in sent]

        # List[str] (not List[util.Token]) versions of the flat documents
        # TODO should this be an instance variable or not?
        self.source_doc_flat_strlist = [tok.text for tok in self.source_doc_flat]
        self.target_doc_flat_strlist = [tok.text for tok in self.target_doc_flat]

        # 2. Create an Aligner object for the entire doc
        self.aligner = Aligner()

        # 3. Get split positions of documents
        self.docsplitter = DocSplitter(
            self.source_doc_flat_strlist,
            self.target_doc_flat_strlist,
            **self.config["splitter"],  # kwargs
        )

        # 4. Iterate over split
        prev_split_idx_orig = 0
        prev_split_idx_norm = 0

        # Use chain to append text length as final position to iterator
        # TODO: this will take the entire rest of source and target doc and
        # tries to compute alignment. Even if one of them is much longer than
        # the other
        for (
            split_idx_orig,
            split_idx_norm,
        ) in itertools.chain(
            self.docsplitter.iterfind_split_positions(),
            [(len(self.docsplitter.tokens_a), len(self.docsplitter.tokens_b))],
        ):
            # Select the splits
            split_orig = self.source_doc_flat_strlist[
                prev_split_idx_orig:split_idx_orig
            ]
            split_norm = self.target_doc_flat_strlist[
                prev_split_idx_norm:split_idx_norm
            ]

            # 5. Create Aligner objects for every split
            aligner_split = Aligner(split_orig, split_norm)
            aligner_split.translit_tokens()
            aligner_split.nw_align(**self.config["aligner"])

            # 6. Append the alignment for the split to the large aligner
            self.aligner.extend(aligner_split)

            prev_split_idx_orig = split_idx_orig
            prev_split_idx_norm = split_idx_norm

        # 7. Clean alignments for whole document
        self.aligner.get_bidirectional_alignments()

        # 8. Create sentence-aligned serialization
        # Create a representation where the bitext is
        #   (1) aligned by sentence
        #   (2) serializable (contains whitespace info: `util.Token`)
        start_idxs_hist = util.get_sentence_start_idxs(
            self.source_doc
        )  # List[List[util.Token]]
        aligned_sents = sentences.get_aligned_sentences(
            self.aligner.aligned_tokidxs,  # List[AlignedPair]
            start_idxs_hist,  # List[int]
            self.source_doc_flat,  # List[util.Token]
            self.target_doc_flat,  # List[util.Token]
            reset_tok_idxs=True,
        )

        return aligned_sents

        # ? Elsewhere - create serialization ans save to file
