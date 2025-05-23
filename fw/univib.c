#include <inttypes.h>
#include <stdbool.h>
#include <avr/io.h>
#include <avr/cpufunc.h>
#include <util/delay.h>

#include "protocol.h"
#include "zif.h"
#include "isense.h"

enum univib_devices {
	UNIVIB_121			= 0,
	UNIVIB_122			= 1,
	UNIVIB_123_1		= 2,
	UNIVIB_123_2		= 3,
	UNIVIB_DEVICE_MAX	= UNIVIB_123_2
};

enum test_types {
	TEST_NOTRIG		= 0,
	TEST_TRIG		= 1,
	TEST_RETRIG		= 2,
	TEST_CLEAR		= 3,
	TEST_CROSSTRIG	= 4,
	TEST_CLEARTRIG	= 5,
	UNIVIB_TEST_MAX	= TEST_CLEARTRIG
};

uint8_t univib_device;
uint8_t univib_test_type;

// 74121

#define VAL_121_A1		_BV(ZIF_2_PORT_BIT)
#define VAL_121_A2		_BV(ZIF_3_PORT_BIT)
#define VAL_121_B		_BV(ZIF_4_PORT_BIT)
#define VAL_121_Q		_BV(ZIF_5_PORT_BIT)
#define VAL_121_NQ		_BV(ZIF_0_PORT_BIT)
#define VAL_121_Q_PU	(_BV(ZIF_0_PORT_BIT) | _BV(ZIF_5_PORT_BIT))

// 74122

#define VAL_122_A1		_BV(ZIF_0_PORT_BIT)
#define VAL_122_A2		_BV(ZIF_1_PORT_BIT)
#define VAL_122_B1		_BV(ZIF_2_PORT_BIT)
#define VAL_122_B2		_BV(ZIF_3_PORT_BIT)
#define VAL_122_CLR		_BV(ZIF_4_PORT_BIT)
#define VAL_122_NQ		_BV(ZIF_5_PORT_BIT)
#define VAL_122_Q		_BV(ZIF_17_PORT_BIT)
#define VAL_122_Q_PU	_BV(ZIF_5_PORT_BIT) // only one because only ~Q is on the same port as triggers

// 74123 1 and 2

#define VAL_123_A		_BV(ZIF_0_PORT_BIT)
#define VAL_123_B		_BV(ZIF_1_PORT_BIT)
#define VAL_123_CLR		_BV(ZIF_2_PORT_BIT)
#define VAL_123_Q		_BV(ZIF_4_PORT_BIT)
#define VAL_123_NQ		_BV(ZIF_3_PORT_BIT)
#define VAL_123_Q_PU	(_BV(ZIF_3_PORT_BIT) | _BV(ZIF_4_PORT_BIT))

// trig and notrig conditions

#define RETRIG_LOOPS 6
#define LAST_TRIG 0xff

// {B, A2, A1} combinations that trigger 74121
static const __flash uint8_t trigs_121[] = {
	VAL_121_B |          0 |          0,
	VAL_121_B |          0 | VAL_121_A1,
	VAL_121_B | VAL_121_A2 |          0,
	LAST_TRIG
};

// {B, A2, A1} combinations that don't trigger 74121
static const __flash uint8_t notrigs_121[] = {
	        0 |          0 |          0,
	        0 |          0 | VAL_121_A1,
	        0 | VAL_121_A2 |          0,
	        0 | VAL_121_A2 | VAL_121_A1,
	// triggers taken from here
	VAL_121_B | VAL_121_A2 | VAL_121_A1,
	LAST_TRIG
};

// {CLR, B2, B1, A2, A1} combinations that trigger 74122
static const __flash uint8_t trigs_122[] = {
	VAL_122_CLR | VAL_122_B2 | VAL_122_B1 |          0 |          0,
	VAL_122_CLR | VAL_122_B2 | VAL_122_B1 |          0 | VAL_122_A1,
	VAL_122_CLR | VAL_122_B2 | VAL_122_B1 | VAL_122_A2 |          0,
	LAST_TRIG
};

