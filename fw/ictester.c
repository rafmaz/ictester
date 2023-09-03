#include <inttypes.h>
#include <stdbool.h>
#include <avr/io.h>
#include <avr/interrupt.h>
#include <util/delay.h>

#include "serial.h"
#include "led.h"
#include "protocol.h"
#include "zif.h"
#include "logic.h"
#include "mem.h"
#include "univib.h"

#define LINK_SPEED 500000

struct port {
	uint8_t dut_input;
	uint8_t dut_output;
	uint8_t dut_pullup;
	uint8_t used_outputs;
} port[3];
uint8_t package_type;
uint8_t pin_count;

uint8_t test_type;
uint8_t test_params[MAX_TEST_PARAMS];

uint8_t zif_vcc_pin;
bool dut_connected;

// -----------------------------------------------------------------------
static void mcu_port_deconfigure(void)
{
	DDRA = 0;
	PORTA = 0;
	DDRB = 0;
	PORTB = 0;
	DDRC = 0;
	PORTC = 0;
}

// -----------------------------------------------------------------------
static void mcu_port_setup(void)
{
	// DUT input == MCU output
	DDRA = port[0].dut_input;
	DDRB = port[1].dut_input;
	DDRC = port[2].dut_input;
	// pullups
	PORTA = port[0].dut_pullup;
	PORTB = port[1].dut_pullup;
	PORTC = port[2].dut_pullup;
}

// -----------------------------------------------------------------------
static uint8_t handle_dut_setup(void)
{
	uint8_t pin_data[24];

	// receive DUT configuration
	package_type = serial_rx_char();
	pin_count = serial_rx_char();
	for (uint8_t i=0 ; i<pin_count ; i++) {
		pin_data[i] = serial_rx_char();
	}

	// check DUT pinout
	if (((pin_count != 14) && (pin_count != 16) && (pin_count != 20) && (pin_count != 24)) || (package_type != PACKAGE_DIP)) {
		return RESP_ERR;
	}

	// clear current DUT configuration
	for (uint8_t i=0 ; i<3 ; i++) {
		port[i].dut_output = 0;
		port[i].dut_input = 0;
		port[i].dut_pullup = 0;
	}

	// prepare port configuration based on provided DUT pin config
	for (uint8_t i=0 ; i<pin_count ; i++) {
		uint8_t zif_pin = zif_pos(pin_count, i);
		int8_t port_pos = mcu_port(zif_pin);
		uint8_t port_val = 1 << mcu_port_pin(zif_pin);
		switch (pin_data[i]) {
			case ZIF_OUT:
				port[port_pos].dut_input |= port_val;
				break;
			case ZIF_IN:
				port[port_pos].dut_output |= port_val;
				break;
			case ZIF_IN_PU_WEAK:
				port[port_pos].dut_output |= port_val;
				port[port_pos].dut_pullup |= port_val;
				break;
			case ZIF_IN_PU_STRONG:
				port[port_pos].dut_output |= port_val;
				zif_func(ZIF_IN_PU_STRONG, zif_pin);
				break;
			case ZIF_VCC:
				zif_vcc_pin = zif_pin;
				if (!zif_func(ZIF_VCC, zif_pin)) {
					return RESP_ERR;
				}
				break;
			case ZIF_GND:
				if (!zif_func(ZIF_GND, zif_pin)) {
					return RESP_ERR;
				}
				break;
			case ZIF_C:
				if (!zif_func(ZIF_C, zif_pin)) {
					return RESP_ERR;
				}
				break;
			case ZIF_IN_HIZ:
				// TODO: ensure HiZ
				break;
			default:
				return RESP_ERR;
		}
	}

	return RESP_OK;
}

// -----------------------------------------------------------------------
static uint8_t handle_test_setup(void)
{
	test_type = serial_rx_char();
	for (uint8_t i=0 ; i<MAX_TEST_PARAMS ; i++) {
		test_params[i] = serial_rx_char();
	}

	// reset port masks
	port[0].used_outputs = 0;
	port[1].used_outputs = 0;
	port[2].used_outputs = 0;

	// read pin usage data
	uint8_t pin_usage[3];
	for (uint8_t i=0 ; i<pin_count ; i+=8) {
		pin_usage[i/8] = serial_rx_char();
	}

	// fill in port masks
	for (uint8_t i=0 ; i<pin_count ; i++) {
		uint8_t zif_pin = zif_pos(pin_count, i);
		int8_t port_pos = mcu_port(zif_pin);
		if (port_pos >= 0) {
			uint8_t pin_used = (pin_usage[i/8] >> (i%8)) & 1;
			uint8_t pin_mask = pin_used << mcu_port_pin(zif_pin);
			port[port_pos].used_outputs |= port[port_pos].dut_output & pin_mask;
		}
	}

	return RESP_OK;
}

// -----------------------------------------------------------------------
static uint8_t handle_dut_connect(void)
{
	if (!zif_config_sane()) {
		return RESP_ERR;
	}

	led_active();
	zif_connect();
	mcu_port_setup();

	if (test_type == TEST_DRAM) {
		mem_setup();
	}

	dut_connected = true;

	return RESP_OK;
}

// -----------------------------------------------------------------------
static uint8_t handle_dut_disconnect(uint8_t resp)
{
	mcu_port_deconfigure();
	zif_disconnect();
	dut_connected = false;

	if (resp == RESP_ERR) led_err();
	else if (resp == RESP_FAIL) led_fail();
	else if (resp == RESP_PASS) led_pass();
	else led_idle();

	return RESP_OK;
}

// -----------------------------------------------------------------------
static uint8_t handle_run(void)
{
	uint8_t res = RESP_PASS;

	uint16_t loops = serial_rx_16le();

	if (!dut_connected) {
		res = handle_dut_connect();
		if (res != RESP_OK) return res;
	}

	switch (test_type) {
		case TEST_LOGIC:
			res = run_logic(loops, test_params);
			break;
		case TEST_DRAM:
			res = run_mem(loops, test_params);
			break;
		case TEST_UNIVIB:
			res = run_univib(loops, test_params);
			break;
		default:
			// unknown test type
			res = RESP_ERR;
			break;
	}

	if (res != RESP_PASS) {
		handle_dut_disconnect(res);
	}
	return res;
}

// -----------------------------------------------------------------------
int main(void)
{
	mcu_port_deconfigure();
	serial_init(LINK_SPEED);
	zif_init();
	led_init();
	led_welcome();

	while (true) {
		uint8_t resp;
		int cmd = serial_rx_char();

		switch (cmd) {
			case CMD_DUT_SETUP:
				resp = handle_dut_setup();
				break;
			case CMD_DUT_CONNECT:
				resp = handle_dut_connect();
				break;
			case CMD_TEST_SETUP:
				resp = handle_test_setup();
				break;
			case CMD_VECTORS_LOAD:
				resp = handle_vectors_load(pin_count);
				break;
			case CMD_TEST_RUN:
				resp = handle_run();
				break;
			case CMD_DUT_DISCONNECT:
				resp = handle_dut_disconnect(resp);
				break;
			default:
				resp = RESP_ERR;
		}

		if (resp == RESP_ERR) {
			led_err();
		}

		reply(resp);
	}

	return 0;
}

// vim: tabstop=4 shiftwidth=4 autoindent
