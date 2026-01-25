#ifndef TMC2209_HPP_
#define TMC2209_HPP_

#ifdef __cplusplus
extern "C" {
#endif

#include "stm32f4xx_hal.h"
#include <cstdint>
#include <cstring>

#ifdef __cplusplus
}
#endif

enum Direction { CW = 0, CCW = 1 };

class TMC2209
{
public:
  TMC2209();
  ~TMC2209();

  enum SerialAddress
  {
    SERIAL_ADDRESS_0 = 0,
    SERIAL_ADDRESS_1 = 1,
    SERIAL_ADDRESS_2 = 2,
    SERIAL_ADDRESS_3 = 3,
  };

// ===================== MANUAL STEP CONTROL ===================== //
  // Initialize UART and GPIO
  void setup(UART_HandleTypeDef *huart,
               GPIO_TypeDef *en_gpio_port, uint16_t en_gpio_pin,
               GPIO_TypeDef *dir_gpio_port, uint16_t dir_gpio_pin,
               TIM_HandleTypeDef *step_timer, uint32_t step_channel,
               GPIO_TypeDef *ms1_gpio_port, uint16_t ms1_gpio_pin,
               GPIO_TypeDef *ms2_gpio_port, uint16_t ms2_gpio_pin,
               SerialAddress serial_address = SERIAL_ADDRESS_0);

  // Enable/Disable motor
  void setHardwareEnablePin(GPIO_TypeDef *gpio_port, uint16_t gpio_pin);
  void enable();
  void disable();
  void setMicrostepGpio(uint16_t microsteps); // microstep (8, 16, 32, 64)
// =============================================================== //

  // Motor direction
  void enableInverseMotorDirection();
  void disableInverseMotorDirection();

  // Microstepping
  void setMicrostepsPerStep(uint16_t microsteps_per_step);
  void setMicrostepsPerStepPowerOfTwo(uint8_t exponent);

  // Current control
  void setRunCurrent(uint8_t percent);
  void setHoldCurrent(uint8_t percent);
  void setHoldDelay(uint8_t percent);
  void setAllCurrentValues(uint8_t run_current_percent,
                           uint8_t hold_current_percent,
                           uint8_t hold_delay_percent);
  void setRMSCurrent(uint16_t mA, float rSense, float holdMultiplier = 0.5f);

  // PWM Configuration
  void enableDoubleEdge();
  void disableDoubleEdge();
  void enableVSense();
  void disableVSense();

  // Standstill and Automatic Control
  enum StandstillMode
  {
    NORMAL = 0,
    FREEWHEELING = 1,
    STRONG_BRAKING = 2,
    BRAKING = 3,
  };
  void setStandstillMode(StandstillMode mode);
  void enableAutomaticCurrentScaling();
  void disableAutomaticCurrentScaling();
  void enableAutomaticGradientAdaptation();
  void disableAutomaticGradientAdaptation();
  void setPwmOffset(uint8_t pwm_amplitude);
  void setPwmGradient(uint8_t pwm_amplitude);

  // Power and timing
  void setPowerDownDelay(uint8_t power_down_delay);
  void setReplyDelay(uint8_t reply_delay);

  // StealthChop and speed control
  void enableStealthChop();
  void disableStealthChop();
  void setStealthChopDurationThreshold(uint32_t duration_threshold);

  // Velocity and stepping
  void moveAtVelocity(int32_t microsteps_per_period);
  void moveUsingStepDirInterface();

// ========== MANUAL STEP CONTROL ========== //
  void setStepFrequency(uint32_t frequency_hz);
  void setSpeedRPM(float rpm, uint16_t Microsteps, float Stepangle);
  void setStepPwmDutyCycle(uint8_t duty_percent);
  void startStepping();
  void stopStepping();
  void setDirection(Direction dir);
// ========================================= //

  // Stall detection
  void setStallGuardThreshold(uint8_t stall_guard_threshold);

