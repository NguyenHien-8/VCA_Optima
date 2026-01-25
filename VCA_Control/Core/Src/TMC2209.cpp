#include "TMC2209.hpp"
#include <cmath>

TMC2209::TMC2209()
    : huart_(nullptr),
      serial_baud_rate_(115200),
      serial_address_(SERIAL_ADDRESS_0),
      dir_gpio_port_(nullptr), dir_gpio_pin_(0),
      en_gpio_port_(nullptr), en_gpio_pin_(0),
      ms1_gpio_port_(nullptr), ms1_gpio_pin_(0),
      ms2_gpio_port_(nullptr), ms2_gpio_pin_(0),
      step_timer_(nullptr), step_channel_(0),
      timer_period_(0), // <--- Khởi tạo biến này
      initialized_(false),
      cool_step_enabled_(false),
      toff_(TOFF_DEFAULT)
{
  global_config_.bytes = 0;
  driver_current_.bytes = 0;
  chopper_config_.bytes = 0;
  pwm_config_.bytes = 0;
  cool_config_.bytes = 0;
}

TMC2209::~TMC2209()
{
  if (initialized_)
  {
    stopStepping();
  }
}

// =============================== MANUAL STEP CONTROL ================================ //
void TMC2209::setup(UART_HandleTypeDef *huart,
                    GPIO_TypeDef *en_gpio_port, uint16_t en_gpio_pin,
                    GPIO_TypeDef *dir_gpio_port, uint16_t dir_gpio_pin,
                    TIM_HandleTypeDef *step_timer, uint32_t step_channel,
                    GPIO_TypeDef *ms1_gpio_port, uint16_t ms1_gpio_pin,
                    GPIO_TypeDef *ms2_gpio_port, uint16_t ms2_gpio_pin,
                    SerialAddress serial_address)
{
	huart_ = huart;
	serial_address_ = serial_address;

	en_gpio_port_ = en_gpio_port;
	en_gpio_pin_ = en_gpio_pin;
	dir_gpio_port_ = dir_gpio_port;
	dir_gpio_pin_ = dir_gpio_pin;

	step_timer_ = step_timer;
	step_channel_ = step_channel;

	ms1_gpio_port_ = ms1_gpio_port;
	ms1_gpio_pin_ = ms1_gpio_pin;
	ms2_gpio_port_ = ms2_gpio_port;
	ms2_gpio_pin_ = ms2_gpio_pin;

	// (Default 1/8 step: Low-Low)
	if (ms1_gpio_port_ && ms2_gpio_port_) {
	    HAL_GPIO_WritePin(ms1_gpio_port_, ms1_gpio_pin_, GPIO_PIN_RESET);
	    HAL_GPIO_WritePin(ms2_gpio_port_, ms2_gpio_pin_, GPIO_PIN_RESET);
	}
	initialized_ = true;
}

// Unidirectional methods
void TMC2209::setHardwareEnablePin(GPIO_TypeDef *gpio_port, uint16_t gpio_pin)
{
  en_gpio_port_ = gpio_port;
  en_gpio_pin_ = gpio_pin;
  HAL_GPIO_WritePin(gpio_port, gpio_pin, GPIO_PIN_SET);
}

void TMC2209::enable()
{
  if (en_gpio_port_ != nullptr)
  {
    HAL_GPIO_WritePin(en_gpio_port_, en_gpio_pin_, GPIO_PIN_RESET);
  }
  chopper_config_.toff = toff_;
  writeStoredChopperConfig();
}

void TMC2209::disable()
{
  if (en_gpio_port_ != nullptr)
  {
    HAL_GPIO_WritePin(en_gpio_port_, en_gpio_pin_, GPIO_PIN_SET);
  }
  chopper_config_.toff = TOFF_DISABLE;
  writeStoredChopperConfig();
}

// ==================================================================================== //

void TMC2209::setMicrostepsPerStep(uint16_t microsteps_per_step)
{
  uint16_t microsteps_per_step_shifted = constrain_(microsteps_per_step,
                                                     MICROSTEPS_PER_STEP_MIN,
                                                     MICROSTEPS_PER_STEP_MAX);
  microsteps_per_step_shifted = microsteps_per_step >> 1;
  uint16_t exponent = 0;
  while (microsteps_per_step_shifted > 0)
  {
    microsteps_per_step_shifted = microsteps_per_step_shifted >> 1;
    ++exponent;
  }
  setMicrostepsPerStepPowerOfTwo(exponent);
}

