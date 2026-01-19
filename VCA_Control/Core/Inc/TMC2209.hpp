#ifndef TMC2209_HPP_
#define TMC2209_HPP_

#include "main.h"

class TMC2209 {
public:
    enum Direction { CW = 0, CCW = 1 };

    TMC2209(GPIO_TypeDef* enPort, uint16_t enPin,
            GPIO_TypeDef* dirPort, uint16_t dirPin,
            TIM_HandleTypeDef* htim, uint32_t timChannel);

    void begin();

    // Inline để tăng tốc độ thực thi, giảm gọi hàm
    inline void enable()  { _enPort->BSRR = (uint32_t)_enPin << 16U; } // Reset Pin (Low)
    inline void disable() { _enPort->BSRR = _enPin; }                // Set Pin (High)

    void setDirection(Direction dir);
    void moveAsync(int32_t steps, uint32_t speedFreq);

    // Kiểm tra nhanh
    inline bool isBusy() const { return _stepsRemaining > 0; }

    // Xử lý ngắt (cần tối ưu tốc độ tối đa)
    void irqHandler();

private:
    GPIO_TypeDef* _enPort; uint16_t _enPin;
    GPIO_TypeDef* _dirPort; uint16_t _dirPin;
    TIM_HandleTypeDef* _htim;
    uint32_t _timChannel;

    volatile int32_t _stepsRemaining;
};

#endif