// {CLR, B2, B1, A2, A1} combinations that don't trigger 74122
static const __flash uint8_t notrigs_122[] = {
	          0 |          0 |          0 |          0 |          0,
	          0 |          0 |          0 |          0 | VAL_122_A1,
	          0 |          0 |          0 | VAL_122_A2 |          0,
	          0 |          0 |          0 | VAL_122_A2 | VAL_122_A1,
	          0 |          0 | VAL_122_B1 |          0 |          0,
	          0 |          0 | VAL_122_B1 |          0 | VAL_122_A1,
	          0 |          0 | VAL_122_B1 | VAL_122_A2 |          0,
	          0 |          0 | VAL_122_B1 | VAL_122_A2 | VAL_122_A1,
	          0 | VAL_122_B2 |          0 |          0 |          0,
	          0 | VAL_122_B2 |          0 |          0 | VAL_122_A1,
	          0 | VAL_122_B2 |          0 | VAL_122_A2 |          0,
	          0 | VAL_122_B2 |          0 | VAL_122_A2 | VAL_122_A1,
	          0 | VAL_122_B2 | VAL_122_B1 |          0 |          0,
	          0 | VAL_122_B2 | VAL_122_B1 |          0 | VAL_122_A1,
	          0 | VAL_122_B2 | VAL_122_B1 | VAL_122_A2 |          0,
	          0 | VAL_122_B2 | VAL_122_B1 | VAL_122_A2 | VAL_122_A1,
	VAL_122_CLR |          0 |          0 |          0 |          0,
	VAL_122_CLR |          0 |          0 |          0 | VAL_122_A1,
	VAL_122_CLR |          0 |          0 | VAL_122_A2 |          0,
	VAL_122_CLR |          0 |          0 | VAL_122_A2 | VAL_122_A1,
	VAL_122_CLR |          0 | VAL_122_B1 |          0 |          0,
	VAL_122_CLR |          0 | VAL_122_B1 |          0 | VAL_122_A1,
	VAL_122_CLR |          0 | VAL_122_B1 | VAL_122_A2 |          0,
	VAL_122_CLR |          0 | VAL_122_B1 | VAL_122_A2 | VAL_122_A1,
	VAL_122_CLR | VAL_122_B2 |          0 |          0 |          0,
	VAL_122_CLR | VAL_122_B2 |          0 |          0 | VAL_122_A1,
	VAL_122_CLR | VAL_122_B2 |          0 | VAL_122_A2 |          0,
	VAL_122_CLR | VAL_122_B2 |          0 | VAL_122_A2 | VAL_122_A1,
	// triggers taken from here
	VAL_122_CLR | VAL_122_B2 | VAL_122_B1 | VAL_122_A2 | VAL_122_A1,
	LAST_TRIG
};

// {CLR, B, A} combinations that trigger 74123
static const __flash uint8_t trigs_123[] = {
	VAL_123_CLR | VAL_123_B |         0,
	LAST_TRIG
};

// {CLR, B, A} combinations that don't trigger 74123
static const __flash uint8_t notrigs_123[] = {
	          0 |         0 |         0,
	          0 |         0 | VAL_123_A,
	          0 | VAL_123_B |         0,
	          0 | VAL_123_B | VAL_123_A,
    VAL_123_CLR |         0 |         0,
	VAL_123_CLR |         0 | VAL_123_A,
	// triggers taken from here
	VAL_123_CLR | VAL_123_B | VAL_123_A,
	LAST_TRIG
};

// device-specific test variables

