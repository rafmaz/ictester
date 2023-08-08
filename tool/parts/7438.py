from prototypes import (Pin, PinType, partimport)

class Part7438(partimport("7400")):
    name = "7438"
    desc = "Quad 2-input positive-NAND buffers with open collector outputs"
    pin_cfg = {
        1: Pin("1A", PinType.IN),
        2: Pin("1B", PinType.IN),
        3: Pin("1Y", PinType.OC),
        4: Pin("2A", PinType.IN),
        5: Pin("2B", PinType.IN),
        6: Pin("2Y", PinType.OC),
        8: Pin("3Y", PinType.OC),
        9: Pin("3A", PinType.IN),
        10: Pin("3B", PinType.IN),
        11: Pin("4Y", PinType.OC),
        12: Pin("4A", PinType.IN),
        13: Pin("4B", PinType.IN),
    }
