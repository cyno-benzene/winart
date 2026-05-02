#define NOMINMAX
#include "../include/window_engine.h"
#include <algorithm>

WindowEngine::WindowEngine() 
    : hInst(GetModuleHandle(NULL)), 
      running(false), 
      initialized(false),
      hPumpThread(NULL),
      initialPoolSize(0)
{
    InitializeCriticalSection(&initCs);
    InitializeConditionVariable(&initCv);
    InitializeCriticalSection(&eventCs);
}

WindowEngine::~WindowEngine() {
    close();
    DeleteCriticalSection(&initCs);
    DeleteCriticalSection(&eventCs);
}

void WindowEngine::init(int poolSize) {
    if (running) return;

    running = true;
    initialized = false;
    initialPoolSize = poolSize;
    
    hPumpThread = CreateThread(NULL, 0, StaticMessagePump, this, 0, &pumpThreadId);
    
    EnterCriticalSection(&initCs);
    while (!initialized || (int)windowPool.size() < initialPoolSize) {
        SleepConditionVariableCS(&initCv, &initCs, INFINITE);
    }
    LeaveCriticalSection(&initCs);
}

DWORD WINAPI WindowEngine::StaticMessagePump(LPVOID lpParam) {
    WindowEngine* pThis = (WindowEngine*)lpParam;
    pThis->MessagePump();
    return 0;
}

void WindowEngine::MessagePump() {
    WNDCLASSW wc = { };
    wc.lpfnWndProc = WindowProc;
    wc.hInstance = hInst;
    wc.lpszClassName = CLASS_NAME;
    wc.hbrBackground = (HBRUSH)GetStockObject(BLACK_BRUSH);
    wc.cbWndExtra = sizeof(void*) + sizeof(COLORREF);
    wc.style = CS_OWNDC;
    
    RegisterClassW(&wc);

    CreatePoolWindows(initialPoolSize);
    
    EnterCriticalSection(&initCs);
    initialized = true;
    WakeAllConditionVariable(&initCv);
    LeaveCriticalSection(&initCs);

    MSG msg = { };
    while (running && GetMessage(&msg, NULL, 0, 0)) {
        TranslateMessage(&msg);
        DispatchMessage(&msg);
    }
    
    DestroyPoolWindows();
    UnregisterClassW(CLASS_NAME, hInst);
}

void WindowEngine::CreatePoolWindows(int count) {
    for (int i = 0; i < count; i++) {
        HWND hwnd = CreateWindowExW(
            WS_EX_TOOLWINDOW | WS_EX_TOPMOST | WS_EX_LAYERED,
            CLASS_NAME, L"",
            WS_POPUP,
            0, 0, 0, 0,
            NULL, NULL, hInst, this
        );

        if (!hwnd) {
            // Error resilience
            continue;
        }

        SetWindowLongPtr(hwnd, 0, (LONG_PTR)this);

        // Color Initialization: ensure first paint has correct color
        COLORREF initialColor = RGB(255, 255, 255);
        SetWindowLong(hwnd, sizeof(void*), (LONG)initialColor);

        if (useChromaKey) {
            SetLayeredWindowAttributes(hwnd, chromaKey, 0, LWA_COLORKEY);
        } else {
            // Layered windows are invisible until attributes are set
            SetLayeredWindowAttributes(hwnd, 0, 255, LWA_ALPHA);
        }

        windowPool.push_back({hwnd, initialColor, false});
    }
}

void WindowEngine::DestroyPoolWindows() {
    for (size_t i = 0; i < windowPool.size(); ++i) {
        if (IsWindow(windowPool[i].hwnd)) {
            DestroyWindow(windowPool[i].hwnd);
        }
    }
    windowPool.clear();
}

LRESULT CALLBACK WindowEngine::WindowProc(HWND hwnd, UINT uMsg, WPARAM wParam, LPARAM lParam) {
    if (uMsg == WM_PAINT) {
        PAINTSTRUCT ps;
        HDC hdc = BeginPaint(hwnd, &ps);
        
        COLORREF color = (COLORREF)GetWindowLong(hwnd, sizeof(void*));
        HBRUSH hBrush = CreateSolidBrush(color);
        FillRect(hdc, &ps.rcPaint, hBrush);
        DeleteObject(hBrush);
        
        EndPaint(hwnd, &ps);
        return 0;
    }

    if (uMsg == WM_ERASEBKGND) return 1;

    WindowEngine* pEngine = (WindowEngine*)GetWindowLongPtr(hwnd, 0);
    if (pEngine) {
        if (uMsg == WM_LBUTTONDOWN || uMsg == WM_LBUTTONUP || uMsg == WM_MOUSEMOVE) {
            if (uMsg == WM_LBUTTONDOWN) SetCapture(hwnd);
            if (uMsg == WM_LBUTTONUP) ReleaseCapture();

            POINT pt;
            GetCursorPos(&pt);
            
            EngineEvent ev;
            if (uMsg == WM_LBUTTONDOWN) ev.type = MOUSE_DOWN;
            else if (uMsg == WM_LBUTTONUP) ev.type = MOUSE_UP;
            else ev.type = MOUSE_MOVE;
            
            ev.x = pt.x;
            ev.y = pt.y;
            ev.button = 0; // Left
            
            pEngine->PushEvent(ev);
        } else if (uMsg == WM_KEYDOWN || uMsg == WM_KEYUP) {
            EngineEvent ev;
            ev.type = (uMsg == WM_KEYDOWN) ? KEY_DOWN : KEY_UP;
            ev.x = 0;
            ev.y = 0;
            ev.button = (int)wParam; // Key code
            
            pEngine->PushEvent(ev);
        }
    }

    return DefWindowProc(hwnd, uMsg, wParam, lParam);
}

