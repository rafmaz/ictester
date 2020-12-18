import sys
import inspect
from functools import reduce
from prototypes import (Test, Pin, PartDIP14, PartDIP16, PartDIP24)


# ------------------------------------------------------------------------
def bin2vec(val, bitlen):
    return [
        (val >> (bitlen-pos-1)) & 1
        for pos in range(0, bitlen)
    ]


# ------------------------------------------------------------------------
def binary_combinator(bitlen):
    return [
        bin2vec(v, bitlen)
        for v in range(0, 2**bitlen)
    ]


# ------------------------------------------------------------------------
def binary_fun_gen(unit_count, vector_len, fun, ofun):
    return [
        [unit_count*v, unit_count*[ofun(reduce(fun, v))]]
        for v in binary_combinator(vector_len)
    ]


# ------------------------------------------------------------------------
class Part7400(PartDIP14):
    name = "7400"
    desc = "Quad 2-input positive-NAND gates"
    pins = [
        Pin(1, "1A", Pin.INPUT),
        Pin(2, "1B", Pin.INPUT),
        Pin(3, "1Y", Pin.OUTPUT),
        Pin(4, "2A", Pin.INPUT),
        Pin(5, "2B", Pin.INPUT),
        Pin(6, "2Y", Pin.OUTPUT),
        Pin(7, "GND", Pin.POWER),
        Pin(8, "3Y", Pin.OUTPUT),
        Pin(9, "3A", Pin.INPUT),
        Pin(10, "3B", Pin.INPUT),
        Pin(11, "4Y", Pin.OUTPUT),
        Pin(12, "4A", Pin.INPUT),
        Pin(13, "4B", Pin.INPUT),
        Pin(14, "VCC", Pin.POWER),
    ]
    tests = [
        Test(
            name="Complete logic",
            inputs=[1, 2, 4, 5, 10, 9, 13, 12],
            outputs=[3, 6, 8, 11],
            ttype=Test.COMB,
            body=binary_fun_gen(4, 2, lambda a, b: a & b, lambda a: not a)
        )
    ]


# ------------------------------------------------------------------------
class Part7402(PartDIP14):
    name = "7402"
    desc = "Quad 2-input positive-NOR gates"
    pins = [
        Pin(1, "1Y", Pin.OUTPUT),
        Pin(2, "1A", Pin.INPUT),
        Pin(3, "1B", Pin.INPUT),
        Pin(4, "2Y", Pin.OUTPUT),
        Pin(5, "2A", Pin.INPUT),
        Pin(6, "2B", Pin.INPUT),
        Pin(7, "GND", Pin.POWER),
        Pin(8, "3A", Pin.INPUT),
        Pin(9, "3B", Pin.INPUT),
        Pin(10, "3Y", Pin.OUTPUT),
        Pin(11, "4A", Pin.INPUT),
        Pin(12, "4B", Pin.INPUT),
        Pin(13, "4Y", Pin.OUTPUT),
        Pin(14, "VCC", Pin.POWER),
    ]
    tests = [
        Test(
            name="Complete logic",
            inputs=[2, 3, 5, 6, 8, 9, 11, 12],
            outputs=[1, 4, 10, 13],
            ttype=Test.COMB,
            body=binary_fun_gen(4, 2, lambda a, b: a | b, lambda a: not a)
        )
    ]


# ------------------------------------------------------------------------
class Part7404(PartDIP14):
    name = "7404"
    desc = "Hex inverters"
    pins = [
        Pin(1, "1A", Pin.INPUT),
        Pin(2, "1Y", Pin.OUTPUT),
        Pin(3, "2A", Pin.INPUT),
        Pin(4, "2Y", Pin.OUTPUT),
        Pin(5, "3A", Pin.INPUT),
        Pin(6, "3Y", Pin.OUTPUT),
        Pin(7, "GND", Pin.POWER),
        Pin(8, "6Y", Pin.OUTPUT),
        Pin(9, "6A", Pin.INPUT),
        Pin(10, "5Y", Pin.OUTPUT),
        Pin(11, "5A", Pin.INPUT),
        Pin(12, "4Y", Pin.OUTPUT),
        Pin(13, "4A", Pin.INPUT),
        Pin(14, "VCC", Pin.POWER),
    ]
    tests = [
        Test(
            name="Complete logic",
            inputs=[1, 3, 5, 9, 11, 13],
            outputs=[2, 4, 6, 8, 10, 12],
            ttype=Test.COMB,
            body=[
                [[0, 0, 0, 0, 0, 0], [1, 1, 1, 1, 1, 1]],
                [[1, 1, 1, 1, 1, 1], [0, 0, 0, 0, 0, 0]]
            ]
        )
    ]