void TMC2209::setMicrostepsPerStepPowerOfTwo(uint8_t exponent)
{
  switch (exponent)
  {
    case 0:
      chopper_config_.mres = MRES_001;
      break;
    case 1:
      chopper_config_.mres = MRES_002;
      break;
    case 2:
      chopper_config_.mres = MRES_004;
      break;
    case 3:
      chopper_config_.mres = MRES_008;
      break;
    case 4:
      chopper_config_.mres = MRES_016;
      break;
    case 5:
      chopper_config_.mres = MRES_032;
      break;
    case 6:
      chopper_config_.mres = MRES_064;
      break;
    case 7:
      chopper_config_.mres = MRES_128;
      break;
    case 8:
    default:
      chopper_config_.mres = MRES_256;
      break;
  }
  writeStoredChopperConfig();
}

void TMC2209::setRunCurrent(uint8_t percent)
{
  uint8_t run_current = percentToCurrentSetting(percent);
  driver_current_.irun = run_current;
  writeStoredDriverCurrent();
}

void TMC2209::setHoldCurrent(uint8_t percent)
{
  uint8_t hold_current = percentToCurrentSetting(percent);
  driver_current_.ihold = hold_current;
  writeStoredDriverCurrent();
}

void TMC2209::setHoldDelay(uint8_t percent)
{
  uint8_t hold_delay = percentToHoldDelaySetting(percent);
  driver_current_.iholddelay = hold_delay;
  writeStoredDriverCurrent();
}

void TMC2209::setAllCurrentValues(uint8_t run_current_percent,
                                  uint8_t hold_current_percent,
                                  uint8_t hold_delay_percent)
{
  uint8_t run_current = percentToCurrentSetting(run_current_percent);
  uint8_t hold_current = percentToCurrentSetting(hold_current_percent);
  uint8_t hold_delay = percentToHoldDelaySetting(hold_delay_percent);

  driver_current_.irun = run_current;
  driver_current_.ihold = hold_current;
  driver_current_.iholddelay = hold_delay;
  writeStoredDriverCurrent();
}

void TMC2209::setRMSCurrent(uint16_t mA, float rSense, float holdMultiplier)
{
  uint8_t CS = 32.0 * 1.41421 * mA / 1000.0 * (rSense + 0.02) / 0.325 - 1;
  if (CS < 16)
  {
    enableVSense();
    CS = 32.0 * 1.41421 * mA / 1000.0 * (rSense + 0.02) / 0.180 - 1;
  }
  else
  {
    disableVSense();
  }

  if (CS > 31)
  {
    CS = 31;
  }

  driver_current_.irun = CS;
  driver_current_.ihold = (uint8_t)(CS * holdMultiplier);
  writeStoredDriverCurrent();
}

void TMC2209::enableDoubleEdge()
{
  chopper_config_.double_edge = DOUBLE_EDGE_ENABLE;
  writeStoredChopperConfig();
}

void TMC2209::disableDoubleEdge()
{
  chopper_config_.double_edge = DOUBLE_EDGE_DISABLE;
  writeStoredChopperConfig();
}

void TMC2209::enableVSense()
{
  chopper_config_.vsense = VSENSE_ENABLE;
  writeStoredChopperConfig();
}

void TMC2209::disableVSense()
{
  chopper_config_.vsense = VSENSE_DISABLE;
  writeStoredChopperConfig();
}

void TMC2209::enableInverseMotorDirection()
{
  global_config_.shaft = 1;
  writeStoredGlobalConfig();
}

void TMC2209::disableInverseMotorDirection()
{
  global_config_.shaft = 0;
  writeStoredGlobalConfig();
}

void TMC2209::setStandstillMode(StandstillMode mode)
{
  pwm_config_.freewheel = mode;
  writeStoredPwmConfig();
}

void TMC2209::enableAutomaticCurrentScaling()
{
  pwm_config_.pwm_autoscale = STEPPER_DRIVER_FEATURE_ON;
  writeStoredPwmConfig();
}

void TMC2209::disableAutomaticCurrentScaling()
{
  pwm_config_.pwm_autoscale = STEPPER_DRIVER_FEATURE_OFF;
  writeStoredPwmConfig();
}

void TMC2209::enableAutomaticGradientAdaptation()
{
  pwm_config_.pwm_autograd = STEPPER_DRIVER_FEATURE_ON;
  writeStoredPwmConfig();
}