  // CoolStep
  void enableCoolStep(uint8_t lower_threshold = 1,
                      uint8_t upper_threshold = 0);
  void disableCoolStep();
  enum CurrentIncrement
  {
    CURRENT_INCREMENT_1 = 0,
    CURRENT_INCREMENT_2 = 1,
    CURRENT_INCREMENT_4 = 2,
    CURRENT_INCREMENT_8 = 3,
  };
  void setCoolStepCurrentIncrement(CurrentIncrement current_increment);
  enum MeasurementCount
  {
    MEASUREMENT_COUNT_32 = 0,
    MEASUREMENT_COUNT_8 = 1,
    MEASUREMENT_COUNT_2 = 2,
    MEASUREMENT_COUNT_1 = 3,
  };
  void setCoolStepMeasurementCount(MeasurementCount measurement_count);
  void setCoolStepDurationThreshold(uint32_t duration_threshold);

  // Sense resistor configuration
  void enableAnalogCurrentScaling();
  void disableAnalogCurrentScaling();
  void useExternalSenseResistors();
  void useInternalSenseResistors();

  // Status and diagnostics
  uint8_t getVersion();
  bool isCommunicating();
  bool isSetupAndCommunicating();
  bool isCommunicatingButNotSetup();
  bool hardwareDisabled();
  uint16_t getMicrostepsPerStep();

  struct Settings
  {
    bool is_communicating;
    bool is_setup;
    bool software_enabled;
    uint16_t microsteps_per_step;
    bool inverse_motor_direction_enabled;
    bool stealth_chop_enabled;
    uint8_t standstill_mode;
    uint8_t irun_percent;
    uint8_t irun_register_value;
    uint8_t ihold_percent;
    uint8_t ihold_register_value;
    uint8_t iholddelay_percent;
    uint8_t iholddelay_register_value;
    bool automatic_current_scaling_enabled;
    bool automatic_gradient_adaptation_enabled;
    uint8_t pwm_offset;
    uint8_t pwm_gradient;
    bool cool_step_enabled;
    bool analog_current_scaling_enabled;
    bool internal_sense_resistors_enabled;
  };
  Settings getSettings();

  struct Status
  {
    uint32_t over_temperature_warning : 1;
    uint32_t over_temperature_shutdown : 1;
    uint32_t short_to_ground_a : 1;
    uint32_t short_to_ground_b : 1;
    uint32_t low_side_short_a : 1;
    uint32_t low_side_short_b : 1;
    uint32_t open_load_a : 1;
    uint32_t open_load_b : 1;
    uint32_t over_temperature_120c : 1;
    uint32_t over_temperature_143c : 1;
    uint32_t over_temperature_150c : 1;
    uint32_t over_temperature_157c : 1;
    uint32_t reserved0 : 4;
    uint32_t current_scaling : 5;
    uint32_t reserved1 : 9;
    uint32_t stealth_chop_mode : 1;
    uint32_t standstill : 1;
  };
  static const uint8_t CURRENT_SCALING_MAX = 31;
  Status getStatus();

  struct GlobalStatus
  {
    uint32_t reset : 1;
    uint32_t drv_err : 1;
    uint32_t uv_cp : 1;
    uint32_t reserved : 29;
  };
  GlobalStatus getGlobalStatus();
  void clearReset();
  void clearDriveError();

  uint8_t getInterfaceTransmissionCounter();
  uint32_t getInterstepDuration();
  uint16_t getStallGuardResult();
  uint8_t getPwmScaleSum();
  int16_t getPwmScaleAuto();
  uint8_t getPwmOffsetAuto();
  uint8_t getPwmGradientAuto();
  uint16_t getMicrostepCounter();

private:
  UART_HandleTypeDef *huart_;
    uint32_t serial_baud_rate_;
    uint8_t serial_address_;

    // Các chân điều khiển GPIO
    GPIO_TypeDef *dir_gpio_port_;
    uint16_t dir_gpio_pin_;

    GPIO_TypeDef *en_gpio_port_;
    uint16_t en_gpio_pin_;

    // Biến lưu chân Microstep
    GPIO_TypeDef *ms1_gpio_port_;
    uint16_t ms1_gpio_pin_;
    GPIO_TypeDef *ms2_gpio_port_;
    uint16_t ms2_gpio_pin_;

    // Timer cho PWM
    TIM_HandleTypeDef *step_timer_;
    uint32_t step_channel_;
    uint32_t timer_period_;

