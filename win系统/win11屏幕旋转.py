import ctypes
import ctypes.wintypes as wintypes
import tkinter as tk
from tkinter import messagebox
import sys

ENUM_CURRENT_SETTINGS = 0xFFFFFFFF
CDS_UPDATEREGISTRY     = 0x00000001
DISP_CHANGE_SUCCESSFUL = 0

DM_DISPLAYORIENTATION = 0x00000080
DM_PELSWIDTH           = 0x00080000
DM_PELSHEIGHT          = 0x00100000

class POINTL(ctypes.Structure):
    _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]

class DEVMODE(ctypes.Structure):
    _fields_ = [
        ("dmDeviceName",         ctypes.c_wchar * 32),
        ("dmSpecVersion",        wintypes.WORD),
        ("dmDriverVersion",      wintypes.WORD),
        ("dmSize",               wintypes.WORD),
        ("dmDriverExtra",        wintypes.WORD),
        ("dmFields",             wintypes.DWORD),
        ("dmPosition",           POINTL),
        ("dmDisplayOrientation", wintypes.DWORD),
        ("dmDisplayFixedOutput", wintypes.DWORD),
        ("dmColor",              wintypes.SHORT),
        ("dmDuplex",             wintypes.SHORT),
        ("dmYResolution",        wintypes.SHORT),
        ("dmTTOption",           wintypes.SHORT),
        ("dmCollate",            wintypes.SHORT),
        ("dmFormName",           ctypes.c_wchar * 32),
        ("dmLogPixels",          wintypes.WORD),
        ("dmBitsPerPel",         wintypes.DWORD),
        ("dmPelsWidth",          wintypes.DWORD),
        ("dmPelsHeight",         wintypes.DWORD),
        ("dmDisplayFlags",       wintypes.DWORD),
        ("dmDisplayFrequency",   wintypes.DWORD),
        ("dmICMMethod",          wintypes.DWORD),
        ("dmICMIntent",          wintypes.DWORD),
        ("dmMediaType",          wintypes.DWORD),
        ("dmDitherType",         wintypes.DWORD),
        ("dmReserved1",          wintypes.DWORD),
        ("dmReserved2",          wintypes.DWORD),
        ("dmPanningWidth",       wintypes.DWORD),
        ("dmPanningHeight",      wintypes.DWORD),
    ]

user32 = ctypes.windll.user32
user32.EnumDisplaySettingsExW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, ctypes.POINTER(DEVMODE), wintypes.DWORD]
user32.EnumDisplaySettingsExW.restype  = wintypes.BOOL
user32.ChangeDisplaySettingsExW.argtypes = [wintypes.LPCWSTR, ctypes.POINTER(DEVMODE), wintypes.HWND, wintypes.DWORD, wintypes.LPVOID]
user32.ChangeDisplaySettingsExW.restype  = wintypes.LONG

ORIENT_NAMES = {0: "0°  横屏", 1: "90°  竖屏", 2: "180°  横屏翻转", 3: "270°  竖屏"}
ORIENT_EMOJI = {0: "🎮", 1: "📖", 2: "🔄", 3: "📕"}

def get_current_orientation():
    dm = DEVMODE()
    dm.dmSize = ctypes.sizeof(DEVMODE)
    dm.dmDriverExtra = 0
    if not user32.EnumDisplaySettingsExW(None, ENUM_CURRENT_SETTINGS, ctypes.byref(dm), 0):
        return None
    return dm.dmDisplayOrientation

def set_orientation(new_orient):
    dm = DEVMODE()
    dm.dmSize = ctypes.sizeof(DEVMODE)
    dm.dmDriverExtra = 0
    if not user32.EnumDisplaySettingsExW(None, ENUM_CURRENT_SETTINGS, ctypes.byref(dm), 0):
        return False, "无法获取当前显示设置"
    cur = dm.dmDisplayOrientation
    if (cur in (0, 2)) != (new_orient in (0, 2)):
        dm.dmPelsWidth, dm.dmPelsHeight = dm.dmPelsHeight, dm.dmPelsWidth
    dm.dmDisplayOrientation = new_orient
    dm.dmFields = DM_DISPLAYORIENTATION | DM_PELSWIDTH | DM_PELSHEIGHT
    r = user32.ChangeDisplaySettingsExW(None, ctypes.byref(dm), None, CDS_UPDATEREGISTRY, None)
    if r == DISP_CHANGE_SUCCESSFUL:
        return True, "成功"
    return False, f"错误码 {r}"

class App:
    def __init__(self, root):
        self.root = root
        root.title("显示器朝向")
        root.geometry("360x280")
        root.resizable(False, False)
        root.attributes("-topmost", True)

        self.label = tk.Label(root, text="", font=("Microsoft YaHei", 13))
        self.label.pack(pady=12)

        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=5)

        self.buttons = {}
        for idx, orient in enumerate([0, 1, 2, 3]):
            text = f"{ORIENT_EMOJI[orient]}  {ORIENT_NAMES[orient]}"
            btn = tk.Button(
                btn_frame, text=text,
                font=("Microsoft YaHei", 12, "bold"),
                width=14, height=2,
                command=lambda o=orient: self.do_set(o)
            )
            btn.grid(row=idx // 2, column=idx % 2, padx=8, pady=6)
            self.buttons[orient] = btn

        self.update_label()

    def do_set(self, orient):
        ok, msg = set_orientation(orient)
        if not ok:
            messagebox.showerror("错误", f"切换失败: {msg}")
        self.update_label()

    def update_label(self):
        cur = get_current_orientation()
        if cur is None:
            self.label.config(text="⚠ 无法读取朝向")
            return
        self.label.config(text=f"当前: {ORIENT_EMOJI[cur]} {ORIENT_NAMES[cur]}")
        for o, btn in self.buttons.items():
            if o == cur:
                btn.config(bg="#4CAF50", fg="white", relief=tk.SUNKEN)
            else:
                btn.config(bg="SystemButtonFace", fg="black", relief=tk.RAISED)

if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