void TMC2209::disableAutomaticGradientAdaptation()
{
  pwm_config_.pwm_autograd = STEPPER_DRIVER_FEATURE_OFF;
  writeStoredPwmConfig();
}

void TMC2209::setPwmOffset(uint8_t pwm_amplitude)
{
  pwm_config_.pwm_offset = pwm_amplitude;
  writeStoredPwmConfig();
}

void TMC2209::setPwmGradient(uint8_t pwm_amplitude)
{
  pwm_config_.pwm_grad = pwm_amplitude;
  writeStoredPwmConfig();
}

void TMC2209::setPowerDownDelay(uint8_t power_down_delay)
{
  write(ADDRESS_TPOWERDOWN, power_down_delay);
}

void TMC2209::setReplyDelay(uint8_t reply_delay)
{
  if (reply_delay > REPLY_DELAY_MAX)
  {
    reply_delay = REPLY_DELAY_MAX;
  }
  ReplyDelay reply_delay_data;
  reply_delay_data.bytes = 0;
  reply_delay_data.replydelay = reply_delay;
  write(ADDRESS_REPLYDELAY, reply_delay_data.bytes);
}

void TMC2209::moveAtVelocity(int32_t microsteps_per_period)
{
  write(ADDRESS_VACTUAL, (uint32_t)microsteps_per_period);
}

void TMC2209::moveUsingStepDirInterface()
{
  write(ADDRESS_VACTUAL, VACTUAL_STEP_DIR_INTERFACE);
}

void TMC2209::enableStealthChop()
{
  global_config_.enable_spread_cycle = 0;
  writeStoredGlobalConfig();
}

void TMC2209::disableStealthChop()
{
  global_config_.enable_spread_cycle = 1;
  writeStoredGlobalConfig();
}

void TMC2209::setCoolStepDurationThreshold(uint32_t duration_threshold)
{
  write(ADDRESS_TCOOLTHRS, duration_threshold);
}

void TMC2209::setStealthChopDurationThreshold(uint32_t duration_threshold)
{
  write(ADDRESS_TPWMTHRS, duration_threshold);
}

void TMC2209::setStallGuardThreshold(uint8_t stall_guard_threshold)
{
  write(ADDRESS_SGTHRS, stall_guard_threshold);
}

void TMC2209::enableCoolStep(uint8_t lower_threshold, uint8_t upper_threshold)
{
  lower_threshold = constrain_(lower_threshold, SEMIN_MIN, SEMIN_MAX);
  cool_config_.semin = lower_threshold;
  upper_threshold = constrain_(upper_threshold, SEMAX_MIN, SEMAX_MAX);
  cool_config_.semax = upper_threshold;
  write(ADDRESS_COOLCONF, cool_config_.bytes);
  cool_step_enabled_ = true;
}

void TMC2209::disableCoolStep()
{
  cool_config_.semin = SEMIN_OFF;
  write(ADDRESS_COOLCONF, cool_config_.bytes);
  cool_step_enabled_ = false;
}

void TMC2209::setCoolStepCurrentIncrement(CurrentIncrement current_increment)
{
  cool_config_.seup = current_increment;
  write(ADDRESS_COOLCONF, cool_config_.bytes);
}

void TMC2209::setCoolStepMeasurementCount(MeasurementCount measurement_count)
{
  cool_config_.sedn = measurement_count;
  write(ADDRESS_COOLCONF, cool_config_.bytes);
}

void TMC2209::enableAnalogCurrentScaling()
{
  global_config_.i_scale_analog = 1;
  writeStoredGlobalConfig();
}

void TMC2209::disableAnalogCurrentScaling()
{
  global_config_.i_scale_analog = 0;
  writeStoredGlobalConfig();
}

void TMC2209::useExternalSenseResistors()
{
  global_config_.internal_rsense = 0;
  writeStoredGlobalConfig();
}

void TMC2209::useInternalSenseResistors()
{
  global_config_.internal_rsense = 1;
  writeStoredGlobalConfig();
}

// Bidirectional methods
uint8_t TMC2209::getVersion()
{
  Input input;
  input.bytes = read(ADDRESS_IOIN);
  return input.version;
}

bool TMC2209::isCommunicating()
{
  return (getVersion() == VERSION);
}

bool TMC2209::isSetupAndCommunicating()
{
  return serialOperationMode();
}

bool TMC2209::isCommunicatingButNotSetup()
{
  return (isCommunicating() && (not isSetupAndCommunicating()));
}

bool TMC2209::hardwareDisabled()
{
  Input input;
  input.bytes = read(ADDRESS_IOIN);
  return input.enn;
}