    // Các biến nội bộ trạng thái
    bool initialized_;

  // Register unions and structures
  union GlobalConfig
  {
    struct
    {
      uint32_t i_scale_analog : 1;
      uint32_t internal_rsense : 1;
      uint32_t enable_spread_cycle : 1;
      uint32_t shaft : 1;
      uint32_t index_otpw : 1;
      uint32_t index_step : 1;
      uint32_t pdn_disable : 1;
      uint32_t mstep_reg_select : 1;
      uint32_t multistep_filt : 1;
      uint32_t test_mode : 1;
      uint32_t reserved : 22;
    };
    uint32_t bytes;
  };

  union DriverCurrent
  {
    struct
    {
      uint32_t ihold : 5;
      uint32_t reserved_0 : 3;
      uint32_t irun : 5;
      uint32_t reserved_1 : 3;
      uint32_t iholddelay : 4;
      uint32_t reserved_2 : 12;
    };
    uint32_t bytes;
  };

  union ChopperConfig
  {
    struct
    {
      uint32_t toff : 4;
      uint32_t hstart : 3;
      uint32_t hend : 4;
      uint32_t reserved_0 : 4;
      uint32_t tbl : 2;
      uint32_t vsense : 1;
      uint32_t reserved_1 : 6;
      uint32_t mres : 4;
      uint32_t interpolation : 1;
      uint32_t double_edge : 1;
      uint32_t diss2g : 1;
      uint32_t diss2vs : 1;
    };
    uint32_t bytes;
  };

  union PwmConfig
  {
    struct
    {
      uint32_t pwm_offset : 8;
      uint32_t pwm_grad : 8;
      uint32_t pwm_freq : 2;
      uint32_t pwm_autoscale : 1;
      uint32_t pwm_autograd : 1;
      uint32_t freewheel : 2;
      uint32_t reserved : 2;
      uint32_t pwm_reg : 4;
      uint32_t pwm_lim : 4;
    };
    uint32_t bytes;
  };

  union CoolConfig
  {
    struct
    {
      uint32_t semin : 4;
      uint32_t reserved_0 : 1;
      uint32_t seup : 2;
      uint32_t reserved_1 : 1;
      uint32_t semax : 4;
      uint32_t reserved_2 : 1;
      uint32_t sedn : 2;
      uint32_t seimin : 1;
      uint32_t reserved_3 : 16;
    };
    uint32_t bytes;
  };

  union Input
  {
    struct
    {
      uint32_t enn : 1;
      uint32_t reserved_0 : 1;
      uint32_t ms1 : 1;
      uint32_t ms2 : 1;
      uint32_t diag : 1;
      uint32_t reserved_1 : 1;
      uint32_t pdn_serial : 1;
      uint32_t step : 1;
      uint32_t spread_en : 1;
      uint32_t dir : 1;
      uint32_t reserved_2 : 14;
      uint32_t version : 8;
    };
    uint32_t bytes;
  };

  union GlobalStatusUnion
  {
    struct
    {
      GlobalStatus global_status;
    };
    uint32_t bytes;
  };

  union DriveStatus
  {
    struct
    {
      Status status;
    };
    uint32_t bytes;
  };

  union PwmScale
  {
    struct
    {
      uint32_t pwm_scale_sum : 8;
      uint32_t reserved_0 : 8;
      uint32_t pwm_scale_auto : 9;
      uint32_t reserved_1 : 7;
    };
    uint32_t bytes;
  };

  union PwmAuto
  {
    struct
    {
      uint32_t pwm_offset_auto : 8;
      uint32_t reserved_0 : 8;
      uint32_t pwm_gradient_auto : 8;
      uint32_t reserved_1 : 8;
    };
    uint32_t bytes;
  };

  union WriteReadReplyDatagram
  {
    struct
    {
      uint64_t sync : 4;
      uint64_t reserved : 4;
      uint64_t serial_address : 8;
      uint64_t register_address : 7;
      uint64_t rw : 1;
      uint64_t data : 32;
      uint64_t crc : 8;
    };
    uint64_t bytes;
  };

