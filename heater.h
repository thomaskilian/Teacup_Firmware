#ifndef	_HEATER_H
#define	_HEATER_H

#include "config_wrapper.h"
#include	<stdint.h>
#include "temp.h"

/// Default scaled P factor, equivalent to 8.0 counts/qC or 32 counts/C.
#ifdef PID_P
  #define DEFAULT_P       PID_P
#else
  #define DEFAULT_P       (32 * PID_SCALE_D)
#endif

/// Default scaled I factor, equivalent to 0.5 counts/(qC*qs) or 8 counts/C*s.
#ifdef PID_I
  #define DEFAULT_I       PID_I
#else
  #define DEFAULT_I       (8 * PID_SCALE_I)
#endif

/// Default scaled D factor, equivalent to 24 counts/(qc/(TH_COUNT*qs)) or
/// 192 counts/(C/s).
#ifdef PID_D
  #define DEFAULT_D       PID_D
#else
  #define DEFAULT_D       (192 * PID_SCALE_D)
#endif

/// Default scaled I limit, equivalent to 384 qC*qs, or 24 C*s.
#define DEFAULT_I_LIMIT   384

/** \def HEATER_THRESHOLD

  Defines the threshold when to turn a non-PWM heater on and when to turn it
  off. Applies only to heaters which have only two states, on and off.
  Opposed to those heaters which allow to turn them on gradually as needed,
  usually by using PWM.
*/
#ifdef BANG_BANG
  #define HEATER_THRESHOLD ((BANG_BANG_ON + BANG_BANG_OFF) / 2)
#else
  #define HEATER_THRESHOLD 8
#endif

/** \def PID_SCALE_P
  Conversion factor between internal kP value and user values.  Since temperatures are measured in C/4 units,
  kP in counts/C would be kP*PID_SCALE/4 in internal units.
*/
#define PID_SCALE_P ((int32_t)PID_SCALE/4L)   // convert to internal 1/4C

/** \def PID_SCALE_I
  Conversion factor between internal kI value and user values. Since temperatures are measured in C/4 and the I
  accumulation is done four times per second, kI in counts/(C*s) would be kI*PID_SCALE/16 in internal counts/(qC*qs)
*/
#define PID_SCALE_I ((int32_t)PID_SCALE/16L)   // internal 1/4C by 1/4s second integration.

/** \def PID_SCALE_D
  Conversion factor between internal kD value and user values.
  Since temperatures are measured in C/4 and the derivative is measured over TH_COUNT 250ms cycles,
  kD in counts/(C/s) would be kI*PID_SCALE/TH_COUNT in internal counts/(qC/(TH_COUNT*qs).
*/
#define PID_SCALE_D ((int32_t)PID_SCALE/TH_COUNT) // Internal 1/4 degree per 1/4s sampling cancels, but the dt window is TH_COUNT long.

#undef DEFINE_HEATER
#define DEFINE_HEATER(name, pin, invert, pwm, p, i, d, i_limit, watts, t_dead) \
HEATER_ ## name,
typedef enum
{
	#include "config_wrapper.h"
	NUM_HEATERS,
	HEATER_noheater
} heater_t;
#undef DEFINE_HEATER

/** This struct holds the runtime heater data.

  PID integrator history, temperature history, sanity checker.
*/
typedef struct {
  /// Integrator, \f$-i_{limit} < \sum{4*eC*\Delta t} < i_{limit}\f$
  int16_t heater_i;

  /// Store last TH_COUNT readings in a ring, so we can smooth out our
  /// differentiator.
  uint16_t temp_history[TH_COUNT];
  /// Pointer to last entry in ring.
  uint8_t temp_history_pointer;

  #ifdef HEATER_SANITY_CHECK
    /// How long things haven't seemed sane.
    uint16_t sanity_counter;
    /// A temperature we consider sane given the heater settings.
    uint16_t sane_temperature;
  #endif

  /// This is the PID value we eventually send to the heater.
  uint8_t heater_output;
} heater_runtime_t;


extern heater_runtime_t heaters_runtime[];

void heater_init(void);
void pid_init(void);

void heater_set(heater_t index, uint8_t value);
void heater_tick(heater_t h, temp_type_t type, uint16_t current_temp, uint16_t target_temp);

uint8_t heaters_all_zero(void);

#ifdef EECONFIG
void pid_set_p(heater_t index, int32_t p);
void pid_set_i(heater_t index, int32_t i);
void pid_set_d(heater_t index, int32_t d);
void pid_set_i_limit(heater_t index, int32_t i_limit);
void heater_save_settings(void);
#endif /* EECONFIG */

void heater_print(uint16_t i);

#endif	/* _HEATER_H */