uint16_t TMC2209::getMicrostepsPerStep()
{
  uint16_t microsteps_per_step_exponent;
  switch (chopper_config_.mres)
  {
    case MRES_001:
      microsteps_per_step_exponent = 0;
      break;
    case MRES_002:
      microsteps_per_step_exponent = 1;
      break;
    case MRES_004:
      microsteps_per_step_exponent = 2;
      break;
    case MRES_008:
      microsteps_per_step_exponent = 3;
      break;
    case MRES_016:
      microsteps_per_step_exponent = 4;
      break;
    case MRES_032:
      microsteps_per_step_exponent = 5;
      break;
    case MRES_064:
      microsteps_per_step_exponent = 6;
      break;
    case MRES_128:
      microsteps_per_step_exponent = 7;
      break;
    case MRES_256:
    default:
      microsteps_per_step_exponent = 8;
      break;
  }
  return 1 << microsteps_per_step_exponent;
}

TMC2209::Settings TMC2209::getSettings()
{
  Settings settings;
  settings.is_communicating = isCommunicating();

  if (settings.is_communicating)
  {
    readAndStoreRegisters();

    settings.is_setup = global_config_.pdn_disable;
    settings.software_enabled = (chopper_config_.toff > TOFF_DISABLE);
    settings.microsteps_per_step = getMicrostepsPerStep();
    settings.inverse_motor_direction_enabled = global_config_.shaft;
    settings.stealth_chop_enabled = not global_config_.enable_spread_cycle;
    settings.standstill_mode = pwm_config_.freewheel;
    settings.irun_percent = currentSettingToPercent(driver_current_.irun);
    settings.irun_register_value = driver_current_.irun;
    settings.ihold_percent = currentSettingToPercent(driver_current_.ihold);
    settings.ihold_register_value = driver_current_.ihold;
    settings.iholddelay_percent = holdDelaySettingToPercent(driver_current_.iholddelay);
    settings.iholddelay_register_value = driver_current_.iholddelay;
    settings.automatic_current_scaling_enabled = pwm_config_.pwm_autoscale;
    settings.automatic_gradient_adaptation_enabled = pwm_config_.pwm_autograd;
    settings.pwm_offset = pwm_config_.pwm_offset;
    settings.pwm_gradient = pwm_config_.pwm_grad;
    settings.cool_step_enabled = cool_step_enabled_;
    settings.analog_current_scaling_enabled = global_config_.i_scale_analog;
    settings.internal_sense_resistors_enabled = global_config_.internal_rsense;
  }
  else
  {
    settings.is_setup = false;
    settings.software_enabled = false;
    settings.microsteps_per_step = 0;
    settings.inverse_motor_direction_enabled = false;
    settings.stealth_chop_enabled = false;
    settings.standstill_mode = pwm_config_.freewheel;
    settings.irun_percent = 0;
    settings.irun_register_value = 0;
    settings.ihold_percent = 0;
    settings.ihold_register_value = 0;
    settings.iholddelay_percent = 0;
    settings.iholddelay_register_value = 0;
    settings.automatic_current_scaling_enabled = false;
    settings.automatic_gradient_adaptation_enabled = false;
    settings.pwm_offset = 0;
    settings.pwm_gradient = 0;
    settings.cool_step_enabled = false;
    settings.analog_current_scaling_enabled = false;
    settings.internal_sense_resistors_enabled = false;
  }

  return settings;
}

TMC2209::Status TMC2209::getStatus()
{
  DriveStatus drive_status;
  drive_status.bytes = 0;
  drive_status.bytes = read(ADDRESS_DRV_STATUS);
  return drive_status.status;
}

TMC2209::GlobalStatus TMC2209::getGlobalStatus()
{
  GlobalStatusUnion global_status_union;
  global_status_union.bytes = 0;
  global_status_union.bytes = read(ADDRESS_GSTAT);
  return global_status_union.global_status;
}

void TMC2209::clearReset()
{
  GlobalStatusUnion global_status_union;
  global_status_union.bytes = 0;
  global_status_union.global_status.reset = 1;
  write(ADDRESS_GSTAT, global_status_union.bytes);
}

void TMC2209::clearDriveError()
{
  GlobalStatusUnion global_status_union;
  global_status_union.bytes = 0;
  global_status_union.global_status.drv_err = 1;
  write(ADDRESS_GSTAT, global_status_union.bytes);
}