  union ReadRequestDatagram
  {
    struct
    {
      uint32_t sync : 4;
      uint32_t reserved : 4;
      uint32_t serial_address : 8;
      uint32_t register_address : 7;
      uint32_t rw : 1;
      uint32_t crc : 8;
    };
    uint32_t bytes;
  };

  union ReplyDelay
  {
    struct
    {
      uint32_t reserved_0 : 8;
      uint32_t replydelay : 4;
      uint32_t reserved_1 : 20;
    };
    uint32_t bytes;
  };

  // Private helper methods
  void initialize(SerialAddress serial_address);
  void setOperationModeToSerial(SerialAddress serial_address);
  void setRegistersToDefaults();
  void readAndStoreRegisters();
  bool serialOperationMode();
  void minimizeMotorCurrent();

  void serialWrite(uint8_t c);
  int serialRead();
  uint32_t serialAvailable();

  uint32_t reverseData(uint32_t data);
  template <typename Datagram>
  uint8_t calculateCrc(Datagram &datagram, uint8_t datagram_size);
  template <typename Datagram>
  void sendDatagramUnidirectional(Datagram &datagram, uint8_t datagram_size);
  template <typename Datagram>
  void sendDatagramBidirectional(Datagram &datagram, uint8_t datagram_size);

  void write(uint8_t register_address, uint32_t data);
  uint32_t read(uint8_t register_address);

  uint8_t percentToCurrentSetting(uint8_t percent);
  uint8_t currentSettingToPercent(uint8_t current_setting);
  uint8_t percentToHoldDelaySetting(uint8_t percent);
  uint8_t holdDelaySettingToPercent(uint8_t hold_delay_setting);

  void writeStoredGlobalConfig();
  uint32_t readGlobalConfigBytes();
  void writeStoredDriverCurrent();
  void writeStoredChopperConfig();
  uint32_t readChopperConfigBytes();
  void writeStoredPwmConfig();
  uint32_t readPwmConfigBytes();

  uint32_t constrain_(uint32_t value, uint32_t low, uint32_t high);

  // Configuration register storage
  GlobalConfig global_config_;
  DriverCurrent driver_current_;
  ChopperConfig chopper_config_;
  PwmConfig pwm_config_;
  CoolConfig cool_config_;
  bool cool_step_enabled_;
  uint8_t toff_;

  // Constants
  static const uint8_t BYTE_MAX_VALUE = 0xFF;
  static const uint8_t BITS_PER_BYTE = 8;
  static const uint32_t ECHO_DELAY_INC_MICROSECONDS = 1;
  static const uint32_t ECHO_DELAY_MAX_MICROSECONDS = 4000;
  static const uint32_t REPLY_DELAY_INC_MICROSECONDS = 1;
  static const uint32_t REPLY_DELAY_MAX_MICROSECONDS = 10000;
  static const uint8_t MAX_READ_RETRIES = 5;
  static const uint32_t READ_RETRY_DELAY_MS = 20;
  static const uint8_t WRITE_READ_REPLY_DATAGRAM_SIZE = 8;
  static const uint8_t DATA_SIZE = 4;
  static const uint8_t SYNC = 0b101;
  static const uint8_t RW_READ = 0;
  static const uint8_t RW_WRITE = 1;
  static const uint8_t READ_REPLY_SERIAL_ADDRESS = 0xFF;
  static const uint8_t READ_REQUEST_DATAGRAM_SIZE = 4;
  static const uint8_t VERSION = 0x21;
  static const uint8_t REPLY_DELAY_MAX = 15;

