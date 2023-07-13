# Utilities for splitting documents at positions where they match well
#
# This is useful in order to then apply token-wise alignment to the parts of the
# split documents

from typing import Dict, Generator, List, Tuple
from fuzzysearch import find_near_matches

from textalign import util, translit


class DocSplitter:
    def __init__(
        self,
        tokens_a: List[str],
        tokens_b: List[str],
        max_lev_dist: int = 7,
        subseq_len: int = 7,
        max_len_split: int = 2000,
        step_size: int = 20,  # TODO: maybe change dynamically (e.g. increase after each step)?
        apply_translit: bool = True,
    ):
        """
        A class for splitting documents at positions where they match well

        TODO: Either change the name, the description or the behavior - because
        currently the class does not acutally split the documents, it only gives
        you indices (= the positions where to split the docs).

        """
        # Texts, tokenized
        self.tokens_a: List[str] = tokens_a
        self.tokens_b: List[str] = tokens_b

        # Text B, serialized
        self.b_joined = "".join(self.tokens_b)  # TODO apply directly here or elsewhere?

        # For text B: mapping of offsets to token index
        self.offset2tokidx_b: Dict[int, int] = self._get_offset2tokidx(
            self.tokens_b
        )  # TODO apply directly here or elsewhere?
        self.offset2tokidx_b_keys: List[int] = list(self.offset2tokidx_b.keys())

        # Parameters
        # Maximum Levenshtein distance for fuzzy search
        self.max_lev_dist: int = max_lev_dist
        # Number of tokens from text A to fuzzy search in text B
        self.subseq_len: int = subseq_len
        # Maximum split length (in tokens) for splitting the documents
        self.max_len_split: int = max_len_split
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
        if self.apply_translit:
            return translit.unidecode_ger(pattern)
        return pattern

    def iterfind_split_positions(self) -> Generator[Tuple[int, int], None, None]:
        """
        Generates pairs (start_a, start_b) where start_a [start_b] is the index of the
        first token in tokens_a [tokens_b] that should go in the next split.

        About the index pair (start_a, start_b) we know that, starting at start_a and start_b, there is a token sequence of length `k` in both documents that aligns uniquely well with the other one.

        Use the output as follows: Create a split from tokens_a[prev_start_a:start_a]
        (same for for tokens_b)

        TODO: What if, for some reason, this is still not the best match overall...
        """

        tokidx_a = 0
        tokidx_b = 0

        while tokidx_a <= len(self.tokens_a) - self.max_len_split - self.subseq_len:
            tokidx_a += self.max_len_split

            # Get the candidate token sequence from text a
            pattern_a = self._get_search_pattern(tokidx_a)

            # Get offsets of near matches of pattern_a in b
            # only look at the remaining part of b
            near_matches = find_near_matches(
                pattern_a,
                self.b_joined[tokidx_b:],
                max_l_dist=self.max_lev_dist,
            )

            # Look for a single near match
            while len(near_matches) != 1:
                # Decrease index (look for a matching pattern earlier)
                tokidx_a -= self.step_size

                # TODO: What to do if the index is decreased to be smaller than 0
                # or smaller than the last index
                if tokidx_a < 0:
                    break

                # Generate a new search pattern and look for matches
                pattern_a = self._get_search_pattern(tokidx_a)
                near_matches = find_near_matches(
                    pattern_a,
                    self.b_joined[tokidx_b:],
                    max_l_dist=self.max_lev_dist,
                )
            # ~ while

            # TODO: Could the while loop never end?
            # Possible if none of the pattern candidates have exactly 1 match (either always 0 or multiple)
            # Break the loop after n attemps and say: sorry, this does not work?!

            # Our matching function gave us a character offset, but we need a token index. Use the mapping to get the token index from the offset
            offset_b = near_matches[0].start + tokidx_b
            try:
                tokidx_b = self.offset2tokidx_b[offset_b]
            # If the offset does not match with the beginning of a token in b, i.e. is located within a token, we need to take the find the closest offset
            except KeyError:
                closest_offset_b = util.find_closest(
                    self.offset2tokidx_b_keys, offset_b
                )
                tokidx_b = self.offset2tokidx_b[closest_offset_b]

            yield tokidx_a, tokidx_b