uint8_t TMC2209::getInterfaceTransmissionCounter()
{
  return read(ADDRESS_IFCNT);
}

uint32_t TMC2209::getInterstepDuration()
{
  return read(ADDRESS_TSTEP);
}

uint16_t TMC2209::getStallGuardResult()
{
  return read(ADDRESS_SG_RESULT);
}

uint8_t TMC2209::getPwmScaleSum()
{
  PwmScale pwm_scale;
  pwm_scale.bytes = read(ADDRESS_PWM_SCALE);
  return pwm_scale.pwm_scale_sum;
}

int16_t TMC2209::getPwmScaleAuto()
{
  PwmScale pwm_scale;
  pwm_scale.bytes = read(ADDRESS_PWM_SCALE);
  return pwm_scale.pwm_scale_auto;
}

uint8_t TMC2209::getPwmOffsetAuto()
{
  PwmAuto pwm_auto;
  pwm_auto.bytes = read(ADDRESS_PWM_AUTO);
  return pwm_auto.pwm_offset_auto;
}

uint8_t TMC2209::getPwmGradientAuto()
{
  PwmAuto pwm_auto;
  pwm_auto.bytes = read(ADDRESS_PWM_AUTO);
  return pwm_auto.pwm_gradient_auto;
}

uint16_t TMC2209::getMicrostepCounter()
{
  return read(ADDRESS_MSCNT);
}

// =============================== MANUAL STEP CONTROL ================================ //
void TMC2209::setStepFrequency(uint32_t frequency)
{
  if (frequency == 0) return;
  if (step_timer_ == nullptr) return;

  /* 1. AUTOMATICALLY DETERMINE THE CLOCK FREQUENCY FOR THE TIMER (APB1 TIMER CLOCK) */
  // Timer Clock = PCLK1 * (if APB1 Prescaler = 1 then x1, otherwise x2)
  uint32_t pclk1 = HAL_RCC_GetPCLK1Freq();
  uint32_t timer_base_clock = pclk1;
  // Check the RCC register to see if APB1 is divided (PPRE1 bit)
  // If PPRE1 != 0 (i.e., divided by 2, 4, 8...), then the Timer Clock will double
  if ((RCC->CFGR & RCC_CFGR_PPRE1) != 0) {
    timer_base_clock = pclk1 * 2;
  }

  /* 2. AUTOMATICALLY READ PSC (PRESCALER) VALUE FROM HARDWARE */
  uint32_t current_psc = step_timer_->Instance->PSC;
  uint32_t timer_tick_frequency = timer_base_clock / (current_psc + 1);

  /* 3. CALCULATE THE FREQUENCY OF THE COUNTER (TICK) */
  // Formula: F_tick = Timer_Clock / (PSC + 1)
  // Example: 16MHz / (15 + 1) = 1MHz
  uint32_t new_arr = (timer_tick_frequency / frequency) - 1;
  uint32_t new_ccr = new_arr / 2; // Duty Cycle 50%

  /* 4. Calculating ARR (Auto Reload Register) */
  // Formula: ARR = (F_tick / F_step) - 1
  __HAL_TIM_SET_AUTORELOAD(step_timer_, new_arr);
  __HAL_TIM_SET_COMPARE(step_timer_, step_channel_, new_ccr);

  /* 5. UPDATE REGISTERS AND FIX DUTY CYCLE ERRORS */
  HAL_TIM_GenerateEvent(step_timer_, TIM_EVENTSOURCE_UPDATE);
}

void TMC2209::startStepping()
{
  if (step_timer_ != nullptr)
  {
    __HAL_TIM_SET_COUNTER(step_timer_, 0); // Reset the Counter to zero before running.
    // Start PWM
    HAL_TIM_PWM_Start(step_timer_, step_channel_);
  }
}

void TMC2209::stopStepping()
{
  if (step_timer_ == nullptr)
    return;

  HAL_TIM_PWM_Stop(step_timer_, step_channel_);
}

void TMC2209::setDirection(Direction dir) {
    if (dir == CW) {
        dir_gpio_port_->BSRR = dir_gpio_pin_;
    } else {
        dir_gpio_port_->BSRR = (uint32_t)dir_gpio_pin_ << 16U;
    }
}