  // Register addresses
  static const uint8_t ADDRESS_GCONF = 0x00;
  static const uint8_t ADDRESS_GSTAT = 0x01;
  static const uint8_t ADDRESS_IFCNT = 0x02;
  static const uint8_t ADDRESS_REPLYDELAY = 0x03;
  static const uint8_t ADDRESS_IOIN = 0x06;
  static const uint8_t ADDRESS_IHOLD_IRUN = 0x10;
  static const uint8_t ADDRESS_TPOWERDOWN = 0x11;
  static const uint8_t ADDRESS_TSTEP = 0x12;
  static const uint8_t ADDRESS_TPWMTHRS = 0x13;
  static const uint8_t ADDRESS_TCOOLTHRS = 0x14;
  static const uint8_t ADDRESS_VACTUAL = 0x22;
  static const uint8_t ADDRESS_SGTHRS = 0x40;
  static const uint8_t ADDRESS_SG_RESULT = 0x41;
  static const uint8_t ADDRESS_COOLCONF = 0x42;
  static const uint8_t ADDRESS_CHOPCONF = 0x6C;
  static const uint8_t ADDRESS_DRV_STATUS = 0x6F;
  static const uint8_t ADDRESS_PWMCONF = 0x70;
  static const uint8_t ADDRESS_PWM_SCALE = 0x71;
  static const uint8_t ADDRESS_PWM_AUTO = 0x72;
  static const uint8_t ADDRESS_MSCNT = 0x6A;
  static const uint8_t ADDRESS_MSCURACT = 0x6B;

  // Default values
  static const uint8_t IHOLD_DEFAULT = 16;
  static const uint8_t IRUN_DEFAULT = 31;
  static const uint8_t IHOLDDELAY_DEFAULT = 1;
  static const uint8_t TPOWERDOWN_DEFAULT = 20;
  static const uint32_t TPWMTHRS_DEFAULT = 0;
  static const int32_t VACTUAL_DEFAULT = 0;
  static const int32_t VACTUAL_STEP_DIR_INTERFACE = 0;
  static const uint8_t TCOOLTHRS_DEFAULT = 0;
  static const uint8_t SGTHRS_DEFAULT = 0;
  static const uint8_t COOLCONF_DEFAULT = 0;
  static const uint32_t CHOPPER_CONFIG_DEFAULT = 0x10000053;
  static const uint32_t PWM_CONFIG_DEFAULT = 0xC10D0024;
  static const uint8_t TBL_DEFAULT = 0b10;
  static const uint8_t HEND_DEFAULT = 0;
  static const uint8_t HSTART_DEFAULT = 5;
  static const uint8_t TOFF_DEFAULT = 3;
  static const uint8_t TOFF_DISABLE = 0;
  static const uint8_t PERCENT_MIN = 0;
  static const uint8_t PERCENT_MAX = 100;
  static const uint8_t CURRENT_SETTING_MIN = 0;
  static const uint8_t CURRENT_SETTING_MAX = 31;
  static const uint8_t HOLD_DELAY_MIN = 0;
  static const uint8_t HOLD_DELAY_MAX = 15;
  static const uint8_t SEIMIN_UPPER_CURRENT_LIMIT = 20;
  static const uint8_t SEIMIN_LOWER_SETTING = 0;
  static const uint8_t SEIMIN_UPPER_SETTING = 1;
  static const uint8_t SEMIN_OFF = 0;
  static const uint8_t SEMIN_MIN = 1;
  static const uint8_t SEMIN_MAX = 15;
  static const uint8_t SEMAX_MIN = 0;
  static const uint8_t SEMAX_MAX = 15;
  static const uint8_t MRES_256 = 0b0000;
  static const uint8_t MRES_128 = 0b0001;
  static const uint8_t MRES_064 = 0b0010;
  static const uint8_t MRES_032 = 0b0011;
  static const uint8_t MRES_016 = 0b0100;
  static const uint8_t MRES_008 = 0b0101;
  static const uint8_t MRES_004 = 0b0110;
  static const uint8_t MRES_002 = 0b0111;
  static const uint8_t MRES_001 = 0b1000;
  static const uint8_t DOUBLE_EDGE_DISABLE = 0;
  static const uint8_t DOUBLE_EDGE_ENABLE = 1;
  static const uint8_t VSENSE_DISABLE = 0;
  static const uint8_t VSENSE_ENABLE = 1;
  static const uint8_t STEPPER_DRIVER_FEATURE_OFF = 0;
  static const uint8_t STEPPER_DRIVER_FEATURE_ON = 1;
  static const size_t MICROSTEPS_PER_STEP_MIN = 1;
  static const size_t MICROSTEPS_PER_STEP_MAX = 256;
};

#endif /* TMC2209_HPP_ */