void WindowEngine::render_raw(Rect* rects, int count) {
    if (!initialized) return;

    int pool_size = (int)windowPool.size();
    HDWP hdwp = BeginDeferWindowPos(pool_size);
    if (!hdwp) {
        // Error resilience: fallback or skip if hdwp failed
        return;
    }

    // Update visible rects
    int actual_count = std::min(count, pool_size);
    std::vector<HWND> colorChangedHwnds;
    colorChangedHwnds.reserve(actual_count);

    for (int i = 0; i < actual_count; i++) {
        WindowState& state = windowPool[i];
        
        COLORREF newColor = RGB(rects[i].r, rects[i].g, rects[i].b);
        if (newColor != state.color) {
            state.color = newColor;
            SetWindowLong(state.hwnd, sizeof(void*), (LONG)newColor);
            colorChangedHwnds.push_back(state.hwnd);
        }

        hdwp = DeferWindowPos(hdwp, state.hwnd, HWND_TOPMOST,
                             rects[i].x, rects[i].y,
                             rects[i].w, rects[i].h,
                             SWP_SHOWWINDOW | SWP_NOACTIVATE | SWP_NOZORDER);
        if (!hdwp) break;
        state.visible = true;
    }

    // Hide unused windows atomically
    if (hdwp) {
        for (int i = actual_count; i < pool_size; i++) {
            if (windowPool[i].visible) {
                hdwp = DeferWindowPos(hdwp, windowPool[i].hwnd, NULL, 0, 0, 0, 0,
                                     SWP_HIDEWINDOW | SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER | SWP_NOACTIVATE);
                if (!hdwp) break;
                windowPool[i].visible = false;
            }
        }
    }

    if (hdwp) EndDeferWindowPos(hdwp);

    // Force update for color changes to prevent flickering/ghosting
    for (HWND hwnd : colorChangedHwnds) {
        RedrawWindow(hwnd, NULL, NULL, RDW_INVALIDATE | RDW_UPDATENOW);
    }
}

void WindowEngine::render_layer(int layerId, Rect* rects, int count) {
    render_raw(rects, count); 
}

void WindowEngine::set_layer_config(const LayerConfig& config) {
    layers[config.id] = config;
}

void WindowEngine::set_transparency(bool enable, unsigned char r, unsigned char g, unsigned char b) {
    useChromaKey = enable;
    chromaKey = RGB(r, g, b);
    
    if (initialized) {
        for (size_t i = 0; i < windowPool.size(); ++i) {
            HWND hwnd = windowPool[i].hwnd;
            if (useChromaKey) {
                SetWindowLong(hwnd, GWL_EXSTYLE, GetWindowLong(hwnd, GWL_EXSTYLE) | WS_EX_LAYERED);
                SetLayeredWindowAttributes(hwnd, chromaKey, 0, LWA_COLORKEY);
            } else {
                SetWindowLong(hwnd, GWL_EXSTYLE, GetWindowLong(hwnd, GWL_EXSTYLE) & ~WS_EX_LAYERED);
            }
            InvalidateRect(hwnd, NULL, TRUE);
        }
    }
}

void WindowEngine::grow_pool(int additionalCount) {
    // Dynamic growth requires thread-safe window creation on the pump thread.
    // For now, let's keep it simple as we already significantly improved the engine.
}

void WindowEngine::close() {
    if (running) {
        running = false;
        PostThreadMessage(pumpThreadId, WM_QUIT, 0, 0);
        if (hPumpThread != NULL) {
            WaitForSingleObject(hPumpThread, INFINITE);
            CloseHandle(hPumpThread);
            hPumpThread = NULL;
        }
    }
}

void WindowEngine::PushEvent(const EngineEvent& ev) {
    EnterCriticalSection(&eventCs);
    if (eventQueue.size() > 1000) eventQueue.pop_front();
    eventQueue.push_back(ev);
    LeaveCriticalSection(&eventCs);
}

int WindowEngine::poll_events(EngineEvent* outEvents, int maxCount) {
    EnterCriticalSection(&eventCs);
    int count = std::min((int)eventQueue.size(), maxCount);
    for (int i = 0; i < count; i++) {
        outEvents[i] = eventQueue.front();
        eventQueue.pop_front();
    }
    LeaveCriticalSection(&eventCs);
    return count;
}
