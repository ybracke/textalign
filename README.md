# README

Package for aligning two (similar) tokenized versions of a text. 


## Ablauf

1. Tokenisierung beider Texte (`tokens_orig: List[str]` und `tokens_hist: List[str]`) und merken der Satzgrenzen des orig-Textes in einer Liste `sent_start_idxs: List[int]`, z.B. `[1,10,28]`, ints geben Tokenindex an, an dem ein Satz beginnt.
2. Tokenweise Alignierung (z.B. mit Needleman-Wunsch). Ergebnis: `tok_alignments: List[Union[int,None]]`, z.B. `[1,None,2,4,...]`. Position `i` von `tok_alignments` gibt an, dass das `i`-te orig-Token mit dem norm-Token an Position `j =tok_alignments[i]` aligniert ist.  
Voraussetzung für eine korrekte Liste: Muss per sliding window über norm/orig erstellt worden sein. Damit das funktioniert, dürfen nicht *zu* große Passagen in orig oder norm fehlen, die im anderen Text vorhanden sind.
3. Optional: Nachkorrektur der Alginierung #TODO
4. Aus Satzindizes und Tokenalignierung alignierte Sätze machen. 

## Klasse `Aligner`

* Das macht die Klasse **nicht**:
  * Tokenisierung
* Das macht die Klasse vielleicht:
  * Re-serialisierung der Sätze (Leerzeichen da einfügen, wo im Original welche waren, siehe `util/serialize`).
  * Aus Satzindizes und Tokenalignierung (s.u.) alignierte Sätze erzeugen.
* Das kann die Klasse:
  * Tokenweise Alignierung erzeugen, z.B. mit Needleman-Wunsch
  * Nachkorrektur der Alignierungen: 
    * NW-Algorithmus erzeugt eine 1:1 (oder 0:1/1:0) Zuordnung von Tokens. Es gibt aber auch n:1 oder 1:n-Zuordnungen (`in folge dessen` <-> `infolgedessen`). Diese müssen aus den 1:1-Zuordnungen erzeugt werden.
`Aligner`

### Instanzvariablen

* tokens_a (oder tokens_orig) `List[str]`
  * muss man anderweitig erzeugt haben
* tokens_b (oder tokens_norm) `List[str]`
  * muss man anderweitig erzeugt haben
* tok_alignments
  * `List[Tuple[Union[int,None],Union[int,None]]]`, z.B. `[(0,0),(1,None),(2,1),(None,2),...]`. 
  * `tok_alignments` hat die Länge des erzeugten Alignments: diese ist höchstens `len(tokens_a)+len(tokens_b)` (wenn es überhaupt keine Übereinstimmung gäbe und die günstigste Alignierung darin bestünde nur indels vorzunehmen), und mindestens `max(len(tokens_a),len(tokens_b))` also die Länge der längeren Tokensequenz (z.B. wenn eine Seq ein Substring der anderen ist: nur keep-Operationen und dann ggf. indel bis zur Länge der längeren Sequenz).
  * Die ints in den Paaren sind Tokenindizes auf tokens in tokens_a und tokens_b. Wenn `None`, ist eine indel-Zuordnung vorgenommen worden. D.h. es handelt sich entweder um Text ohne Entsprechung im anderen Text, z.B. eine fehlende Überschrift, Seitenzahl, Editorennotiz, ... **oder** um split/merge-Fälle wie (`(in,folge,dessen)` <-> `infolgedessen` oder `gehts`<-> `(geht,es)`)
* tok_alignments_cleaned
  * `List[Tuple[Union[int,None],Union[int,None]]]` oder `List[Tuple[int,int]]`
  * Bereinigte version von `tok_alignments`
  * None-Mappings wurden behandelt: auf einer oder beiden Seiten der Paare gibt es kein `None` mehr. Entweder aufgelöst oder gelöscht.



## Initialize git repo
```bash
git init
```

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

