from textalign import docsplit


def test_docsplit_iterfind_split_positions() -> None:

    tokens_a = ['Um', 'den', 'Vorrath', 'grüner', 'Olivenäſte', '.', 'Den', 'er', 
              'ſich', 'zur', 'Seite', 'hatte', 'hinlegen', 'laſſen', '.', 'Allmählig', 
              'in', 'die', 'Flamme', 'zu', 'ſchieben', '.']
    tokens_b = ['Um', 'den', 'Vorrat', 'grüner', 'Olivenäste', '.', 'Den', 'er', 
              'sich', 'zur', 'Seite', 'hatte', 'hinlegen', 'lassen', '.', 'Allmählich', 
              'in', 'die', 'Flamme', 'zu', 'schieben', '.']

    docsplitter = docsplit.DocSplitter(tokens_a, tokens_b, max_lev_dist=2, subseq_len=3, step_size=1, max_len_split=5)

    print()
    for idx_a, idx_b in docsplitter.iterfind_split_positions():
        print(idx_a, idx_b)
        pass

    assert True


def test_docsplit_iterfind_split_positions_realdoc() -> None:

    f_hist = "tests/testdata/simplicissimus_hist.txt"
    f_norm = "tests/testdata/simplicissimus_norm.txt"
    with open(f_hist, "r", encoding="utf-8") as f:
        hist = f.read()
    with open(f_norm, "r", encoding="utf-8") as f:
        norm = f.read()

    hist = [line.split()[0] for line in hist.split("\n") if len(line.split())]
    norm = [line.split()[0] for line in norm.split("\n") if len(line.split())]

    docsplitter = docsplit.DocSplitter(hist, norm, max_lev_dist=3, subseq_len=7, step_size=100, max_len_split=1000)

    pairs = []
    for idx_a, idx_b in docsplitter.iterfind_split_positions():
        pairs.append((idx_a, idx_b))

    for (idx_a, idx_b) in pairs:
        a = hist[idx_a:idx_a+7]
        b = norm[idx_b:idx_b+7]
        print(f"Matching:\n{a}\n{b}\n")

    assert True

    



def test_find_closest() -> None:
    # Driver code
    arr = [1, 2, 4, 5, 6, 7, 8, 9]
    target = 11
    closest = docsplit.find_closest(arr, target)
    assert closest == 9
    target = 7
    closest = docsplit.find_closest(arr, target)
    assert closest == 7


