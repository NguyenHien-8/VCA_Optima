#ifndef MAINAPP_HPP_
#define MAINAPP_HPP_

#ifdef __cplusplus
extern "C" {
#endif

#include <stdint.h>
#include <stdbool.h>

void App_Setup(void);
void App_Loop(void);
void App_USB_Data_Rx_Handler(uint8_t* Buf, uint32_t Len);

#ifdef __cplusplus
}
#endif

#endif
