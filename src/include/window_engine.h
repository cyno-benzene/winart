#ifndef WINDOW_ENGINE_H
#define WINDOW_ENGINE_H

#include <windows.h>
#include <vector>
#include <map>
#include <deque>
#include <atomic>
#include "types.h"

class WindowEngine {
private:
    struct WindowState {
        HWND hwnd;
        COLORREF color;
        bool visible;
    };

    std::vector<WindowState> windowPool;
    std::map<int, LayerConfig> layers;
    std::deque<MouseEvent> eventQueue;
    CRITICAL_SECTION eventCs;
    
    HINSTANCE hInst;
    const wchar_t* CLASS_NAME = L"PixelWindowClass";
    
    HANDLE hPumpThread;
    DWORD pumpThreadId;
    std::atomic<bool> running;
    std::atomic<bool> initialized;
    
    CRITICAL_SECTION initCs;
    CONDITION_VARIABLE initCv;

    COLORREF chromaKey = RGB(255, 0, 255); // Default magenta
    bool useChromaKey = false;
    int initialPoolSize = 0;

    static LRESULT CALLBACK WindowProc(HWND hwnd, UINT uMsg, WPARAM wParam, LPARAM lParam);
    static DWORD WINAPI StaticMessagePump(LPVOID lpParam);
    
    void MessagePump();
    void CreatePoolWindows(int count);
    void DestroyPoolWindows();
    void PushEvent(const MouseEvent& ev);

public:
    WindowEngine();
    ~WindowEngine();

    void init(int poolSize);
    void render_raw(Rect* rects, int count);
    void render_layer(int layerId, Rect* rects, int count);
    
    int poll_events(MouseEvent* outEvents, int maxCount);
    
    void set_layer_config(const LayerConfig& config);
    void set_transparency(bool enable, unsigned char r, unsigned char g, unsigned char b);
    void grow_pool(int additionalCount);
    void close();
};

#endif
