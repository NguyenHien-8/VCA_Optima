#include "MainApp.hpp"
#include "main.h" // Để dùng các thư viện HAL

// Tại đây bạn có thể dùng Class, Object thoải mái
void App_Setup(void) {
    // Viết code khởi tạo của bạn ở đây (ví dụ: khởi tạo biến, class)
}

void App_Loop(void) {
    // Viết code vòng lặp chính ở đây
    HAL_GPIO_TogglePin(GPIOC, GPIO_PIN_13); // Ví dụ nháy LED
    HAL_Delay(500);
}
