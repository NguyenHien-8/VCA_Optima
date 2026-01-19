#include "MainApp.hpp"
#include "TMC2209.hpp"

extern TIM_HandleTypeDef htim3;

// Khởi tạo Static (Không dùng new -> Không phân mảnh bộ nhớ)
TMC2209 MyStep(GPIOB, GPIO_PIN_10,
                GPIOA, GPIO_PIN_6,
                &htim3, TIM_CHANNEL_3);

void App_Setup(void) {
    MyStep.begin();
    // Driver Enable có thể gọi ở đây hoặc trong moveAsync tùy nhu cầu giữ torque
}

void App_Loop(void) {

    if (!MyStep.isBusy()) {
        static int state = 0;

        if (state == 0) {
            MyStep.setDirection(TMC2209::CW);
            // Non-blocking: Hàm này trả về ngay lập tức, motor tự chạy ngầm
            MyStep.moveAsync(1600, 2000);
            state = 1;
        }
        else if (state == 1) {
            HAL_Delay(500); // Chờ 0.5s sau khi dừng hẳn

            MyStep.setDirection(TMC2209::CCW);
            MyStep.moveAsync(1600, 1000); // Quay ngược chậm hơn
            state = 2;
        }
        else if (state == 2) {
             HAL_Delay(500);
             state = 0; // Lặp lại
        }
    }
}

// Liên kết ngắt
extern "C" void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim) {
    if (htim->Instance == TIM3) {
        MyStep.irqHandler();
    }
}
