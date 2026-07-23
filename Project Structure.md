# Project Structure
```
Ver1.1/                     
├── App/
│   ├── __init__.py
│   ├── Presentation/
│   │   ├── __init__.py 
│   │   ├── Views/
│   │   │   ├── __init__.py 
│   │   │   ├── Widgets/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── MenuBar/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── KeyboardShortcut.py
│   │   │   │   │   ├── MenuFile.py
│   │   │   │   │   ├── MenuSetup.py 
│   │   │   │   │   ├── MenuControl.py
│   │   │   │   │   ├── MenuTool.py
│   │   │   │   │   ├── MenuWindow.py
│   │   │   │   │   ├── MenuHelp.py
│   │   │   │   │   └── ToggleSideBar.py
│   │   │   │   ├── FileEditorWorkspace/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── FileEditor.py
│   │   │   │   │   ├── ImageEditor.py
│   │   │   │   │   ├── VideoEditor.py
│   │   │   │   │   ├── MotorControlEditor.py
│   │   │   │   │   └── MediaControlEditor.py
│   │   │   │   ├── EditorWorkspace.py
│   │   │   │   ├── DropletAnalysisWindow.py
│   │   │   │   ├── StatusBar.py
│   │   │   │   └── SideBar.py
│   │   │   ├── Dialog/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── ConfigCameraDialog.py
│   │   │   │   ├── ConfigHardwareDialog.py
│   │   │   │   ├── MotorControlDialog.py
│   │   │   │   ├── DeleteResourcesDialog.py
│   │   │   │   └── SaveResourcesDialog.py 
│   │   │   ├── MainView.py
│   │   │   └── MenuBar.py 
│   │   │   
│   │   ├── ViewModels/
│   │   │   ├── __init__.py
│   │   │   ├── DialogViewModel/
│   │   │   │   ├── __init__.
│   │   │   │   ├── ConfigCameraViewModel.py 
│   │   │   │   ├── ConfigHardwareViewModel.py
│   │   │   │   ├── MotorControlViewModel.py
│   │   │   │   ├── DeleteResourcesViewModel.py
│   │   │   │   └── SaveResourcesViewModel.py 
│   │   │   ├── FeatureViewModel/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── FileEditorViewModel.py
│   │   │   │   ├── DropletAnalysisViewModel.py
│   │   │   │   └── ImageEditorViewModel.py
│   │   │   ├── MainViewModel.py  
│   │   │   └── Workers.py
│   │
│   ├── Models/
│   │   ├── __init__.py 
│   │   ├── Controllers/
│   │   │    ├── __init__.py 
│   │   │    ├── HardwareManager.py
│   │   │    └── HardwareConnector.py
│   │   ├── Vision/
│   │   │    ├── __init__.py 
│   │   │    ├── CameraManager.py
│   │   │    ├── CameraFrameDispatcher.py
│   │   │    ├── HardwareCameraScan.py
│   │   │    └── CameraThread.py 
│   │   ├── MediaUtils/
│   │   │    ├── __init__.py 
│   │   │    ├── MediaManager.py
│   │   │    ├── ImageCaptureManager.py
│   │   │    └── VideoRecorderManager.py 
│   │   ├── Analysis/
│   │   │    ├── __init__.py 
│   │   │    ├── AnalysisManager.py
│   │   │    ├── BaselineAnalysis.py
│   │   │    └── DropletAnalysis.py 
│   │   ├── ProjectManager.py
│   │   ├── SessionManager.py
│   │   ├── CamHardwareManager.py
│   │   └── ControlPanelManager.py
│   │
│   ├── Infrastructure/
│   │   ├── __init__.py
│   │   ├── Helpers/
│   │   │    ├── __init__.py 
│   │   │    ├── ResourceHelper.py
│   │   ├── Repositories/
│   │   │    ├── __init__.py 
│   │   │    ├── ConfigRepository.py
│   │   │    └── SessionRepository.py
│   │   ├── Persistence/
│   │   │    ├── __init__.py 
│   │   │    ├── ConfigStorage.db
│   │   │    └── SessionData.db
│   │ 
│   ├── ReSource/
│   │   ├── __init__.py
│   │   ├── Styles/  
│   │   │    ├── __init__.py 
│   │   │    ├── MainViewStyles.qss
│   │   │    ├── EditorWorkspaceStyles.qss
│   │   │    ├── FileEditorStyles.qss
│   │   │    ├── ImageEditorStyles.qss
│   │   │    ├── VideoEditorStyles.qss
│   │   │    ├── DelSaveDialogStyles.qss
│   │   │    ├── MenuBarStyles.qss
│   │   │    ├── HardwareDialogStyles.qss
│   │   │    ├── MotorDialogStyles.qss
│   │   │    └── CameraDialogStyles.qss
│   │   ├── Icon/  
│   │   ├── Media/
│   │   │    ├── photo_camera.svg
│   │   │    ├── video_camera.svg
│   │   │    ├── open_image.svg
│   │   │    ├── open_video.svg
│   │   │    ├── play_video.svg
│   │   │    ├── pause_video.svg
│   │   │    ├── pausevideo.svg
│   │   │    ├── convert_camera.svg
│   │   │    ├── image.svg.svg
│   │   │    ├── analysis.svg
│   │   │    ├── skipforward.svg
│   │   │    ├── skipback.svg
│   │   │    └── stop_video.svg
│   │   ├── MenuFile/  
│   │   │    ├── save.svg
│   │   │    ├── delete.svg
│   │   │    ├── exit.svg
│   │   │    ├── new.svg
│   │   │    ├── open_item.svg
│   │   │    ├── open_project.svg
│   │   │    └── restart.svg
│   │   ├── DropletAnalysisWindow/
│   │   │    ├── actualsize.svg
│   │   │    ├── baseline.svg
│   │   │    ├── autodetectedge.svg
│   │   │    └── point.svg
│   │   ├── SideBar/  
│   │   │    ├── arrow_down.svg
│   │   │    ├── arrow_next.svg
│   │   │    ├── video_file.svg
│   │   │    ├── file_tnh.svg
│   │   │    └── image_file.svg
│   │   ├── app_icon.ico
│   │   └── splash_screen.png
│ 
├── venv/
├── .gitignore
├── __init__.py
├── main.py  
├── requirements.txt
├── LICENSE
├── TNH_Optima.spec
└── README.md 
```