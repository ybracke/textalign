from typing import Dict, List

from .aligner import Aligner

from . import sentences
from .docsplit import DocSplitter
from . import util


class AlignmentPipeline:
    def __init__(self, config: Dict = {}):
        self.config: Dict = config
        self.file_a: str
        self.file_b: str
        self.doc_a: List[List[util.Token]]
        self.doc_b: List[List[util.Token]]
        self.doc_flat_a: List[util.Token]
        self.doc_flat_b: List[util.Token]
        self.aligner: Aligner
        self.docsplitter: DocSplitter

    def __call__(self, file_a: str, file_b: str) -> List[sentences.AlignedSentence]:
        # 1. Load files to documents
        self.file_a = file_a
        self.file_b = file_b

        # Sentencized versions of docs: List[List[util.Token]]
        # TODO: generalize to non-WASTE input
        self.doc_a = util.parse_waste_output(self.file_a)
        self.doc_b = util.parse_waste_output(self.file_b)

        # Flat versions of docs (no sentences): List[util.Token]
        self.doc_flat_a = [tok for sent in self.doc_a for tok in sent]
        self.doc_flat_b = [tok for sent in self.doc_b for tok in sent]

        # 2. Create an Aligner object for the entire doc
        self.aligner = Aligner()

        # 3. Get split positions of documents
        self.docsplitter = DocSplitter(
            [tok.text for tok in self.doc_flat_a],  # List[str]
            [tok.text for tok in self.doc_flat_b],  # List[str]
            **self.config["splitter"],  # kwargs
        )

        # 4. Iterate over splits
        for split_a, split_b in self.docsplitter.split():
            # 5. Create Aligner objects for every split
            aligner_split = Aligner(split_a, split_b)
            aligner_split.translit_tokens(self.config["translit_func"])
            aligner_split.nw_align(**self.config["aligner"])

            # 6. Append the alignment for the split to the large aligner
            self.aligner.extend(aligner_split)

        # 7. Clean alignments for whole document
        self.aligner.get_bidirectional_alignments()

        # 8. Create sentence-aligned serialization
        # Create a representation where the bitext is
        #   (1) aligned by sentence
        #   (2) serializable (contains whitespace info: `util.Token`)
        start_idxs_a = util.get_sentence_start_idxs(self.doc_a)
        aligned_sents = sentences.get_aligned_sentences(
            self.aligner.aligned_tokidxs,  # List[AlignedPair]
            start_idxs_a,  # List[int]
            self.doc_flat_a,  # List[util.Token]
            self.doc_flat_b,  # List[util.Token]
            reset_tok_idxs=True,
        )

        return aligned_sents