void TMC2209::setMicrostepGpio(uint16_t microsteps)
{
  if (!ms1_gpio_port_ || !ms2_gpio_port_) return;

  GPIO_PinState ms1 = GPIO_PIN_RESET;
  GPIO_PinState ms2 = GPIO_PIN_RESET;

  switch (microsteps)
  {
    case 8:  ms1 = GPIO_PIN_RESET; ms2 = GPIO_PIN_RESET; break;
    case 16: ms1 = GPIO_PIN_SET;   ms2 = GPIO_PIN_SET; break;
    case 32: ms1 = GPIO_PIN_SET; ms2 = GPIO_PIN_RESET;   break;
    case 64: ms1 = GPIO_PIN_RESET;   ms2 = GPIO_PIN_SET;   break;
    default: return;
  }

  HAL_GPIO_WritePin(ms1_gpio_port_, ms1_gpio_pin_, ms1);
  HAL_GPIO_WritePin(ms2_gpio_port_, ms2_gpio_pin_, ms2);
}

void TMC2209::setSpeedRPM(float rpm, uint16_t Microsteps, float Stepangle)
{
  if (Stepangle <= 0.0f || rpm < 0.0f || Microsteps == 0) {
      return;
  }
  setMicrostepGpio(Microsteps);

  // Freq = (RPM * StepsPerRev * Microsteps) / 60
  float steps_per_rev = 360.0f / Stepangle;
  float steps_per_sec = (rpm * steps_per_rev) / 60.0f;
  float Stepfre = steps_per_sec * (float)Microsteps;

  setStepFrequency((uint32_t)Stepfre);
}
// ==================================================================================== //

void TMC2209::setStepPwmDutyCycle(uint8_t duty_percent)
{
  if (step_timer_ == nullptr || duty_percent > 100)
    return;

  // Set PWM duty cycle (50% default for symmetric pulse)
  uint32_t pulse = (timer_period_ * duty_percent) / 100;

  switch (step_channel_)
  {
    case TIM_CHANNEL_1:
      step_timer_->Instance->CCR1 = pulse;
      break;
    case TIM_CHANNEL_2:
      step_timer_->Instance->CCR2 = pulse;
      break;
    case TIM_CHANNEL_3:
      step_timer_->Instance->CCR3 = pulse;
      break;
    case TIM_CHANNEL_4:
      step_timer_->Instance->CCR4 = pulse;
      break;
  }
}

// Private methods
void TMC2209::initialize(SerialAddress serial_address)
{
  serial_address_ = serial_address;

  setOperationModeToSerial(serial_address);
  setRegistersToDefaults();
  clearDriveError();

  minimizeMotorCurrent();
  disable();
  disableAutomaticCurrentScaling();
  disableAutomaticGradientAdaptation();
}

uint32_t TMC2209::serialAvailable()
{
  if (huart_ == nullptr)
    return 0;

  // Check if data is available in receive buffer
  return (huart_->RxXferSize > 0) ? 1 : 0;
}

void TMC2209::serialWrite(uint8_t c)
{
  if (huart_ == nullptr)
    return;

  HAL_UART_Transmit(huart_, &c, 1, 1000);
}

int TMC2209::serialRead()
{
  if (huart_ == nullptr)
    return -1;

  uint8_t data = 0;
  if (HAL_UART_Receive(huart_, &data, 1, 100) == HAL_OK)
  {
    return data;
  }
  return -1;
}

void TMC2209::setOperationModeToSerial(SerialAddress serial_address)
{
  serial_address_ = serial_address;

  global_config_.bytes = 0;
  global_config_.i_scale_analog = 0;
  global_config_.pdn_disable = 1;
  global_config_.mstep_reg_select = 1;
  global_config_.multistep_filt = 1;

  writeStoredGlobalConfig();
}

void TMC2209::setRegistersToDefaults()
{
  driver_current_.bytes = 0;
  driver_current_.ihold = IHOLD_DEFAULT;
  driver_current_.irun = IRUN_DEFAULT;
  driver_current_.iholddelay = IHOLDDELAY_DEFAULT;
  write(ADDRESS_IHOLD_IRUN, driver_current_.bytes);

  chopper_config_.bytes = CHOPPER_CONFIG_DEFAULT;
  chopper_config_.tbl = TBL_DEFAULT;
  chopper_config_.hend = HEND_DEFAULT;
  chopper_config_.hstart = HSTART_DEFAULT;
  chopper_config_.toff = TOFF_DEFAULT;
  write(ADDRESS_CHOPCONF, chopper_config_.bytes);

  pwm_config_.bytes = PWM_CONFIG_DEFAULT;
  write(ADDRESS_PWMCONF, pwm_config_.bytes);

  cool_config_.bytes = COOLCONF_DEFAULT;
  write(ADDRESS_COOLCONF, cool_config_.bytes);

  write(ADDRESS_TPOWERDOWN, TPOWERDOWN_DEFAULT);
  write(ADDRESS_TPWMTHRS, TPWMTHRS_DEFAULT);
  write(ADDRESS_VACTUAL, VACTUAL_DEFAULT);
  write(ADDRESS_TCOOLTHRS, TCOOLTHRS_DEFAULT);
  write(ADDRESS_SGTHRS, SGTHRS_DEFAULT);
  write(ADDRESS_COOLCONF, COOLCONF_DEFAULT);
}

