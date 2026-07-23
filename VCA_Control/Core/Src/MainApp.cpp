#include "MainApp.hpp"
#include "TMC2209.hpp"
#include "stm32f4xx_hal.h"
#include <cstring>
#include <cstdio>
#include <cstdlib>
#include <cmath>
#include "usbd_cdc_if.h"

/* ============= Hardware Definitions ============= */
#define DIR_PORT    GPIOA
#define DIR_PIN     GPIO_PIN_6
#define EN_PORT     GPIOB
#define EN_PIN      GPIO_PIN_10
#define MS1_PORT    GPIOB
#define MS1_PIN     GPIO_PIN_2
#define MS2_PORT    GPIOB
#define MS2_PIN     GPIO_PIN_1
#define RX_BUFFER_SIZE 128

#define SW_PORT     GPIOB
#define SW_TREN_PIN GPIO_PIN_14
#define SW_DUOI_PIN GPIO_PIN_15

/* ============= Global Objects ============= */
extern TIM_HandleTypeDef htim3;
TMC2209 stepper;

/* ================ Variables =============== */
static char rx_buffer[RX_BUFFER_SIZE];
static uint16_t rx_index = 0;

uint32_t start_time_SwTren = 0;
uint32_t start_time_SwDuoi = 0;

volatile bool current_direction_is_cw = false; // false = CW, true = CW
volatile bool command_received = false;
volatile bool emergency_triggered = false;
volatile bool blocked_CW = false;  // Bottom Limit
volatile bool blocked_CCW = false; // Top Limit
bool was_moving = false;

/* ============= Send command to PC ============= */
void Send_To_PC(const char* str) {
    uint32_t startTick = HAL_GetTick();
    uint8_t result;

    do {
        result = CDC_Transmit_FS((uint8_t*)str, strlen(str));
    } while (result == USBD_BUSY && (HAL_GetTick() - startTick < 10));
}

/* ============= PeriodElapsedCallback ============= */
void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim) {
  if (htim->Instance == TIM3)
  {
    stepper.handleTimerISR();
  }
}

/* ============= Get Direction Function ============= */
bool Is_Direction_CW(void) {
    return current_direction_is_cw;
}

/* ============= EXTI_Callback ============= */
void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin) {
    uint32_t current_tick = HAL_GetTick();

    if (GPIO_Pin == SW_TREN_PIN) {
        if (current_tick - start_time_SwTren > 50) {
            GPIO_PinState pinState = HAL_GPIO_ReadPin(SW_PORT, SW_TREN_PIN);
            if ((!Is_Direction_CW() && pinState) == GPIO_PIN_SET) {
            	if (!blocked_CCW) {
            		stepper.stopMove();
            		stepper.disable();
            		emergency_triggered = true;
            		rx_index = 0;
            		command_received = false;
            	}
            	blocked_CCW = true;
            }else blocked_CCW = false;
            start_time_SwTren = current_tick;
        }
    } else if (GPIO_Pin == SW_DUOI_PIN) {
        if (current_tick - start_time_SwDuoi > 50) {
            GPIO_PinState pinState = HAL_GPIO_ReadPin(SW_PORT, SW_DUOI_PIN);
            if ((Is_Direction_CW() && pinState) == GPIO_PIN_SET) {
            	if (!blocked_CW) {
            		stepper.stopMove();
            		stepper.disable();
            		emergency_triggered = true;
            		rx_index = 0;
            		command_received = false;
            	}
            	blocked_CW = true;
            }else blocked_CW = false;
            start_time_SwDuoi = current_tick;
        }
    }
}

/* ============= Processing Data USB ============= */
void App_USB_Data_Rx_Handler(uint8_t* Buf, uint32_t Len) {
    for (uint32_t i = 0; i < Len; i++) {
        char c = (char)Buf[i];
        if (c == '\r' || c == '\n') continue;
        if (c == '#') {
            rx_index = 0;
            memset(rx_buffer, 0, RX_BUFFER_SIZE);
        }

        if (rx_index < RX_BUFFER_SIZE - 1) {
            rx_buffer[rx_index++] = c;
        }

        if (c == '!') {
            rx_buffer[rx_index] = '\0';
            command_received = true;
        }
    }
}

