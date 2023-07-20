import textalign
from textalign import AlignmentPipeline


def test_alignment_pipeline() -> None:
    f_hist = "tests/testdata/simplicissimus_hist.h200.txt"
    f_norm = "tests/testdata/simplicissimus_norm.h200.txt"
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
            "max_len_split": 100,
            "apply_translit": True,
        },
        "serialization": {"drop_unaligned": True},
    }
    print()
    pipeline = AlignmentPipeline(config)
    aligned_sents = pipeline(f_hist, f_norm)

    assert len(pipeline.aligner.tokens_a) == len(pipeline.source_doc_flat)
    assert len(pipeline.aligner.tokens_b) == len(pipeline.target_doc_flat)

    for sent in aligned_sents:
        sent_hist_ser, sent_norm_ser = sent.serialize()  # **config["serialization"])
        print(sent_hist_ser)
        print(sent_norm_ser)
