
MENU_BAR_STYLE = """
    /* --- THANH MENU CHÍNH (Top Bar) --- */
    QMenuBar {
        background-color: #F0F0F0; /* Màu nền xám trắng nhẹ */
        color: #000000;            /* Chữ màu đen */
        border-bottom: 1px solid #CCCCCC;
        padding: 2px;
    }
    
    QMenuBar::item {
        background-color: transparent;
        padding: 6px 10px;
        color: #000000;
        border-radius: 4px; /* Bo góc nhẹ khi hover */
    }

    /* Khi di chuột vào hoặc đã chọn */
    QMenuBar::item:selected {
        background-color: #E0E0E0; /* Xám đậm hơn chút */
        color: #000000;
    }

    /* Khi nhấn chuột xuống */
    QMenuBar::item:pressed {
        background-color: #D0D0D0;
    }
    
    /* --- MENU CON (Dropdown) --- */
    QMenu {
        background-color: #FFFFFF; /* Menu con nền trắng tinh */
        color: #000000;
        border: 1px solid #CCCCCC;
        padding: 4px;
        border-radius: 4px; /* Bo góc menu con */
    }

    QMenu::item {
        padding: 6px 25px 6px 30px; /* Padding rộng để chứa Icon */
        border-radius: 3px;
        margin: 1px 0px;
    }

    /* Hiệu ứng Hover vào mục con (Giống Windows 11/Office) */
    QMenu::item:selected {
        background-color: #CDE6F7; /* Màu xanh nhạt */
        color: #000000;
    }

    /* Icon bên trái */
    QMenu::icon {
        padding-left: 10px;
    }

    /* Đường kẻ phân cách */
    QMenu::separator {
        height: 1px;
        background: #E0E0E0;
        margin: 4px 10px;
    }
"""