/* ============= Reset Command State ============= */
void Reset_Command_State() {
    rx_index = 0;
    command_received = false;
    memset(rx_buffer, 0, RX_BUFFER_SIZE);
}

/* ============= Check Safety ============= */
bool Is_Safety_Move(bool is_cw_direction) {

    if (is_cw_direction && blocked_CW) {
        Send_To_PC("ERR: Locked CW (Bottom Hit)! Move CCW to release.\r\n");
        return false;
    }else if (!is_cw_direction && blocked_CCW) {
        Send_To_PC("ERR: Locked CCW (Top Hit)! Move CW to release.\r\n");
        return false;
    }

    return true;
}

/* ============= Process Main Order ============= */
void Process_Serial_Command() {
    char* dir_str = nullptr;
    char* dist_str = nullptr;
    char* speed_str = nullptr;
    char* stop_str = nullptr;

    float distance = 0.0f;
    float speed = 0.0f;
    int stop_step = 0;

    if (rx_buffer[0] != '#') {
        Send_To_PC("ERR: Invalid Format (Missing #)\r\n");
        Reset_Command_State();
        return;
    }

    char cmd_copy[RX_BUFFER_SIZE];
    strncpy(cmd_copy, rx_buffer, RX_BUFFER_SIZE);

    dir_str = strtok(cmd_copy + 1, ",");
    dist_str = strtok(NULL, ",");
    speed_str = strtok(NULL, ",");
    stop_str = strtok(NULL, "!");

    if (dir_str == nullptr || dist_str == nullptr || speed_str == nullptr || stop_str == nullptr) {
        Send_To_PC("ERR: Syntax Error (Need 4 params)\r\n");
        Reset_Command_State();
        return;
    }

    distance = strtof(dist_str, NULL);
    speed = strtof(speed_str, NULL);
    stop_step = atoi(stop_str);

    if (stop_step == -1) {
        stepper.stopMove();
        stepper.disable();
        Send_To_PC("STOP: Software Command Executed!\r\n");
        Reset_Command_State();
        return;
    }

    if (stepper.isMoving()) {
        Send_To_PC("BUSY: Motor is running...\r\n");
        Reset_Command_State();
        return;
    }

    if (speed <= 0 || distance == 0) {
        Send_To_PC("ERR: Invalid Param\r\n");
        Reset_Command_State();
        return;
    }

    bool is_cw = (strcmp(dir_str, "CW") == 0);
    if (!is_cw && strcmp(dir_str, "CCW") != 0) {
        Send_To_PC("ERR: Wrong Dir\r\n");
        Reset_Command_State();
        return;
    }

    if (!Is_Safety_Move(is_cw)) {
        Reset_Command_State();
        return;
    }

    if (is_cw) {
        stepper.setDirection(CW);
        current_direction_is_cw = true;
    } else {
        stepper.setDirection(CCW);
        current_direction_is_cw = false;
        distance = -distance; // Ensure sign is correct
    }

    stepper.enable();
    HAL_Delay(5);
    stepper.moveRelativeDistance(distance, speed);

    was_moving = true;
    Reset_Command_State();
}

void App_Setup(void) {
  stepper.setup(EN_PORT, EN_PIN, DIR_PORT, DIR_PIN, &htim3, TIM_CHANNEL_3);
  stepper.configureMicrostepPins(MS1_PORT, MS1_PIN, MS2_PORT, MS2_PIN);
  stepper.setMicrostepGpio(16);
  stepper.setStepAngle(1.8f);
  stepper.setScrewPitch(1.25f);

  stepper.disable();
  HAL_TIM_Base_Start_IT(&htim3);
}

void App_Loop(void) {
//	HAL_GPIO_WritePin(GPIOC, GPIO_PIN_13, GPIO_PIN_RESET);
  if (emergency_triggered) {
      char alert_msg[32];
      sprintf(alert_msg, "ALARM: STOP by EXTI!\r\n");
      Send_To_PC(alert_msg);
      emergency_triggered = false;
  }

  bool current_moving = stepper.isMoving();

  if (was_moving && !current_moving) {
      HAL_Delay(50);
      stepper.disable();
  }
  was_moving = current_moving;

  if (command_received) {
      Process_Serial_Command();
  }

}
