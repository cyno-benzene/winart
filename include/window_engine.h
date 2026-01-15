#include <windows.h>
#include <vector>
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

        if (uMsg == WM_PAINT) 
        {
            PAINTSTRUCT ps;
            HDC hdc = BeginPaint(hwnd, &ps);
            FillRect(hdc, &ps.rcPaint, (HBRUSH)GetStockObject(WHITE_BRUSH)); // Set pixel color
            EndPaint(hwnd, &ps);
            return 0;
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
        wc.hbrBackground = (HBRUSH)GetStockObject(WHITE_BRUSH); 
        
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

    void run_animation(const std::vector<Frame>& frames) 
    {
        for (const auto& frame : frames) 
        {
            //  killswitch
            if (GetAsyncKeyState(VK_ESCAPE)) break;

            // moving required windows
            for (int i = 0; i < frame.rectCount && i < windowPool.size(); i++) 
            {
                SetWindowPos(
                    windowPool[i], 
                    HWND_TOPMOST, 
                    
                    frame.rects[i].x, frame.rects[i].y, 
                    frame.rects[i].w, frame.rects[i].h, 

                    SWP_SHOWWINDOW | SWP_NOACTIVATE
                );
            }

            // rest remain hidden
            for (int i = frame.rectCount; i < windowPool.size(); i++) 
            {
                ShowWindow(windowPool[i], SW_HIDE);
            }

            Sleep(50); 
        }
    }

    ~WindowEngine() 
    {
        for (HWND h : windowPool) DestroyWindow(h);
    }
};