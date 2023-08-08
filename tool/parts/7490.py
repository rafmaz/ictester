from prototypes import (PackageDIP14_vcc5, Pin, PinType, Test)

class Part7490(PackageDIP14_vcc5):
    name = "7490"
    desc = "Decade counter"
    pin_cfg = {
        1: Pin("CKB", PinType.IN),
        2: Pin("R0(1)", PinType.IN),
        3: Pin("R0(2)", PinType.IN),
        4: Pin("NC", PinType.NC),
        6: Pin("R9(1)", PinType.IN),
        7: Pin("R9(2)", PinType.IN),
        8: Pin("QC", PinType.OUT),
        9: Pin("QB", PinType.OUT),
        11: Pin("QD", PinType.OUT),
        12: Pin("QA", PinType.OUT),
        13: Pin("NC", PinType.NC),
        14: Pin("CKA", PinType.IN),
    }

    default_inputs = [2, 3,  6, 7,  14, 1]
    default_outputs = [11, 8, 9, 12]

    test_count_cka = Test("Count CKA", Test.SEQ, default_inputs, default_outputs,
        body=[
            # reset R0
            [[1, 1,  1, 0,  0, 0], [0, 0, 0, 0]],
            # count CKA
            [[0, 0,  0, 0,  '-', 0], [0, 0, 0, 1]],
            [[0, 0,  0, 0,  '-', 0], [0, 0, 0, 0]],
            [[0, 0,  0, 0,  '-', 0], [0, 0, 0, 1]],
        ]
    )
    test_count_ckb = Test("Count CKB", Test.SEQ, default_inputs, default_outputs,
        body=[
            # reset R0
            [[1, 1,  1, 0,  0, 0], [0, 0, 0, 0]],
            # count CKB
            [[0, 0,  0, 0,  0, '-'], [0, 0, 1, 0]],
            [[0, 0,  0, 0,  0, '-'], [0, 1, 0, 0]],
            [[0, 0,  0, 0,  0, '-'], [0, 1, 1, 0]],
            [[0, 0,  0, 0,  0, '-'], [1, 0, 0, 0]],
            [[0, 0,  0, 0,  0, '-'], [0, 0, 0, 0]],
            # count CKB again to fill bits with 1s
            [[0, 0,  0, 0,  0, '-'], [0, 0, 1, 0]],
            [[0, 0,  0, 0,  0, '-'], [0, 1, 0, 0]],
            [[0, 0,  0, 0,  0, '-'], [0, 1, 1, 0]],
        ]
    )
    test_resets = Test("Resets", Test.SEQ, default_inputs, default_outputs,
        body=[
            # reset R0
            [[1, 1,  1, 0,  0, 0], [0, 0, 0, 0]],
            # count 1 CKA
            [[0, 0,  0, 0,  '-', 0], [0, 0, 0, 1]],
            # count 1 CKB
            [[0, 0,  0, 0,  0, '-'], [0, 0, 1, 1]],
            # no reset
            [[0, 1,  0, 1,  0, 0], [0, 0, 1, 1]],
            [[1, 0,  1, 0,  0, 0], [0, 0, 1, 1]],
            # reset R9
            [[1, 1,  1, 1,  0, 0], [1, 0, 0, 1]],
            # reset R0
            [[1, 1,  0, 0,  0, 0], [0, 0, 0, 0]],
        ]
    )

    tests = [test_count_cka, test_count_ckb, test_resets]