static const __flash struct univib_test {
	volatile uint8_t *port_trig;		// port with trigger inputs
	volatile uint8_t *pin_q;			// pin with Q output
	volatile uint8_t *pin_nq;			// pin with ~Q output
	uint8_t val_trig;					// input for trigger
	uint8_t val_notrig;					// "idle" input
	uint8_t val_clear;					// input for clear
	uint8_t val_clear_trig;				// input for clear with trigger active
	uint8_t val_q, val_nq;				// Q, ~Q pin values
	uint8_t val_q_pullups;				// Q/~Q positions on trigger port (that may be pulled up)
	const __flash uint8_t *trigs;		// all triggers
	const __flash uint8_t *notrigs;		// all non-triggers
} univib_test[4] = {
	{ // 74121
		.port_trig = &ZIF_MCU_PORT_0,
		.pin_q = &ZIF_MCU_PIN_0,
		.pin_nq = &ZIF_MCU_PIN_0,
		.val_trig = VAL_121_B,
		.val_notrig = VAL_121_A1 | VAL_121_A2,
		.val_clear = 0,
		.val_q = VAL_121_Q,
		.val_nq = VAL_121_NQ,
		.val_q_pullups = VAL_121_Q_PU,
		.trigs = trigs_121,
		.notrigs = notrigs_121,
	},
	{ // 74122
		.port_trig = &ZIF_MCU_PORT_0,
		.pin_q = &ZIF_MCU_PIN_2,
		.pin_nq = &ZIF_MCU_PIN_0,
		.val_trig = VAL_122_B1 | VAL_122_B2 | VAL_122_CLR,
		.val_notrig = VAL_122_A1 | VAL_122_A2 | VAL_122_CLR,
		.val_clear = VAL_122_A1 | VAL_122_A2,
		.val_clear_trig = VAL_122_B1 | VAL_122_B2,
		.val_q = VAL_122_Q,
		.val_nq = VAL_122_NQ,
		.val_q_pullups = VAL_122_Q_PU,
		.trigs = trigs_122,
		.notrigs = notrigs_122,
	},
	{ // 74123 univibrator 1
		.port_trig = &ZIF_MCU_PORT_0,
		.pin_q = &ZIF_MCU_PIN_2,
		.pin_nq = &ZIF_MCU_PIN_0,
		.val_trig = VAL_123_B | VAL_123_CLR,
		.val_notrig = VAL_123_A | VAL_123_CLR,
		.val_clear = VAL_123_A,
		.val_clear_trig = VAL_123_B,
		.val_q = VAL_123_Q,
		.val_nq = VAL_123_NQ,
		.val_q_pullups = VAL_123_Q_PU,
		.trigs = trigs_123,
		.notrigs = notrigs_123,
	},
	{ // 74123 univibrator 2
		.port_trig = &ZIF_MCU_PORT_2,
		.pin_q = &ZIF_MCU_PIN_0,
		.pin_nq = &ZIF_MCU_PIN_2,
		.val_trig = VAL_123_B | VAL_123_CLR,
		.val_notrig = VAL_123_A | VAL_123_CLR,
		.val_clear = VAL_123_A,
		.val_clear_trig = VAL_123_B,
		.val_q = VAL_123_Q,
		.val_nq = VAL_123_NQ,
		.val_q_pullups = VAL_123_Q_PU,
		.trigs = trigs_123,
		.notrigs = notrigs_123,
	},
};

// -----------------------------------------------------------------------
uint8_t univib_test_setup(struct univib_params *params)
{
	if (params->device > UNIVIB_DEVICE_MAX) {
		return error(ERR_UNKNOWN_CHIP);
	}
	if (params->test_type > UNIVIB_TEST_MAX) {
		return error(ERR_UNKNOWN_TEST);
	}

	univib_device = params->device;
	univib_test_type = params->test_type;

	return RESP_OK;
}

// NOTE: The trick to keep compiler optimizations in check and
//       ensure proper test timings is to make sure 'uvt'
//       can be resolved to a constant during compilation time.
//       This makes the whole device/test selection logic dirty with all
//       the (duplicated) switch/case statements and inlined test functions,
//       but I'm afraid it's the only sensible way.

// -----------------------------------------------------------------------
static inline void input_set(const __flash struct univib_test *uvt, uint8_t val)
{
	*uvt->port_trig = (*uvt->port_trig & uvt->val_q_pullups) | val;
	_NOP(); _NOP();
}

