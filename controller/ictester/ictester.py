#!/usr/bin/env python3

import sys
import argparse
import math
import re
import difflib
import logging
import serial.tools.list_ports as listports
from serial.serialutil import SerialException
from colorama import just_fix_windows_console
from colorama import Fore, Back, Style
from struct import unpack

from ictester.test import TestType
from ictester.transport import Transport
from ictester.response import RespType
from ictester.parts import catalog

just_fix_windows_console()

FAIL = Fore.RED + Style.BRIGHT
OK = Fore.GREEN + Style.BRIGHT
WARN = Fore.MAGENTA + Style.BRIGHT
SKIP = Fore.YELLOW + Style.BRIGHT
HI = Fore.WHITE + Style.BRIGHT
LO = Fore.WHITE + Style.DIM
LAB = Fore.BLUE + Style.BRIGHT
ENDC = Style.RESET_ALL

result_color = {
    RespType.HELLO: OK,
    RespType.OK: OK,
    RespType.PASS: OK,
    RespType.FAIL: FAIL,
    RespType.ERR: FAIL,
    RespType.TIMING_ERROR: WARN,
}

logging.basicConfig(format='%(message)s', level=logging.CRITICAL)
logger = logging.getLogger('ictester')

'''
Log levels:
    20 - regular debug
    19 - vector dump
    18 - protocol data
'''

# ------------------------------------------------------------------------
def print_parts(list_tests=False):
    families = {}
    for i in catalog.items():
        family = i[0][0:2]
        if family not in families:
            families[family] = []
        families[family].append(i)

    for family, parts in sorted(families.items()):
        for name, part in sorted(parts, key=lambda x: int(re.sub("74[HSL]+", "74", x[0]))):
            print(f"{name:7s} {part.package_name:6s} {part.desc}")
            if (list_tests):
                for t in part.tests:
                    print(f"  * {t.name} ({len(t.vectors)} vectors)")

# ------------------------------------------------------------------------
def print_part_info(part):
    print(f"Part: {HI}{part.name} ({part.package_name}) - {part.desc}{ENDC}")
    if part.missing_tests:
        print(f"{WARN}WARNING:{ENDC} missing tests: {part.missing_tests}")

# ------------------------------------------------------------------------
def print_vector_chunk(prefix, vector, widths, vector_other=None, color=""):
    print(prefix, end="")
    for n, i in enumerate(vector):
        bitcolor = FAIL if vector_other and i != vector_other[n] else color
        print(f"{bitcolor}{str(i):>{widths[n]+1}}{ENDC}", end="")

# ------------------------------------------------------------------------
def print_vector(label, inputs, outputs, i_width, o_width, i_other=None, o_other=None, color="", separator=""):
    print_vector_chunk(f" {label:<5}", inputs, i_width, i_other, color)
    print_vector_chunk(separator.center(5), outputs, o_width, o_other, color)
    print()

# ------------------------------------------------------------------------
def print_failed_vector(part, test, failed_vector_num, failed_pin_vector, context=3):
    i_failed = [int(failed_pin_vector[pin-1]) for pin in test.inputs]
    o_failed = [int(failed_pin_vector[pin-1]) for pin in test.outputs]

    i_names = [part.pins[pin].name for pin in test.inputs]
    o_names = [part.pins[pin].name for pin in test.outputs]

    i_width = [len(x) for x in i_names]
    o_width = [len(x) for x in o_names]

    print()
    start_vec = max(failed_vector_num - context, 0)
    print_vector("", i_names, o_names, i_width, o_width, color="", separator="->")
    for i in range(start_vec, failed_vector_num+1):
        inputs = [int(x) for x in test.vectors[i].input]
        outputs = [int(x) for x in test.vectors[i].output]
        if i != failed_vector_num:
            print_vector(f"{i}:", inputs, outputs, i_width, o_width, color=LO)
        else:
            print_vector(f"{i}:", i_failed, o_failed, i_width, o_width, inputs, outputs, color=HI)
    print()

# ------------------------------------------------------------------------
def parse_cmd():
    parser = argparse.ArgumentParser(description='IC tester controller')
    parser.add_argument('-d', '--device', default=None, help='Serial port where the IC tester is connected')
    parser.add_argument('-l', '--loops', type=int, default=None, help='Loop count (1..65535)')
    parser.add_argument('-t', '--test', type=int, default=None, help='Test number to run')
    parser.add_argument('-D', '--delay', type=float, default=None, help='additional DUT output read delay in μs (for logic tests only, 13107 μs max, rounded to nearest 0.2 μs)')
    parser.add_argument('-L', '--list', action="store_true", help='List all supported parts')
    parser.add_argument('-A', '--list-all', action="store_true", help='List all supported parts and all tests for each part')
    parser.add_argument('--safety-off', action="store_true", help='Disable safety checks')
    parser.add_argument('-v', '--verbose', action="count", default=0, help='Verbose output. Repeat for even more verbosity')
    parser.add_argument('part', help='Part symbol', nargs='?')
    args = parser.parse_args()

    logger.setLevel(21 - args.verbose)

    if args.test is not None and args.test <= 0:
        parser.error("Test numbers start from 1")

    if args.loops is not None and (args.loops <= 0 or args.loops > 65535):
        parser.error("Loops should be between 1 and 65535")

    if args.delay is not None and (args.delay < 0 or args.delay > 13107):
        parser.error("Delay should be between 0 and 13107")

    if not args.list and not args.list_all and args.part is None:
        parser.error("'part' argument is required")

    return args

