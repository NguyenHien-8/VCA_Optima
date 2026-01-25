#include "MainApp.hpp"
#include "TMC2209.hpp"
#include "stm32f4xx_hal.h"

/* ============= Hardware Definitions ============= */
#define DIR_PORT    GPIOA
#define DIR_PIN     GPIO_PIN_6
#define EN_PORT     GPIOB
#define EN_PIN      GPIO_PIN_10

#define MS1_PORT    GPIOB
#define MS1_PIN     GPIO_PIN_2
#define MS2_PORT    GPIOB
#define MS2_PIN     GPIO_PIN_1

/* ============= External References ============= */
//extern UART_HandleTypeDef huart2;
extern TIM_HandleTypeDef htim3;

/* ============= Global Variables ============= */
TMC2209 stepper;
/* ============= Interrupt Callback ============= */
void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim)
{
  if (htim->Instance == TIM3)
  {
    stepper.handleTimerISR();
  }
}

void App_Setup(void)
{
  stepper.setup(EN_PORT, EN_PIN,
	            DIR_PORT, DIR_PIN,
	            &htim3, TIM_CHANNEL_3);

  stepper.configureMicrostepPins(MS1_PORT, MS1_PIN,
                                 MS2_PORT, MS2_PIN);
  stepper.enable();
  stepper.setStepAngle(1.8);
  stepper.setMicrostepGpio(16);
}

void App_Loop(void)
{
  // --- 1. QUAY THUẬN (FORWARD) ---
  stepper.setDirection(CW);
  stepper.setSpeedRPM(60, 16, 1.8);
  stepper.startStepping();
  HAL_Delay(3000);

  // --- 2. DỪNG (STOP) ---
  stepper.stopStepping();
  HAL_Delay(1000);

  // --- 3. QUAY NGHỊCH (REVERSE) ---
  stepper.setDirection(CCW);
  stepper.setSpeedRPM(120, 16, 1.8);
  stepper.startStepping();
  HAL_Delay(3000);

  // --- 4. DỪNG (STOP) ---
  stepper.stopStepping();
  HAL_Delay(1000);
}