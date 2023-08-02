# `textalign`

Package for aligning two (similar) tokenized versions of a text. 

The package provides the following functionality:  
(1) Token alignment for two texts
(2) Splitting texts at positions where they align well
(3) Creating sentence alignments from the tokenized alignments


## In a nutshell

The alignment of longer texts is achieved by, first, (1) splitting the documents at
positions where they align well. (2) Next the resulting shorter text sequences are
aligned token-wise. (3) After that, the prelimenary alignments are joined back
together and cleaned. (4) Optionally, the text can then be serialized back to
sentence strings, giving us aligned sentence pairs.

`textalign.AlignmentPipeline` provides all of the above functionality. The individual aspects are provided by other modules of the package.


## Requirements

Python3.10+

See `requirements.txt`

Set up virtual environment like this:

```bash
python3 -m venv .venv 
source .venv/bin/activate 
pip install --upgrade pip 
pip install -r requirements.txt 
pip install -r requirements-dev.txt
```


## Scripts

The script `align_short_demo.py` contains the code for aligning a short(ish) text, without splitting it first.

For aligning two versions of a longer text, refer to `test_alignment_pipeline.py` for the moment. Here we use the `AlignmentPipeline` (see [below](#pipeline)). This entails steps (1-4) described [above](#in-a-nutshell).


## Details

### Token-wise alignment with `Aligner`

Class to create a token-wise alignment (e.g. with Needleman-Wunsch algorithm). 

Prerequisite for a correct alignment: Must have been created by sliding window via norm/orig. For this to work, there must not be *too* large passages missing from orig or norm that are present in the other text.

Post-correction of alignments: 
  * Needleman-Wunsch algorithm generates a 1:1 (or 0:1/1:0) alignment of tokens. However, there are also n:1 or 1:n assignments (`in consequence of which` <-> `in consequence of which`). These must be generated from the 1:1 assignments.

#### Instance variables

* `tokens_a`: `List[str]`
* `tokens_b`: `List[str]`
* `tok_alignments` nach Anwendung von `clean_alignments`
  * `List[textalign.AlignedPair]`, z.B. `[(a=0,b=0),(a=1,b=None),(a=2,b=1),(a=None,b=2),...]`. 
  * `aligned_tokidxs` hat die Länge des erzeugten Alignments: diese ist höchstens `len(tokens_a)+len(tokens_b)` (wenn es überhaupt keine Übereinstimmung gäbe und die günstigste Alignierung darin bestünde, nur inserts/deletions ("indel") vorzunehmen), und mindestens `max(len(tokens_a),len(tokens_b))` also die Länge der längeren Tokensequenz (z.B. wenn eine Seq ein Substring der anderen ist: nur keep-Operationen und dann ggf. indels bis zur Länge der längeren Sequenz).
  * Die ints in den Paaren sind Tokenindizes auf tokens in `tokens_a` und `tokens_b`. Wenn `None`, ist eine indel-Zuordnung vorgenommen worden. D.h. es handelt sich entweder um Text ohne Entsprechung im anderen Text, z.B. eine fehlende Überschrift, Seitenzahl, Editorennotiz, ... **oder** um split/merge-Fälle wie (`(in,folge,dessen)` <-> `infolgedessen` oder `gehts`<-> `(geht,es)`)
* `tok_alignments` nach Anwendung von `clean_alignments`
  * `None`-Mappings wurden behandelt: auf einer oder beiden Seiten der Paare gibt es kein `None` mehr. Entweder aufgelöst oder gelöscht.


### Document-splitting with `DocSplitter`

Utilities for splitting documents at positions where they match well. Useful for creating well-alignable parts of two documents. This way, apply token-wise alignment can be computed on shorter passages, saving time and memory.


### Sentence serialization with `sentences`

Re-serialise the sentences (insert spaces where they were in the original).

1. we need both texts in tokenised form (`tokens_orig: List[str]` and `tokens_hist: List[str]`) and store the sentence boundaries of the orig text in a list `sent_start_idxs: List[int]`, e.g. `[1,10,28]`, ints indicate the token index where a sentence starts.
2. we need a token alignment, created with `Aligner`
3. make aligned sentences from sentence indices and token alignment.

### Workflow with `AlignmentPipeline`

Initialize a pipeline with a config file in YAML. Refer to the `config.yaml` in the root directory of this project and to the test script `test_alignment_pipeline.py` for examples.

Call the pipeline object with two files containing tokenized documents. TODO: Currently, only [WASTE](https://kaskade.dwds.de/waste/about.perl)-style input files are supported.

WASTE format:

```txt
Solchen	1091 7
naͤrꝛiſchen	1099 15
Leuten	1115 6
nun	1122 3
/	1125 1	[$(]
mag	1127 3
ich	1131 3
mich	1135 4
nicht	1140 5
```

A pipeline call returns an object of type `List[AlignedSentences]`, based on the sentences in the source text. For each sentence in the source text, we get the tokens from the source text, the aligned or unaligned intervening tokens from the target text and alignment mapping between the two. 
This can be used to create a representation of the document's sentence alignment with serialized sentences, e.g. in JSON format, like:

```json
{
  "orig": "(du moͤgſt wol Eſelsleben ſagen) in welchem man ſich auch nichts umb die Medicin bekuͤmmert.",
  "norm": "(du mögst wohl Eselsleben sagen) in welchem man sich auch nichts um die Medizin bekümmert."
}
