#include <windows.h>
#include <vector>
#include <algorithm>
#include "csv_reader.h" 
#include "types.h"

class WindowEngine {
private:
    std::vector<HWND> windowPool;
    HINSTANCE hInst;
    const wchar_t* CLASS_NAME = L"PixelWindowClass";

    static LRESULT CALLBACK WindowProc(
        HWND hwnd, 
        UINT uMsg, 
        WPARAM wParam, 
        LPARAM lParam
    ) 
    {
        if (uMsg == WM_DESTROY) 
        { 
            PostQuitMessage(0); 
            return 0; 
        }

        if (uMsg == WM_ERASEBKGND)
        {
            HDC hdc = (HDC)wParam;
            RECT rc;
            GetClientRect(hwnd, &rc);
            COLORREF color = (COLORREF)GetWindowLongPtr(hwnd, GWLP_USERDATA);
            HBRUSH hBrush = CreateSolidBrush(color);
            FillRect(hdc, &rc, hBrush);
            DeleteObject(hBrush);
            return 1;
        }

        return DefWindowProc(hwnd, uMsg, wParam, lParam);
    }

public:
    WindowEngine() : hInst(GetModuleHandle(NULL)) {}

    void init(int poolSize) 
    {
        // define window type
        WNDCLASSW wc = { };
        wc.lpfnWndProc = WindowProc;
        wc.hInstance = hInst;
        wc.lpszClassName = CLASS_NAME;
        wc.hbrBackground = NULL; // We handle painting in WM_ERASEBKGND
        
        RegisterClassW(&wc);

        // spawn the hidden pool
        for (int i = 0; i < poolSize; i++) 
        {
            HWND h = CreateWindowExW(
                WS_EX_TOOLWINDOW | WS_EX_TOPMOST, 
                CLASS_NAME, L"", 
                WS_POPUP, 
                0, 0, 0, 0, NULL, NULL, hInst, NULL
            );
            windowPool.push_back(h);
        }
    }

    void render_raw(Rect* rects, int count) 
    {
        // 1. Begin a deferred window position cycle
        int actual_count = std::min(count, (int)windowPool.size());
        if (actual_count > 0) {
            HDWP hdwp = BeginDeferWindowPos(actual_count);

            for (int i = 0; i < actual_count; i++) {
                // Update color
                COLORREF newColor = RGB(rects[i].r, rects[i].g, rects[i].b);
                COLORREF oldColor = (COLORREF)GetWindowLongPtr(windowPool[i], GWLP_USERDATA);
                
                if (newColor != oldColor) {
                    SetWindowLongPtr(windowPool[i], GWLP_USERDATA, (LONG_PTR)newColor);
                    InvalidateRect(windowPool[i], NULL, TRUE);
                }

                // 2. Add each window move to the bundle
                hdwp = DeferWindowPos(hdwp, windowPool[i], HWND_TOPMOST,
                                    rects[i].x, rects[i].y, 
                                    rects[i].w, rects[i].h, 
                                    SWP_SHOWWINDOW | SWP_NOACTIVATE | SWP_NOZORDER);
            }

            // 3. Execute all moves at once
            EndDeferWindowPos(hdwp);
        }

        // Hide the rest if they were previously visible
        for (int i = actual_count; i < (int)windowPool.size(); i++) {
            // Optimization: Only hide if it might be visible
            if (IsWindowVisible(windowPool[i])) {
                ShowWindow(windowPool[i], SW_HIDE);
            }
        }
    }

    ~WindowEngine() 
    {
        for (HWND h : windowPool) DestroyWindow(h);
    }
};