// -----------------------------------------------------------------------
static inline void trig(const __flash struct univib_test *uvt, uint8_t val)
{
	input_set(uvt, val);
	*uvt->port_trig = (*uvt->port_trig & uvt->val_q_pullups) | uvt->val_notrig;
}

// -----------------------------------------------------------------------
static inline bool output_active(const __flash struct univib_test *uvt)
{
	return (*uvt->pin_q & uvt->val_q) && !(*uvt->pin_nq & uvt->val_nq);
}

// -----------------------------------------------------------------------
static inline bool other_output_active(const __flash struct univib_test *uvt)
{
	return (*uvt->pin_nq & uvt->val_q) && !(*uvt->pin_q & uvt->val_nq);
}

// -----------------------------------------------------------------------
static void test_imeasure(const __flash struct univib_test *uvt)
{
	const __flash uint8_t *i = uvt->notrigs;

	while (*i != LAST_TRIG) {
		input_set(uvt, *i);
		update_current_stats();
		i++;
	}

	i = uvt->trigs;

	while (*i != LAST_TRIG) {
		input_set(uvt, *i);
		update_current_stats();
		i++;
	}
}

// -----------------------------------------------------------------------
static inline uint8_t test_no_trig(const __flash struct univib_test *uvt)
{
	const __flash uint8_t *i = uvt->notrigs;

	while (*i != LAST_TRIG) {
		input_set(uvt, *i);
		_NOP(); _NOP(); _NOP();
		if (output_active(uvt)) return RESP_FAIL;
		i++;
	}

	return RESP_PASS;
}

// -----------------------------------------------------------------------
static inline uint8_t test_crosstrig(const __flash struct univib_test *uvt)
{
	const __flash uint8_t *i = uvt->trigs;

	while (*i != LAST_TRIG) {
		trig(uvt, *i);
		if (other_output_active(uvt)) return RESP_FAIL;
		_NOP(); _NOP(); _NOP();
		// ~500ns after the trigger
		if (other_output_active(uvt)) return RESP_FAIL;
		_delay_us(1.3);
		// ~2us after the last trigger
		if (other_output_active(uvt)) return RESP_FAIL;
		i++;
	}

	return RESP_PASS;
}

// -----------------------------------------------------------------------
static inline uint8_t test_trig(const __flash struct univib_test *uvt)
{
	const __flash uint8_t *i = uvt->trigs;

	while (*i != LAST_TRIG) {
		trig(uvt, *i);
		// right after the trigger
		if (!output_active(uvt)) return RESP_FAIL;
		_NOP(); _NOP(); _NOP();
		// ~500ns after the trigger
		if (!output_active(uvt)) return RESP_FAIL;
		_delay_us(1.3);
		// ~2us after the last trigger
		if (output_active(uvt)) return RESP_FAIL;
		i++;
	}

	return RESP_PASS;
}

// -----------------------------------------------------------------------
static inline uint8_t test_cleartrig(const __flash struct univib_test *uvt)
{
	const __flash uint8_t *i = uvt->trigs;

	while (*i != LAST_TRIG) {
		input_set(uvt, uvt->val_clear); // initial CLR held
		input_set(uvt, uvt->val_clear_trig); // trigger pulled with CLR still held
		_NOP(); _NOP(); _NOP();
		if (output_active(uvt)) return RESP_FAIL;
		trig(uvt, *i); // release CLR => trigger
		// right after the trigger
		if (!output_active(uvt)) return RESP_FAIL;
		_NOP(); _NOP(); _NOP();
		// ~500ns after the trigger
		if (!output_active(uvt)) return RESP_FAIL;
		_delay_us(1.3);
		// ~2us after the last trigger
		if (output_active(uvt)) return RESP_FAIL;
		i++;
	}

	return RESP_PASS;
}

// -----------------------------------------------------------------------
static inline uint8_t test_retrig(const __flash struct univib_test *uvt)
{
	for (uint8_t i=0 ; i<RETRIG_LOOPS; i++) {
		trig(uvt, uvt->val_trig);
		if (!output_active(uvt)) return RESP_FAIL;
		_NOP(); _NOP(); _NOP();
		// ~500ns after the trigger
		if (!output_active(uvt)) return RESP_FAIL;
	}
	_delay_us(1.3);
	// ~2us after the last trigger
	if (output_active(uvt)) return RESP_FAIL;

	return RESP_PASS;
}

