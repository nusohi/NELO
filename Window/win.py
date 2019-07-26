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