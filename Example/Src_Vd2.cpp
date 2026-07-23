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
  // --- TEST 1: Quay chính xác 1 vòng (360 độ) ---
  stepper.setDirection(CW); // Quay thuận

  // Quay 360 độ, tốc độ 60 RPM
  // Thư viện tự tính toán số bước dựa trên StepAngle (1.8) và Microstep (16)
  stepper.moveDegrees(360.0f, 100.0f);

  // Chờ cho đến khi động cơ dừng hẳn
  while (stepper.isMoving())
  {
    HAL_Delay(10);
  }
  HAL_Delay(1000); // Nghỉ 1 giây

  // --- TEST 2: Quay chính xác 1000 bước ---
  stepper.setDirection(CCW); // Quay nghịch

  // Quay 1000 bước, tốc độ 120 RPM
  stepper.moveSteps(3200, 190.0f);

  while (stepper.isMoving())
  {
    HAL_Delay(10);
  }
  HAL_Delay(1000);
}
