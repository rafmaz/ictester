from binvec import BV
from prototypes import (PackageDIP14, Pin, PinType, Test)

class Part7453(PackageDIP14):
    name = "7453"
    desc = "Expandable 4-wide, 2-input And-Or-Invert gate"
    pin_cfg = {
        1: Pin("A1", PinType.IN),
        2: Pin("B1", PinType.IN),
        3: Pin("B2", PinType.IN),
        4: Pin("C1", PinType.IN),
        5: Pin("C2", PinType.IN),
        6: Pin("NC", PinType.IN),  # defined as IN for the test to fail when 74H53 is tested as 7453
        8: Pin("~Y", PinType.OUT),
        9: Pin("D1", PinType.IN),
        10: Pin("D2", PinType.IN),
        11: Pin("X", PinType.NC),
        12: Pin("~X", PinType.NC),
        13: Pin("A2", PinType.IN),
    }

    missing_tests = "Gate expansion is not tested"
    # 7453 outputs, although TTL,  are a tad slow with no serious load
    read_delay_us = 0.4


    test_async = Test("Asynchronous operation", Test.LOGIC,
        params=list(round(read_delay_us/0.2).to_bytes(2, 'little')),
        inputs=[1, 13, 2, 3, 4, 5, 6, 9, 10],
        outputs=[8],
        loops=256,
        body=lambda: [
            [
                [*ab, *cd, *ef, 0, *gh], # '0' inserted for NC input 6
                ~(ab.vand() | cd.vand() | ef.vand() | gh.vand())
            ]
            for ab in BV.range(0, 4)
            for cd in BV.range(0, 4)
            for ef in BV.range(0, 4)
            for gh in BV.range(0, 4)
        ]
    )

    tests = [test_async]