# ------------------------------------------------------------------------
class Part7408(PartDIP14):
    name = "7408"
    desc = "Quad 2-input positive-AND gates"
    pins = [
        Pin(1, "1A", Pin.INPUT),
        Pin(2, "1B", Pin.INPUT),
        Pin(3, "1Y", Pin.OUTPUT),
        Pin(4, "2A", Pin.INPUT),
        Pin(5, "2B", Pin.INPUT),
        Pin(6, "2Y", Pin.OUTPUT),
        Pin(7, "GND", Pin.POWER),
        Pin(8, "3Y", Pin.OUTPUT),
        Pin(9, "3A", Pin.INPUT),
        Pin(10, "3B", Pin.INPUT),
        Pin(11, "4Y", Pin.OUTPUT),
        Pin(12, "4A", Pin.INPUT),
        Pin(13, "4B", Pin.INPUT),
        Pin(14, "VCC", Pin.POWER),
    ]
    tests = [
        Test(
            name="Complete logic",
            inputs=[1, 2, 4, 5, 10, 9, 13, 12],
            outputs=[3, 6, 8, 11],
            ttype=Test.COMB,
            body=binary_fun_gen(4, 2, lambda a, b: a & b, lambda a: a)
        )
    ]


# ------------------------------------------------------------------------
class Part7410(PartDIP14):
    name = "7410"
    desc = "Triple 3-input positive-NAND gates"
    pins = [
        Pin(1, "1A", Pin.INPUT),
        Pin(2, "1B", Pin.INPUT),
        Pin(3, "2A", Pin.INPUT),
        Pin(4, "2B", Pin.INPUT),
        Pin(5, "2C", Pin.INPUT),
        Pin(6, "2Y", Pin.OUTPUT),
        Pin(7, "GND", Pin.POWER),
        Pin(8, "3Y", Pin.OUTPUT),
        Pin(9, "3A", Pin.INPUT),
        Pin(10, "3B", Pin.INPUT),
        Pin(11, "3C", Pin.INPUT),
        Pin(12, "1Y", Pin.OUTPUT),
        Pin(13, "1C", Pin.INPUT),
        Pin(14, "VCC", Pin.POWER),
    ]

    tests = [
        Test(
            name="Complete logic",
            inputs=[1, 2, 13, 3, 4, 5, 9, 10, 11],
            outputs=[12, 6, 8],
            ttype=Test.COMB,
            body=binary_fun_gen(3, 3, lambda a, b: a & b, lambda a: not a)
        )
    ]


# ------------------------------------------------------------------------
class Part7413(PartDIP14):
    name = "7413"
    desc = "Dual 4-input positive-NAND Schmitt triggers"
    pins = [
        Pin(1, "1A", Pin.INPUT),
        Pin(2, "1B", Pin.INPUT),
        Pin(3, "NC", Pin.NC),
        Pin(4, "1C", Pin.INPUT),
        Pin(5, "1D", Pin.INPUT),
        Pin(6, "1Y", Pin.OUTPUT),
        Pin(7, "GND", Pin.POWER),
        Pin(8, "2Y", Pin.OUTPUT),
        Pin(9, "2A", Pin.INPUT),
        Pin(10, "2B", Pin.INPUT),
        Pin(11, "NC", Pin.NC),
        Pin(12, "2C", Pin.INPUT),
        Pin(13, "2D", Pin.INPUT),
        Pin(14, "VCC", Pin.POWER),
    ]

    tests = [
        Test(
            name="Complete logic",
            inputs=[1, 2, 4, 5, 13, 12, 10, 9],
            outputs=[6, 8],
            ttype=Test.COMB,
            body=binary_fun_gen(2, 4, lambda a, b: a & b, lambda a: not a)
        )
    ]


# ------------------------------------------------------------------------
class Part7420(Part7413):
    name = "7420"
    desc = "Dual 4-input positive-NAND gates"


# ------------------------------------------------------------------------
class Part7430(PartDIP14):
    name = "7430"
    desc = "8-input positive-NAND gate"
    pins = [
        Pin(1, "A", Pin.INPUT),
        Pin(2, "B", Pin.INPUT),
        Pin(3, "C", Pin.INPUT),
        Pin(4, "D", Pin.INPUT),
        Pin(5, "E", Pin.INPUT),
        Pin(6, "F", Pin.INPUT),
        Pin(7, "GND", Pin.POWER),
        Pin(8, "Y", Pin.OUTPUT),
        Pin(9, "NC", Pin.NC),
        Pin(10, "NC", Pin.NC),
        Pin(11, "G", Pin.INPUT),
        Pin(12, "H", Pin.INPUT),
        Pin(13, "NC", Pin.NC),
        Pin(14, "VCC", Pin.POWER),
    ]

    tests = [
        Test(
            name="Complete logic",
            inputs=[1, 2, 3, 4, 5, 6, 11, 12],
            outputs=[8],
            ttype=Test.COMB,
            body=binary_fun_gen(1, 8, lambda a, b: a & b, lambda a: not a)
        )
    ]


