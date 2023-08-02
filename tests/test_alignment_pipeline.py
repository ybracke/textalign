import textalign
from textalign import AlignmentPipeline


# fake test
def test_alignment_pipeline() -> None:
    f_hist = "tests/testdata/simplicissimus_hist.txt"
    f_norm = "tests/testdata/simplicissimus_norm.txt"
    config = {
        "aligner": {
            "similarity_func": textalign.aligner.levsim_rescored,
            "gap_cost_func": textalign.aligner.decreasing_gap_cost,
            "gap_cost_length_discount": textalign.aligner.length_discount,
            "gap_cost_initial": 0.5,
        },
        "splitter": {
            "max_lev_dist": 3,
            "subseq_len": 7,
            "step_size": 10,
            "max_len_split": 1000,
            "apply_translit": True,
        },
        "serialization": {"drop_unaligned": True},
    }
    print()
    pipeline = AlignmentPipeline(config)
    aligned_sents = pipeline(f_hist, f_norm)

    assert len(pipeline.aligner.tokens_a) == len(pipeline.doc_flat_a)
    assert len(pipeline.aligner.tokens_b) == len(pipeline.doc_flat_b)

    # with open("tests/testdata/out/pipeline.sent.02.out", "w", encoding="utf-8") as f:
    #     for sent in aligned_sents:
    #         sent_hist_ser, sent_norm_ser = sent.serialize(**config["serialization"])
    #         f.write(f"{sent_hist_ser}\n")
    #         f.write(f"{sent_norm_ser}\n")
    #         f.write("\n")
