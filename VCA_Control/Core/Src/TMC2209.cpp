#include "TMC2209.hpp"

TMC2209::TMC2209(GPIO_TypeDef* enPort, uint16_t enPin,
                 GPIO_TypeDef* dirPort, uint16_t dirPin,
                 TIM_HandleTypeDef* htim, uint32_t timChannel)
    : _enPort(enPort), _enPin(enPin),
      _dirPort(dirPort), _dirPin(dirPin),
      _htim(htim), _timChannel(timChannel),
      _stepsRemaining(0)
{
}

void TMC2209::begin() {
    // Khởi tạo trạng thái ban đầu: Disable driver, Duty = 0
    disable();
    __HAL_TIM_SET_COMPARE(_htim, _timChannel, 0);
    // Bật PWM sẵn sàng, nhưng duty = 0 nên chưa có xung
    HAL_TIM_PWM_Start(_htim, _timChannel);
}

void TMC2209::setDirection(Direction dir) {
    if (dir == CW) {
        _dirPort->BSRR = _dirPin; // High
    } else {
        _dirPort->BSRR = (uint32_t)_dirPin << 16U; // Low
    }
}

void TMC2209::moveAsync(int32_t steps, uint32_t speedFreq) {
    if (steps <= 0) return;

    // 1. Kích hoạt Driver
    enable();

    // 2. Cài đặt số bước
    _stepsRemaining = steps;

    // 3. Tính toán Timer (Clock 16MHz -> PSC=15 -> 1MHz Timer)
    // Giới hạn tốc độ min/max để bảo vệ
    if (speedFreq < 10) speedFreq = 10;
    if (speedFreq > 50000) speedFreq = 50000; // Max 50kHz cho an toàn

    uint32_t period = (1000000UL / speedFreq) - 1;

    // Cập nhật thanh ghi trực tiếp (nhanh hơn gọi hàm HAL)
    __HAL_TIM_SET_AUTORELOAD(_htim, period);
    __HAL_TIM_SET_COMPARE(_htim, _timChannel, period >> 1); // Duty 50% (chia 2)
    __HAL_TIM_SET_COUNTER(_htim, 0);

    // 4. Xóa cờ ngắt cũ và bật ngắt Update
    __HAL_TIM_CLEAR_IT(_htim, TIM_IT_UPDATE);
    __HAL_TIM_ENABLE_IT(_htim, TIM_IT_UPDATE);
}

// Hàm ngắt: Được tối ưu để chạy cực nhanh
void TMC2209::irqHandler() {
    // Chỉ trừ bước nếu còn bước
    if (_stepsRemaining > 0) {
        _stepsRemaining--;

        // Nếu vừa chạm mốc 0, tắt xung ngay lập tức
        if (_stepsRemaining == 0) {
            // Set Duty = 0 (Chân STEP giữ mức thấp)
            __HAL_TIM_SET_COMPARE(_htim, _timChannel, 0);
            // Tắt ngắt để giảm tải CPU
            __HAL_TIM_DISABLE_IT(_htim, TIM_IT_UPDATE);
        }
    }
}