# ------------------------------------------------------------------------
class Part7432(PartDIP14):
    name = "7432"
    desc = "Quad 2-input positive-OR gates"
    pins = [
        Pin(1, "1A", Pin.INPUT),
        Pin(2, "1B", Pin.INPUT),
        Pin(3, "1Y", Pin.OUTPUT),
        Pin(4, "2A", Pin.INPUT),
        Pin(5, "2B", Pin.INPUT),
        Pin(6, "2Y", Pin.OUTPUT),
        Pin(7, "GND", Pin.POWER),
        Pin(8, "3Y", Pin.OUTPUT),
        Pin(9, "3A", Pin.INPUT),
        Pin(10, "3B", Pin.INPUT),
        Pin(11, "4Y", Pin.OUTPUT),
        Pin(12, "4A", Pin.INPUT),
        Pin(13, "4B", Pin.INPUT),
        Pin(14, "VCC", Pin.POWER),
    ]
    tests = [
        Test(
            name="Complete logic",
            inputs=[1, 2, 4, 5, 10, 9, 13, 12],
            outputs=[3, 6, 8, 11],
            ttype=Test.COMB,
            body=binary_fun_gen(4, 2, lambda a, b: a | b, lambda a: a)
        )
    ]


# ------------------------------------------------------------------------
class Part7437(Part7400):
    name = "7437"
    desc = "Quad 2-input positive-NAND buffers"


# ------------------------------------------------------------------------
class Part7474(PartDIP14):
    name = "7474"
    desc = "Dual D-type positive-edge-triggered flip-flops with preset and clear"
    pins = [
        Pin(1, "~1CLR", Pin.INPUT),
        Pin(2, "1D", Pin.INPUT),
        Pin(3, "1CLK", Pin.INPUT),
        Pin(4, "~1PRE", Pin.INPUT),
        Pin(5, "1Q", Pin.OUTPUT),
        Pin(6, "~1Q", Pin.OUTPUT),
        Pin(7, "GND", Pin.POWER),
        Pin(8, "~2Q", Pin.OUTPUT),
        Pin(9, "2Q", Pin.OUTPUT),
        Pin(10, "~2PRE", Pin.INPUT),
        Pin(11, "2CLK", Pin.INPUT),
        Pin(12, "2D", Pin.INPUT),
        Pin(13, "~2CLR", Pin.INPUT),
        Pin(14, "VCC", Pin.POWER),
    ]
    test_sync = Test(
        name="Synchronous operation",
        inputs=[1, 4, 2, 3, 13, 10, 12, 11],
        outputs=[5, 6, 9, 8],
        ttype=Test.SEQ,
        body=[
            [[1, 1, 0, 0,  1, 1, 0, 0], [0, 0,  0, 0]],
            [[1, 1, 0, 1,  1, 1, 0, 1], [0, 1,  0, 1]],
            [[1, 1, 1, 0,  1, 1, 1, 0], [0, 0,  0, 0]],
            [[1, 1, 1, 1,  1, 1, 1, 1], [1, 0,  1, 0]],
        ]
    )
    test_async = Test(
        name="Asynchronous operation",
        inputs=[1, 4, 2, 3, 13, 10, 12, 11],
        outputs=[5, 6, 9, 8],
        ttype=Test.SEQ,
        body=[
            [[0, 1, 0, 0,  0, 1, 0, 0], [0, 1,  0, 1]],
            [[1, 0, 0, 0,  1, 0, 0, 0], [1, 0,  1, 0]],
        ]
    )
    tests = [test_sync, test_async]


# ------------------------------------------------------------------------
class Part7486(PartDIP14):
    name = "7486"
    desc = "Quad 2-input exclusive-OR gates"
    pins = [
        Pin(1, "1A", Pin.INPUT),
        Pin(2, "1B", Pin.INPUT),
        Pin(3, "1Y", Pin.OUTPUT),
        Pin(4, "2A", Pin.INPUT),
        Pin(5, "2B", Pin.INPUT),
        Pin(6, "2Y", Pin.OUTPUT),
        Pin(7, "GND", Pin.POWER),
        Pin(8, "3Y", Pin.OUTPUT),
        Pin(9, "3A", Pin.INPUT),
        Pin(10, "3B", Pin.INPUT),
        Pin(11, "4Y", Pin.OUTPUT),
        Pin(12, "4A", Pin.INPUT),
        Pin(13, "4B", Pin.INPUT),
        Pin(14, "VCC", Pin.POWER),
    ]
    test_all = Test(
        name="Complete logic",
        inputs=[1, 2, 4, 5, 10, 9, 13, 12],
        outputs=[3, 6, 8, 11],
        ttype=Test.COMB,
        body=binary_fun_gen(4, 2, lambda a, b: a ^ b, lambda a: a)
    )
    tests = [test_all]


