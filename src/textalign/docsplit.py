# Utilities for splitting documents at positions where they match well
#
# This is useful in order to then apply token-wise alignment to the parts of the
# split documents

from typing import Dict, Generator, List, Tuple

from collections import namedtuple

import fuzzysearch

from textalign import util, translit


SplitPosition = namedtuple("SplitPosition", ["start_a", "end_a", "start_b", "end_b"])


class DocSplitter:
    def __init__(
        self,
        tokens_a: List[str],
        tokens_b: List[str],
        max_len_split: int = 2000,
        subseq_len: int = 7,
        max_lev_dist: int = 7,
        step_size: int = 20,  # TODO: maybe change dynamically (e.g. increase after each step)?
        apply_translit: bool = True,
    ):
        """
        A class for splitting documents at positions where they match well

        A good split position is understood as the beginning of a sequence of
        tokens from the source document, that have a single (that, is neither
        zero, nor multiple) near matching sequence of tokens in the target
        document, i.e. a good local alignment.

        The instance variables specify the behavior of the algorithm to find good
        split positions:

        `max_len_split` : Maximum split length (in tokens) for splitting the
        documents

        `subseq_len` : Number of tokens from text A to fuzzy search in text B. Shorter search patterns lead to more multiple matches. Make sure the value of this parameter fits to the value of `max_lev_dist`

        `max_lev_dist` : Maximum Levenshtein distance for fuzzy search. What is
        a reasonable setting here largely depends on how (dis)similar source and
        target text are and on the length of the search pattern (`subseq_len`). Use a large distance for less similar texts and longer search patterns.

        `step_size` : Step size for setting a new index during the search for a pattern_a

        `apply_translit` : Whether to apply transliteration before fuzzy search

        """
        # Texts, tokenized
        self.tokens_a: List[str] = tokens_a
        self.tokens_b: List[str] = tokens_b

        # Text B, serialized
        self.b_joined = "".join(self.tokens_b)

        # For text B: mapping of offsets to token index
        self.offset2tokidx_b: Dict[int, int] = self._get_offset2tokidx(self.tokens_b)
        self.offset2tokidx_b_keys: List[int] = list(self.offset2tokidx_b.keys())

        # Parameters
        # Maximum split length (in tokens) for splitting the documents
        self.max_len_split: int = max_len_split
        # Number of tokens from text A to fuzzy search in text B
        self.subseq_len: int = subseq_len
        # Maximum Levenshtein distance for fuzzy search
        self.max_lev_dist: int = max_lev_dist
        # Step size for setting a new index during the search for a pattern_a
        self.step_size: int = step_size
        # Apply transliteration before fuzzy search
        self.apply_translit: bool = apply_translit

    @staticmethod
    def _get_offset2tokidx(doc: List[str]) -> Dict[int, int]:
        """
        Create a mapping from a tokenized document: character offset -> token index

        """
        mapping = {}
        idx = 0
        offset = 0
        for token in doc:
            mapping[offset] = idx
            offset += len(token)
            idx += 1

        return mapping

    def _get_search_pattern(self, tokidx_a: int) -> str:
        """Get the candidate token sequence from text a"""
        end = tokidx_a + self.subseq_len
        pattern = "".join(self.tokens_a[tokidx_a:end])
        # TODO remove/replace in the future
        if self.apply_translit:
            return translit.unidecode_ger(pattern)
        return pattern

    def _get_tokidx_from_charidx_b(self, charidx) -> int:
        try:
            tokidx_b = self.offset2tokidx_b[charidx]
        # If the offset does not match with the beginning of a token in b, i.e. is located within a token, we need to find the closest offset
        except KeyError:
            closest_offset = util.find_closest(self.offset2tokidx_b_keys, charidx)
            tokidx_b = self.offset2tokidx_b[closest_offset]
        return tokidx_b

    def find_split_positions(self) -> List[SplitPosition]:
        """
        Returns a list of pairs (start_a, start_b) where start_a [start_b] is the index of the first token in tokens_a [tokens_b] that should go in the next split.

        About the index pair (start_a, start_b) we know that, starting at start_a and start_b, there is a token sequence of length `k` in both documents that aligns uniquely well with the other one.

        Use the output as follows: Create a split from tokens_a[prev_start_a:start_a]
        (same for for tokens_b)
        """

        split_positions = []

        tokidx_a = 0
        tokidx_b = 0
        last_tokidx_a = 0
        last_charidx_b = 0

        while tokidx_a <= len(self.tokens_a) - self.max_len_split - self.subseq_len:
            tokidx_a += self.max_len_split
            # Get the candidate token sequence from text a
            pattern_a = self._get_search_pattern(tokidx_a)

            # Get offsets of near-matches of pattern_a in b
            # only look at the remaining part of b
            near_matches = fuzzysearch.find_near_matches(
                pattern_a,
                self.b_joined[last_charidx_b:],
                max_l_dist=self.max_lev_dist,
            )

            # Look for a single near-match
            while len(near_matches) != 1:
                # Decrease index (= look for a matching pattern earlier in the doc)
                tokidx_a -= self.step_size

                # If we didn't find a match before hitting the last index:
                # Jump up to the next possible position to search for matches
                if tokidx_a <= last_tokidx_a:
                    # Jump back up
                    tokidx_a += self.max_len_split
                    # Set as last index
                    last_tokidx_a = tokidx_a
                    # Jump up one more chunk
                    tokidx_a += self.max_len_split

                if tokidx_a > len(self.tokens_a) - self.max_len_split - self.subseq_len:
                    break

                # Get new search pattern and look for matches
                pattern_a = self._get_search_pattern(tokidx_a)
                near_matches = fuzzysearch.find_near_matches(
                    pattern_a,
                    self.b_joined[last_charidx_b:],
                    max_l_dist=self.max_lev_dist,
                )

            # while-loop finished because there is only a single near match
            else:
                # Our matching function gave us a character offset, but we need a token index. Use the mapping to get the token index from the offset
                charidx_start_b = near_matches[0].start + last_charidx_b
                tokidx_b = self._get_tokidx_from_charidx_b(charidx_start_b)
                charidx_end_b = near_matches[0].end + last_charidx_b
                tokidx_end_b = self._get_tokidx_from_charidx_b(charidx_end_b)

                # Increase by subsequence length, so that we don't end up looking for the same string as in the last iteration again
                last_tokidx_a = tokidx_a + self.subseq_len
                # Increase last character index b by the end of the near match
                last_charidx_b += near_matches[0].end

                # Return start and end token index of a and b
                tokidx_end_a = tokidx_a + self.subseq_len
                split_positions.append(
                    SplitPosition(
                        start_a=tokidx_a,
                        end_a=tokidx_end_a,
                        start_b=tokidx_b,
                        end_b=tokidx_end_b,
                    )
                )

        return split_positions

            yield tokidx_a, tokidx_b

    # def split(self) -> Generator[Tuple[List[str], List[str]], None, None]:
    #     """Generates document splits"""
    #     prev_split_idx_orig = 0
    #     prev_split_idx_norm = 0

    #     # TODO
    #     for idx_a, idx_b in itertools.chain(self.iterfind_split_positions(),[(len(self.tokens_a), len(self.tokens_b))])

    #         split_a = self.tokens_a[idx_a : (idx_a + self.subseq_len)]
    #         split_b = self.tokens_b[idx_b : (idx_b + self.subseq_len)]
    #         yield split_a, split_b
