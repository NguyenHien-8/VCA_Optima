# TNH Optima 1.1.0 — Run Commands

## Chạy source

Từ thư mục repository `VCA_Optima` với virtual environment đã kích hoạt:

```powershell
python .\Release_1.1.0\main.py
```

Hoặc chuyển vào đúng release trước khi chạy:

```powershell
Set-Location .\Release_1.1.0
python .\main.py
```

## Tạo virtual environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r .\Release_1.1.0\requirements.txt
```

```powershell
python -m PyInstaller --clean --noconfirm .\TNH_Optima.spec
```