# ------------------------------------------------------------------------
def get_part(part_name):
    try:
        part = catalog[part_name]
    except KeyError:
        print(f"Part \"{part_name}\" not found. Use --list to list all supported parts.")
        matches = difflib.get_close_matches(part_name, catalog, n=1, cutoff=0.7)
        if matches:
            matches = ', '.join(matches)
            print(f"Supported part with the most similar name is: {HI}{matches}{ENDC}")
        sys.exit(100)
    return part

# ------------------------------------------------------------------------
def get_serial_port(device):
    # Try searching for ictester
    detected_device = None
    for port in listports.comports():
        if port.manufacturer == "mera400.pl" and port.product == "ictester":
            detected_device = port.device

    serial_port = device if device else detected_device

    # Device not found
    if not serial_port:
        print("No ictester found. Please specify device with --device argument.")
        sys.exit(90)

    return serial_port

# ------------------------------------------------------------------------
# --- Main ---------------------------------------------------------------
# ------------------------------------------------------------------------

def main():
    args = parse_cmd()

    if args.list or args.list_all:
        print_parts(list_tests=args.list_all)
        sys.exit(0)

    part = get_part(args.part.upper())
    serial_port = get_serial_port(args.device)

    try:
        transport = Transport(serial_port, 500000)
    except SerialException as e:
        print(f"Could not open connection to the tester: {e}")
        sys.exit(80)

    part.setup(transport)

    if args.test:
        try:
            run_tests = [part.tests[args.test-1]]
        except IndexError:
            print(f"Test number {args.test} is not available for {part.name}")
            sys.exit(70)
    else:
        run_tests = part.tests

    longest_desc = max(len(t.name) for t in run_tests)

    total_time = 0

    print_part_info(part)
    print()

    tests_failed = 0
    tests_warning = 0
    tests_passed = 0

    print("DUT power up: ", end="")
    resp = part.powerup(transport, args.safety_off)
    vbus = unpack("<h", resp.payload)[0] * 1.6 / 1000
    if resp.response == RespType.OK:
        print(f"{OK}OK{ENDC}, ", end="");
    else:
        print(f"{FAIL}Overcurrent{ENDC}, ", end="")
    print(f"Vbus idle = {HI}{vbus:5.3f} V{ENDC}");
    print()
    if resp.response == RespType.ERR and not args.safety_off:
        return 3

    for test in run_tests:
        loops = args.loops if args.loops is not None else test.loops
        plural = "s" if loops != 1 else ""
        stats = f"({len(test.vectors)} vectors, {loops} loop{plural})"
        endc = "\n" if logger.isEnabledFor(20) else ""
        print(f" * Testing: {HI}{test.name:{longest_desc}s}{ENDC}   {stats:25}  ... ", end=endc, flush=True)

        if tests_failed:
            print(f"\b\b\b\b{SKIP}SKIP{ENDC}")
            resp.response = None
            continue

        if args.delay is not None:
            test.set_delay(args.delay)
        test.setup(transport)

        resp = test.run(transport, loops)

        print(f"\b\b\b\b{result_color[resp.response]}{resp.response.name}{ENDC}", end="")
        if resp.response in (RespType.PASS, RespType.FAIL):
            print(f"  ({test.elapsed:.2f} sec.)", end="")
        print()

        if resp.response == RespType.FAIL:
            tests_failed += 1
            if test.type == TestType.LOGIC:
                print()
                print(f"Test failed on loop: {HI}{test.failed_loop}{ENDC}")
                print_failed_vector(part, test, test.failed_vector_num, test.failed_pin_vector)
            if test.type == TestType.DRAM:
                print()
                print(f" Failing address: row {HI}{test.failed_row}{ENDC}, column {HI}{test.failed_column}{ENDC} on MARCH C- step {HI}{test.failed_march_step}{ENDC}")
                print()
        elif resp.response == RespType.PASS:
            tests_passed += 1
        elif resp.response == RespType.TIMING_ERROR:
            tests_warning += 1

    part.disconnect(transport)

    if resp.response != RespType.FAIL:
        print()

    print(f"Lowest measured bus voltage: {HI}{part.vbus:5.3f} V{ENDC}")
    print(f"Current measurements:")
    print()
    print(f"             Ivcc [mA]   Ignd [mA]   𝚫I [mA]")
    measurements = [f"@max Ivcc", f"@max Ignd", f"@min Ivcc", f"@min Ignd"]
    for name, m in zip(measurements, part.imeasurements):
        print(f" {name}:  {HI}{m[0]:6.2f}      {m[1]:6.2f}      {m[2]:6.2f}{ENDC}")
    print()

    logger.log(20, "Bytes sent: %s, received: %s", transport.bytes_sent, transport.bytes_received)

    tests_skipped = len(part.tests) - (tests_failed + tests_warning + tests_passed)

    print(f"Total tests: {HI}{len(run_tests)}{ENDC}", end="")
    if tests_failed:
        print(f", failed: {FAIL}{tests_failed}{ENDC}", end="")
    if tests_warning:
        print(f", warning: {WARN}{tests_warning}{ENDC}", end="")
    if tests_skipped:
        print(f", skipped: {SKIP}{tests_skipped}{ENDC}", end="")
    if tests_passed:
        print(f", passed: {OK}{tests_passed}{ENDC}", end="")
    print()

    if tests_failed:
        result = f"{FAIL}PART DEFECTIVE"
        ret = 1
    elif tests_warning:
        result = f"{WARN}OUTPUT READ TIMING ERROR"
        ret = 2
    else:
        result = f"{OK}PART OK"
        ret = 0

    print(f"{result}{ENDC}")

    return ret

if __name__ == "__main__":
    sys.exit(main())