# ------------------------------------------------------------------------
class Part7495(PartDIP14):
    name = "7495"
    desc = "4-bit parallel-access shift registers"
    pins = [
        Pin(1, "SER", Pin.INPUT),
        Pin(2, "A", Pin.INPUT),
        Pin(3, "B", Pin.INPUT),
        Pin(4, "C", Pin.INPUT),
        Pin(5, "D", Pin.INPUT),
        Pin(6, "MODE", Pin.INPUT),
        Pin(7, "GND", Pin.POWER),
        Pin(8, "CLK2", Pin.INPUT),
        Pin(9, "CLK1", Pin.INPUT),
        Pin(10, "QD", Pin.OUTPUT),
        Pin(11, "QC", Pin.OUTPUT),
        Pin(12, "QB", Pin.OUTPUT),
        Pin(13, "QA", Pin.OUTPUT),
        Pin(14, "VCC", Pin.POWER),
    ]
    test_load = Test(
        name="Parallel load",
        inputs=[6, 8, 9, 1, 2, 3, 4, 5],
        outputs=[13, 12, 11, 10],
        ttype=Test.SEQ,
        body=[
            [[1, 1, 0, 0, 1, 1, 1, 1], [1, 1, 1, 1]],
            [[1, 0, 0, 0, 1, 1, 1, 1], [1, 1, 1, 1]],
            [[1, 1, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0]],
            [[1, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0]],
        ]
    )
    test_rshift = Test(
        name="Right Shift",
        inputs=[6, 8, 9, 1, 2, 3, 4, 5],
        outputs=[13, 12, 11, 10],
        ttype=Test.SEQ,
        body=[
            # set known starting value
            [[1, 1, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0]],
            [[1, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0]],

            [[0, 0, 1, 0, 0, 0, 0, 0], [0, 0, 0, 0]],
            [[0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0]],
            [[0, 0, 1, 1, 0, 0, 0, 0], [1, 0, 0, 0]],
            [[0, 0, 0, 1, 0, 0, 0, 0], [1, 0, 0, 0]],
            [[0, 0, 1, 0, 0, 0, 0, 0], [0, 1, 0, 0]],
            [[0, 0, 0, 0, 0, 0, 0, 0], [0, 1, 0, 0]],
            [[0, 0, 1, 1, 0, 0, 0, 0], [1, 0, 1, 0]],
            [[0, 0, 0, 1, 0, 0, 0, 0], [1, 0, 1, 0]],
            [[0, 0, 1, 0, 0, 0, 0, 0], [0, 1, 0, 1]],
            [[0, 0, 0, 0, 0, 0, 0, 0], [0, 1, 0, 1]],
            [[0, 0, 1, 1, 0, 0, 0, 0], [1, 0, 1, 0]],
            [[0, 0, 0, 1, 0, 0, 0, 0], [1, 0, 1, 0]],
            [[0, 0, 1, 0, 0, 0, 0, 0], [0, 1, 0, 1]],
            [[0, 0, 0, 0, 0, 0, 0, 0], [0, 1, 0, 1]],
            [[0, 0, 1, 0, 0, 0, 0, 0], [0, 0, 1, 0]],
            [[0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 1, 0]],
            [[0, 0, 1, 0, 0, 0, 0, 0], [0, 0, 0, 1]],
            [[0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 1]],
            [[0, 0, 1, 0, 0, 0, 0, 0], [0, 0, 0, 0]],
            [[0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0]],
        ]
    )
    tests = [test_load, test_rshift]