// -----------------------------------------------------------------------
static inline uint8_t test_clear(const __flash struct univib_test *uvt)
{
	trig(uvt, uvt->val_trig);
	if (!output_active(uvt)) return RESP_FAIL;
	input_set(uvt, uvt->val_clear);
	if (output_active(uvt)) return RESP_FAIL;

	return RESP_PASS;
}

// -----------------------------------------------------------------------
static uint8_t test_121(uint8_t test)
{
	switch (test) {
		case TEST_NOTRIG: return test_no_trig(univib_test + UNIVIB_121);
		case TEST_TRIG: return test_trig(univib_test + UNIVIB_121);
		default:
			return error(ERR_UNKNOWN_TEST);
	}
}

// -----------------------------------------------------------------------
static uint8_t test_122(uint8_t test)
{
	switch (test) {
		case TEST_NOTRIG: return test_no_trig(univib_test + UNIVIB_122);
		case TEST_TRIG: return test_trig(univib_test + UNIVIB_122);
		case TEST_RETRIG: return test_retrig(univib_test + UNIVIB_122);
		case TEST_CLEAR: return test_clear(univib_test + UNIVIB_122);
		case TEST_CLEARTRIG: return test_cleartrig(univib_test + UNIVIB_122);
		default:
			return error(ERR_UNKNOWN_TEST);
	}
}

// -----------------------------------------------------------------------
static uint8_t test_123_1(uint8_t test)
{
	switch (test) {
		case TEST_NOTRIG: return test_no_trig(univib_test + UNIVIB_123_1);
		case TEST_TRIG: return test_trig(univib_test + UNIVIB_123_1);
		case TEST_RETRIG: return test_retrig(univib_test + UNIVIB_123_1);
		case TEST_CLEAR: return test_clear(univib_test + UNIVIB_123_1);
		case TEST_CROSSTRIG: return test_crosstrig(univib_test + UNIVIB_123_1);
		case TEST_CLEARTRIG: return test_cleartrig(univib_test + UNIVIB_123_1);
		default:
			return error(ERR_UNKNOWN_TEST);
	}
}

// -----------------------------------------------------------------------
static uint8_t test_123_2(uint8_t test)
{
	switch (test) {
		case TEST_NOTRIG:return test_no_trig(univib_test + UNIVIB_123_2);
		case TEST_TRIG: return test_trig(univib_test + UNIVIB_123_2);
		case TEST_RETRIG: return test_retrig(univib_test + UNIVIB_123_2);
		case TEST_CLEAR: return test_clear(univib_test + UNIVIB_123_2);
		case TEST_CROSSTRIG: return test_crosstrig(univib_test + UNIVIB_123_2);
		case TEST_CLEARTRIG: return test_cleartrig(univib_test + UNIVIB_123_2);
		default:
			return error(ERR_UNKNOWN_TEST);
	}
}

// -----------------------------------------------------------------------
uint8_t univib_run(uint16_t loops)
{
	uint8_t res;

	for (uint16_t rep=0 ; rep<loops ; rep++) {
		switch (univib_device) {
			case UNIVIB_121:
				if ((res = test_121(univib_test_type)) != RESP_PASS) return res;
				break;
			case UNIVIB_122:
				if ((res = test_122(univib_test_type)) != RESP_PASS) return res;
				break;
			case UNIVIB_123_1:
				if ((res = test_123_1(univib_test_type)) != RESP_PASS) return res;
				break;
			case UNIVIB_123_2:
				if ((res = test_123_2(univib_test_type)) != RESP_PASS) return res;
				break;
			default:
				return error(ERR_UNKNOWN_CHIP);
		}
	}

	test_imeasure(univib_test + univib_device);

	return RESP_PASS;
}

// vim: tabstop=4 shiftwidth=4 autoindent
