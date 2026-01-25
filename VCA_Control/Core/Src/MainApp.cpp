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
extern UART_HandleTypeDef huart2;
extern TIM_HandleTypeDef htim3;

/* ============= Global Variables ============= */
TMC2209 stepper;

/* ============= Application Setup ============= */
void App_Setup(void)
{
  // Truyền nullptr vào tham số UART để thư viện biết không cần giao tiếp
  stepper.setup(&huart2,                // UART
	              EN_PORT, EN_PIN,      // Enable
	              DIR_PORT, DIR_PIN,    // Direction
	              &htim3, TIM_CHANNEL_3,// Timer PWM
	              MS1_PORT, MS1_PIN,    // Microstep 1
	              MS2_PORT, MS2_PIN,    // Microstep 2
	              TMC2209::SERIAL_ADDRESS_0);

  stepper.enable();
  stepper.setMicrostepGpio(8);
}

/* ============= Application Loop ============= */
void App_Loop(void)
{
  // --- 1. QUAY THUẬN (FORWARD) ---
  // Điều khiển trực tiếp mức logic chân DIR
  stepper.setDirection(CW);
  // Bắt đầu phát xung PWM
  stepper.setSpeedRPM(60, 16, 1.8);
  stepper.startStepping();
  // Chạy trong 3 giây
  HAL_Delay(3000);
  // --- 2. DỪNG (STOP) ---
  stepper.stopStepping();
  // Nghỉ 1 giây
  HAL_Delay(1000);


  // --- 3. QUAY NGHỊCH (REVERSE) ---
  // Đảo trạng thái chân DIR
  stepper.setDirection(CCW);
  // Bắt đầu phát xung PWM
  stepper.setSpeedRPM(120, 16, 1.8);
  stepper.startStepping();
  // Chạy trong 3 giây
  HAL_Delay(3000);
  // --- 4. DỪNG (STOP) ---
  stepper.stopStepping();
  // Nghỉ 1 giây
  HAL_Delay(1000);
}