# ------------------------------------------------------------------------
class Part74153(PartDIP16):
    name = "74153"
    desc = "Dual 4-line to 1-line data selectors/multiplexers"
    pins = [
        Pin(1, "~1G", Pin.INPUT),
        Pin(2, "B", Pin.INPUT),
        Pin(3, "1C3", Pin.INPUT),
        Pin(4, "1C2", Pin.INPUT),
        Pin(5, "1C1", Pin.INPUT),
        Pin(6, "1C0", Pin.INPUT),
        Pin(7, "1Y", Pin.OUTPUT),
        Pin(8, "GND", Pin.POWER),
        Pin(9, "2Y", Pin.OUTPUT),
        Pin(10, "2C0", Pin.INPUT),
        Pin(11, "2C1", Pin.INPUT),
        Pin(12, "2C2", Pin.INPUT),
        Pin(13, "2C3", Pin.INPUT),
        Pin(14, "A", Pin.INPUT),
        Pin(15, "~2G", Pin.INPUT),
        Pin(16, "VCC", Pin.POWER),
    ]
    test_all = Test(
        name="Complete logic",
        inputs=[2, 14, 1, 3, 4, 5, 6, 15, 13, 12, 11, 10],
        outputs=[7, 9],
        ttype=Test.COMB,
        body=[
            # output is always "0" when G is high
            [[0, 0,  1,  0, 0, 0, 0,  1,  0, 0, 0, 0], [0, 0]],
            [[0, 1,  1,  0, 0, 0, 0,  1,  0, 0, 0, 0], [0, 0]],
            [[1, 0,  1,  0, 0, 0, 0,  1,  0, 0, 0, 0], [0, 0]],
            [[1, 1,  1,  0, 0, 0, 0,  1,  0, 0, 0, 0], [0, 0]],
            [[0, 0,  1,  1, 1, 1, 1,  1,  1, 1, 1, 1], [0, 0]],
            [[0, 1,  1,  1, 1, 1, 1,  1,  1, 1, 1, 1], [0, 0]],
            [[1, 0,  1,  1, 1, 1, 1,  1,  1, 1, 1, 1], [0, 0]],
            [[1, 1,  1,  1, 1, 1, 1,  1,  1, 1, 1, 1], [0, 0]],

            # selection if G is low
            [[0, 0,  0,  1, 1, 1, 0,  0,  1, 1, 1, 0], [0, 0]],
            [[0, 1,  0,  1, 1, 0, 1,  0,  1, 1, 0, 1], [0, 0]],
            [[1, 0,  0,  1, 0, 1, 1,  0,  1, 0, 1, 1], [0, 0]],
            [[1, 1,  0,  0, 1, 1, 1,  0,  0, 1, 1, 1], [0, 0]],

            [[0, 0,  0,  0, 0, 0, 1,  0,  0, 0, 0, 1], [1, 1]],
            [[0, 1,  0,  0, 0, 1, 0,  0,  0, 0, 1, 0], [1, 1]],
            [[1, 0,  0,  0, 1, 0, 0,  0,  0, 1, 0, 0], [1, 1]],
            [[1, 1,  0,  1, 0, 0, 0,  0,  1, 0, 0, 0], [1, 1]],
        ]
    )
    tests = [test_all]