void TMC2209::readAndStoreRegisters()
{
  global_config_.bytes = readGlobalConfigBytes();
  chopper_config_.bytes = readChopperConfigBytes();
  pwm_config_.bytes = readPwmConfigBytes();
}

bool TMC2209::serialOperationMode()
{
  GlobalConfig global_config;
  global_config.bytes = readGlobalConfigBytes();
  return global_config.pdn_disable;
}

void TMC2209::minimizeMotorCurrent()
{
  driver_current_.irun = CURRENT_SETTING_MIN;
  driver_current_.ihold = CURRENT_SETTING_MIN;
  writeStoredDriverCurrent();
}

uint32_t TMC2209::reverseData(uint32_t data)
{
  uint32_t reversed_data = 0;
  uint8_t right_shift;
  uint8_t left_shift;
  for (uint8_t i = 0; i < DATA_SIZE; ++i)
  {
    right_shift = (DATA_SIZE - i - 1) * BITS_PER_BYTE;
    left_shift = i * BITS_PER_BYTE;
    reversed_data |= ((data >> right_shift) & BYTE_MAX_VALUE) << left_shift;
  }
  return reversed_data;
}

template <typename Datagram>
uint8_t TMC2209::calculateCrc(Datagram &datagram, uint8_t datagram_size)
{
  uint8_t crc = 0;
  uint8_t byte;
  for (uint8_t i = 0; i < (datagram_size - 1); ++i)
  {
    byte = (datagram.bytes >> (i * BITS_PER_BYTE)) & BYTE_MAX_VALUE;
    for (uint8_t j = 0; j < BITS_PER_BYTE; ++j)
    {
      if ((crc >> 7) ^ (byte & 0x01))
      {
        crc = (crc << 1) ^ 0x07;
      }
      else
      {
        crc = crc << 1;
      }
      byte = byte >> 1;
    }
  }
  return crc;
}

template <typename Datagram>
void TMC2209::sendDatagramUnidirectional(Datagram &datagram, uint8_t datagram_size)
{
  uint8_t byte;

  for (uint8_t i = 0; i < datagram_size; ++i)
  {
    byte = (datagram.bytes >> (i * BITS_PER_BYTE)) & BYTE_MAX_VALUE;
    serialWrite(byte);
  }
}

template <typename Datagram>
void TMC2209::sendDatagramBidirectional(Datagram &datagram, uint8_t datagram_size)
{
  uint8_t byte;

  // Wait for transmission to complete
  while (huart_->gState == HAL_UART_STATE_BUSY_TX)
    ;

  // Send datagram
  for (uint8_t i = 0; i < datagram_size; ++i)
  {
    byte = (datagram.bytes >> (i * BITS_PER_BYTE)) & BYTE_MAX_VALUE;
    serialWrite(byte);
  }

  // Wait for transmission to complete
  while (huart_->gState == HAL_UART_STATE_BUSY_TX)
    ;
}

void TMC2209::write(uint8_t register_address, uint32_t data)
{
  WriteReadReplyDatagram write_datagram;
  write_datagram.bytes = 0;
  write_datagram.sync = SYNC;
  write_datagram.serial_address = serial_address_;
  write_datagram.register_address = register_address;
  write_datagram.rw = RW_WRITE;
  write_datagram.data = reverseData(data);
  write_datagram.crc = calculateCrc(write_datagram, WRITE_READ_REPLY_DATAGRAM_SIZE);

  sendDatagramUnidirectional(write_datagram, WRITE_READ_REPLY_DATAGRAM_SIZE);
}

