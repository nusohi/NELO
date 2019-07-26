# Windows应用位置重置

> 部分软件放在另一个屏幕后，在不连其他显示器的情况下，无法自动重置位置，导致找不到这个应用界面。

借助 Python 的 `pywin32` 库来查找和调整应用的位置。

```python
import win32gui
import win32con


def ResetWnd(title):
    hWndList = []  
    win32gui.EnumWindows(lambda hWnd, param: param.append(hWnd), hWndList)

    for hwnd in hWndList:
        classname = win32gui.GetClassName(hwnd)
        titlename = win32gui.GetWindowText(hwnd)
        if (titlename.find(title) >= 0):
            rect = win32gui.GetWindowRect(hwnd)
            win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0,0,500,500, win32con.SWP_SHOWWINDOW)


if __name__== '__main__':
    titlename = "Ant Renamer 2.12"
    ResetWnd(titlename)
```