# ------------------------------------------------------------------------
class Part74181(PartDIP24):
    name = "74181"
    desc = "Arithmetic logic units/function generators"
    pins = [
        Pin(1, "B0", Pin.INPUT),
        Pin(2, "A0", Pin.INPUT),
        Pin(3, "S3", Pin.INPUT),
        Pin(4, "S2", Pin.INPUT),
        Pin(5, "S1", Pin.INPUT),
        Pin(6, "S0", Pin.INPUT),
        Pin(7, "~Cn", Pin.INPUT),
        Pin(8, "M", Pin.INPUT),
        Pin(9, "F0", Pin.OUTPUT),
        Pin(10, "F1", Pin.OUTPUT),
        Pin(11, "F2", Pin.OUTPUT),
        Pin(12, "GND", Pin.POWER),
        Pin(13, "F3", Pin.OUTPUT),
        Pin(14, "A=B", Pin.OUTPUT),
        Pin(15, "X", Pin.OUTPUT),
        Pin(16, "~Cn+4", Pin.OUTPUT),
        Pin(17, "Y", Pin.OUTPUT),
        Pin(18, "B3", Pin.INPUT),
        Pin(19, "A3", Pin.INPUT),
        Pin(20, "B2", Pin.INPUT),
        Pin(21, "A2", Pin.INPUT),
        Pin(22, "B1", Pin.INPUT),
        Pin(23, "A1", Pin.INPUT),
        Pin(24, "VCC", Pin.POWER),
    ]

    # ------------------------------------------------------------------------
    def logic_test_gen(s, name, fun):
        data = [
            [x, y, fun(x, y)]
            for x in range(0, 16)
            for y in range(0, 16)
        ]
        body = [
            [[1] + bin2vec(s, 4) + bin2vec(d[0], 4) + bin2vec(d[1], 4), bin2vec(d[2], 4)]
            for d in data
        ]
        return Test(
            name=name,
            inputs=[8, 3, 4, 5, 6,  19, 21, 23, 2,  18, 20, 22, 1],
            outputs=[13, 11, 10, 9],
            ttype=Test.COMB,
            body=body
        )

    test_a0 = Test(
        name="Arithmetic: F=A",
        inputs=[8, 3, 4, 5, 6,  7,  19, 21, 23, 2,  18, 20, 22, 1],
        outputs=[13, 11, 10, 9,  16],
        ttype=Test.COMB,
        body=[
            # M  S3 S2 S1 S0  ~C  A            B             F           ~Cn+4
            [[0, 0, 0, 0, 0,  1,  0, 0, 0, 0,  0, 0, 0, 0], [0, 0, 0, 0,  1]],
            [[0, 0, 0, 0, 0,  1,  0, 0, 0, 1,  0, 0, 0, 0], [0, 0, 0, 1,  1]],
            [[0, 0, 0, 0, 0,  1,  0, 0, 1, 0,  0, 0, 0, 0], [0, 0, 1, 0,  1]],
            [[0, 0, 0, 0, 0,  1,  0, 0, 1, 1,  0, 0, 0, 0], [0, 0, 1, 1,  1]],
            [[0, 0, 0, 0, 0,  1,  0, 1, 0, 0,  0, 0, 0, 0], [0, 1, 0, 0,  1]],
            [[0, 0, 0, 0, 0,  1,  0, 1, 0, 1,  0, 0, 0, 0], [0, 1, 0, 1,  1]],
            [[0, 0, 0, 0, 0,  1,  0, 1, 1, 0,  0, 0, 0, 0], [0, 1, 1, 0,  1]],
            [[0, 0, 0, 0, 0,  1,  0, 1, 1, 1,  0, 0, 0, 0], [0, 1, 1, 1,  1]],
            [[0, 0, 0, 0, 0,  1,  1, 0, 0, 0,  0, 0, 0, 0], [1, 0, 0, 0,  1]],
            [[0, 0, 0, 0, 0,  1,  1, 0, 0, 1,  0, 0, 0, 0], [1, 0, 0, 1,  1]],
            [[0, 0, 0, 0, 0,  1,  1, 0, 1, 0,  0, 0, 0, 0], [1, 0, 1, 0,  1]],
            [[0, 0, 0, 0, 0,  1,  1, 0, 1, 1,  0, 0, 0, 0], [1, 0, 1, 1,  1]],
            [[0, 0, 0, 0, 0,  1,  1, 1, 0, 0,  0, 0, 0, 0], [1, 1, 0, 0,  1]],
            [[0, 0, 0, 0, 0,  1,  1, 1, 0, 1,  0, 0, 0, 0], [1, 1, 0, 1,  1]],
            [[0, 0, 0, 0, 0,  1,  1, 1, 1, 0,  0, 0, 0, 0], [1, 1, 1, 0,  1]],
            [[0, 0, 0, 0, 0,  1,  1, 1, 1, 1,  0, 0, 0, 0], [1, 1, 1, 1,  1]],

            [[0, 0, 0, 0, 0,  0,  0, 0, 0, 0,  0, 0, 0, 0], [0, 0, 0, 1,  1]],
            [[0, 0, 0, 0, 0,  0,  0, 0, 0, 1,  0, 0, 0, 0], [0, 0, 1, 0,  1]],
            [[0, 0, 0, 0, 0,  0,  0, 0, 1, 0,  0, 0, 0, 0], [0, 0, 1, 1,  1]],
            [[0, 0, 0, 0, 0,  0,  0, 0, 1, 1,  0, 0, 0, 0], [0, 1, 0, 0,  1]],
            [[0, 0, 0, 0, 0,  0,  0, 1, 0, 0,  0, 0, 0, 0], [0, 1, 0, 1,  1]],
            [[0, 0, 0, 0, 0,  0,  0, 1, 0, 1,  0, 0, 0, 0], [0, 1, 1, 0,  1]],
            [[0, 0, 0, 0, 0,  0,  0, 1, 1, 0,  0, 0, 0, 0], [0, 1, 1, 1,  1]],
            [[0, 0, 0, 0, 0,  0,  0, 1, 1, 1,  0, 0, 0, 0], [1, 0, 0, 0,  1]],
            [[0, 0, 0, 0, 0,  0,  1, 0, 0, 0,  0, 0, 0, 0], [1, 0, 0, 1,  1]],
            [[0, 0, 0, 0, 0,  0,  1, 0, 0, 1,  0, 0, 0, 0], [1, 0, 1, 0,  1]],
            [[0, 0, 0, 0, 0,  0,  1, 0, 1, 0,  0, 0, 0, 0], [1, 0, 1, 1,  1]],
            [[0, 0, 0, 0, 0,  0,  1, 0, 1, 1,  0, 0, 0, 0], [1, 1, 0, 0,  1]],
            [[0, 0, 0, 0, 0,  0,  1, 1, 0, 0,  0, 0, 0, 0], [1, 1, 0, 1,  1]],
            [[0, 0, 0, 0, 0,  0,  1, 1, 0, 1,  0, 0, 0, 0], [1, 1, 1, 0,  1]],
            [[0, 0, 0, 0, 0,  0,  1, 1, 1, 0,  0, 0, 0, 0], [1, 1, 1, 1,  1]],
            [[0, 0, 0, 0, 0,  0,  1, 1, 1, 1,  0, 0, 0, 0], [0, 0, 0, 0,  0]],

        ]
    )
    test_a1 = Test(
        name="Arithmetic: F=A|B",
        inputs=[8, 3, 4, 5, 6,  7,  19, 21, 23, 2,  18, 20, 22, 1],
        outputs=[13, 11, 10, 9,  16],
        ttype=Test.COMB,
        body=[
            # M  S3 S2 S1 S0  ~C  A            B             F           ~Cn+4
            [[0, 0, 0, 0, 1,  1,  0, 0, 0, 0,  0, 0, 0, 0], [0, 0, 0, 0,  1]],
            [[0, 0, 0, 0, 1,  1,  0, 0, 0, 0,  1, 1, 1, 1], [1, 1, 1, 1,  1]],
            [[0, 0, 0, 0, 1,  1,  1, 1, 1, 1,  0, 0, 0, 0], [1, 1, 1, 1,  1]],
            [[0, 0, 0, 0, 1,  1,  1, 1, 1, 1,  1, 1, 1, 1], [1, 1, 1, 1,  1]],

            [[0, 0, 0, 0, 1,  0,  0, 0, 0, 0,  0, 0, 0, 0], [0, 0, 0, 1,  1]],
            [[0, 0, 0, 0, 1,  0,  0, 0, 0, 0,  0, 0, 0, 1], [0, 0, 1, 0,  1]],
            [[0, 0, 0, 0, 1,  0,  0, 0, 0, 0,  0, 0, 1, 0], [0, 0, 1, 1,  1]],
            [[0, 0, 0, 0, 1,  0,  0, 0, 0, 0,  0, 1, 0, 0], [0, 1, 0, 1,  1]],
            [[0, 0, 0, 0, 1,  0,  0, 0, 0, 0,  1, 0, 0, 0], [1, 0, 0, 1,  1]],
            [[0, 0, 0, 0, 1,  0,  0, 0, 0, 1,  0, 0, 0, 0], [0, 0, 1, 0,  1]],
            [[0, 0, 0, 0, 1,  0,  0, 0, 1, 0,  0, 0, 0, 0], [0, 0, 1, 1,  1]],
            [[0, 0, 0, 0, 1,  0,  0, 1, 0, 0,  0, 0, 0, 0], [0, 1, 0, 1,  1]],
            [[0, 0, 0, 0, 1,  0,  1, 0, 0, 0,  0, 0, 0, 0], [1, 0, 0, 1,  1]],

            [[0, 0, 0, 0, 1,  0,  0, 0, 0, 0,  1, 1, 1, 1], [0, 0, 0, 0,  0]],
            [[0, 0, 0, 0, 1,  0,  1, 1, 1, 1,  0, 0, 0, 0], [0, 0, 0, 0,  0]],
            [[0, 0, 0, 0, 1,  0,  1, 1, 1, 1,  1, 1, 1, 1], [0, 0, 0, 0,  0]],
        ]
    )
    test_a2 = Test(
        name="Arithmetic: F=A|~B",
        inputs=[8, 3, 4, 5, 6,  7,  19, 21, 23, 2,  18, 20, 22, 1],
        outputs=[13, 11, 10, 9,  16],
        ttype=Test.COMB,
        body=[
            # M  S3 S2 S1 S0  ~C  A            B             F           ~Cn+4
            [[0, 0, 0, 1, 0,  1,  0, 0, 0, 0,  0, 0, 0, 0], [1, 1, 1, 1,  1]],
            [[0, 0, 0, 1, 0,  1,  0, 0, 0, 0,  1, 1, 1, 1], [0, 0, 0, 0,  1]],
            [[0, 0, 0, 1, 0,  1,  1, 1, 1, 1,  0, 0, 0, 0], [1, 1, 1, 1,  1]],
            [[0, 0, 0, 1, 0,  1,  1, 1, 1, 1,  1, 1, 1, 1], [1, 1, 1, 1,  1]],

            [[0, 0, 0, 1, 0,  0,  0, 0, 0, 0,  0, 0, 0, 1], [1, 1, 1, 1,  1]],
            [[0, 0, 0, 1, 0,  0,  0, 0, 0, 0,  0, 0, 1, 0], [1, 1, 1, 0,  1]],
            [[0, 0, 0, 1, 0,  0,  0, 0, 0, 0,  0, 1, 0, 0], [1, 1, 0, 0,  1]],
            [[0, 0, 0, 1, 0,  0,  0, 0, 0, 0,  1, 0, 0, 0], [1, 0, 0, 0,  1]],

            [[0, 0, 0, 1, 0,  0,  0, 0, 0, 0,  0, 0, 0, 0], [0, 0, 0, 0,  0]],
            [[0, 0, 0, 1, 0,  0,  0, 0, 0, 0,  1, 1, 1, 1], [0, 0, 0, 1,  1]],
            [[0, 0, 0, 1, 0,  0,  1, 1, 1, 1,  0, 0, 0, 0], [0, 0, 0, 0,  0]],
            [[0, 0, 0, 1, 0,  0,  1, 1, 1, 1,  1, 1, 1, 1], [0, 0, 0, 0,  0]],
        ]
    )
    test_a3 = Test(
        name="Arithmetic: F=-1",
        inputs=[8, 3, 4, 5, 6,  7,  19, 21, 23, 2,  18, 20, 22, 1],
        outputs=[13, 11, 10, 9,  16],
        ttype=Test.COMB,
        body=[
            # M  S3 S2 S1 S0  ~C  A            B             F           ~Cn+4
            [[0, 0, 0, 1, 1,  1,  0, 0, 0, 0,  0, 0, 0, 0], [1, 1, 1, 1,  1]],
            [[0, 0, 0, 1, 1,  1,  0, 0, 0, 0,  0, 0, 0, 1], [1, 1, 1, 1,  1]],
            [[0, 0, 0, 1, 1,  1,  0, 0, 0, 0,  1, 1, 1, 1], [1, 1, 1, 1,  1]],
            [[0, 0, 0, 1, 1,  1,  1, 1, 1, 1,  0, 0, 0, 0], [1, 1, 1, 1,  1]],
            [[0, 0, 0, 1, 1,  1,  1, 1, 1, 1,  1, 1, 1, 1], [1, 1, 1, 1,  1]],

            [[0, 0, 0, 1, 1,  0,  0, 0, 0, 0,  0, 0, 0, 0], [0, 0, 0, 0,  0]],
            [[0, 0, 0, 1, 1,  0,  0, 0, 0, 0,  0, 0, 0, 1], [0, 0, 0, 0,  0]],
            [[0, 0, 0, 1, 1,  0,  0, 0, 0, 0,  1, 1, 1, 1], [0, 0, 0, 0,  0]],
            [[0, 0, 0, 1, 1,  0,  1, 1, 1, 1,  0, 0, 0, 0], [0, 0, 0, 0,  0]],
            [[0, 0, 0, 1, 1,  0,  1, 1, 1, 1,  1, 1, 1, 1], [0, 0, 0, 0,  0]],
        ]
    )

    tests = [
        logic_test_gen(0, "Logic: F=~A", lambda a, b: ~a),
        logic_test_gen(1, "Logic: F=~(A|B)", lambda a, b: ~(a | b)),
        logic_test_gen(2, "Logic: F=~A&B", lambda a, b: ~a & b),
        logic_test_gen(3, "Logic: F=0", lambda a, b: 0),
        logic_test_gen(4, "Logic: F=~(A&B)", lambda a, b: ~(a & b)),
        logic_test_gen(5, "Logic: F=~B", lambda a, b: ~b),
        logic_test_gen(6, "Logic: F=A^B", lambda a, b: a ^ b),
        logic_test_gen(7, "Logic: F=A&~B", lambda a, b: a & ~b),
        logic_test_gen(8, "Logic: F=~A|B", lambda a, b: ~a | b),
        logic_test_gen(9, "Logic: F=~(A^B)", lambda a, b: ~(a ^ b)),
        logic_test_gen(10, "Logic: F=B", lambda a, b: b),
        logic_test_gen(11, "Logic: F=A&B", lambda a, b: a & b),
        logic_test_gen(12, "Logic: F=1", lambda a, b: 0xf),
        logic_test_gen(13, "Logic: F=A|~B", lambda a, b: a | ~b),
        logic_test_gen(14, "Logic: F=A|B", lambda a, b: a | b),
        logic_test_gen(15, "Logic: F=A", lambda a, b: a),

        test_a0, test_a1, test_a2, test_a3
    ]


# build parts catalog
catalog = {}
for i in inspect.getmembers(sys.modules[__name__]):
    if inspect.isclass(i[1]) and 'pins' in [i[0] for i in inspect.getmembers(i[1])]:
        catalog[i[1].name] = i[1]