uint32_t TMC2209::read(uint8_t register_address)
{
  ReadRequestDatagram read_request_datagram;
  read_request_datagram.bytes = 0;
  read_request_datagram.sync = SYNC;
  read_request_datagram.serial_address = serial_address_;
  read_request_datagram.register_address = register_address;
  read_request_datagram.rw = RW_READ;
  read_request_datagram.crc = calculateCrc(read_request_datagram, READ_REQUEST_DATAGRAM_SIZE);

  for (uint8_t retry = 0; retry < MAX_READ_RETRIES; retry++)
  {
    sendDatagramBidirectional(read_request_datagram, READ_REQUEST_DATAGRAM_SIZE);

    // Wait for reply with timeout
    uint32_t timeout = 10000; // 10ms timeout
    while ((serialAvailable() < WRITE_READ_REPLY_DATAGRAM_SIZE) && (timeout > 0))
    {
      HAL_Delay(1);
      timeout--;
    }

    if (timeout == 0)
      return 0;

    uint8_t byte_count = 0;
    WriteReadReplyDatagram read_reply_datagram;
    read_reply_datagram.bytes = 0;

    for (uint8_t i = 0; i < WRITE_READ_REPLY_DATAGRAM_SIZE; ++i)
    {
      int data = serialRead();
      if (data >= 0)
      {
        read_reply_datagram.bytes |= ((uint64_t)data << (byte_count++ * BITS_PER_BYTE));
      }
    }

    auto crc = calculateCrc(read_reply_datagram, WRITE_READ_REPLY_DATAGRAM_SIZE);
    if (crc == read_reply_datagram.crc)
    {
      return reverseData(read_reply_datagram.data);
    }

    HAL_Delay(READ_RETRY_DELAY_MS);
  }

  return 0;
}

uint8_t TMC2209::percentToCurrentSetting(uint8_t percent)
{
  uint8_t constrained_percent = constrain_(percent, PERCENT_MIN, PERCENT_MAX);
  uint8_t current_setting = (constrained_percent * (CURRENT_SETTING_MAX - CURRENT_SETTING_MIN)) / (PERCENT_MAX - PERCENT_MIN) + CURRENT_SETTING_MIN;
  return current_setting;
}

uint8_t TMC2209::currentSettingToPercent(uint8_t current_setting)
{
  uint8_t percent = (current_setting * (PERCENT_MAX - PERCENT_MIN)) / (CURRENT_SETTING_MAX - CURRENT_SETTING_MIN) + PERCENT_MIN;
  return percent;
}

uint8_t TMC2209::percentToHoldDelaySetting(uint8_t percent)
{
  uint8_t constrained_percent = constrain_(percent, PERCENT_MIN, PERCENT_MAX);
  uint8_t hold_delay_setting = (constrained_percent * (HOLD_DELAY_MAX - HOLD_DELAY_MIN)) / (PERCENT_MAX - PERCENT_MIN) + HOLD_DELAY_MIN;
  return hold_delay_setting;
}

uint8_t TMC2209::holdDelaySettingToPercent(uint8_t hold_delay_setting)
{
  uint8_t percent = (hold_delay_setting * (PERCENT_MAX - PERCENT_MIN)) / (HOLD_DELAY_MAX - HOLD_DELAY_MIN) + PERCENT_MIN;
  return percent;
}

void TMC2209::writeStoredGlobalConfig()
{
  write(ADDRESS_GCONF, global_config_.bytes);
}

uint32_t TMC2209::readGlobalConfigBytes()
{
  return read(ADDRESS_GCONF);
}

void TMC2209::writeStoredDriverCurrent()
{
  write(ADDRESS_IHOLD_IRUN, driver_current_.bytes);

  if (driver_current_.irun >= SEIMIN_UPPER_CURRENT_LIMIT)
  {
    cool_config_.seimin = SEIMIN_UPPER_SETTING;
  }
  else
  {
    cool_config_.seimin = SEIMIN_LOWER_SETTING;
  }
  if (cool_step_enabled_)
  {
    write(ADDRESS_COOLCONF, cool_config_.bytes);
  }
}

void TMC2209::writeStoredChopperConfig()
{
  write(ADDRESS_CHOPCONF, chopper_config_.bytes);
}

uint32_t TMC2209::readChopperConfigBytes()
{
  return read(ADDRESS_CHOPCONF);
}

void TMC2209::writeStoredPwmConfig()
{
  write(ADDRESS_PWMCONF, pwm_config_.bytes);
}

uint32_t TMC2209::readPwmConfigBytes()
{
  return read(ADDRESS_PWMCONF);
}

uint32_t TMC2209::constrain_(uint32_t value, uint32_t low, uint32_t high)
{
  return ((value) < (low) ? (low) : ((value) > (high) ? (high) : (value)));
}
