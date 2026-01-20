#include "window_engine.h"
#include "types.h"

// global pointer 
WindowEngine* g_engine = nullptr;

extern "C" 
{
    __declspec(dllexport) void InitEngine(int poolSize)
    {
        if (g_engine == nullptr) 
        {
            g_engine = new WindowEngine();
            g_engine->init(poolSize);
        }
    };
    
    __declspec(dllexport) void RenderFrame(Rect* rects, int count)
    {
        if (g_engine != nullptr) 
        {
            g_engine->render_raw(rects, count);
        }
    };
    
    __declspec(dllexport) void CloseEngine()
    {
        if (g_engine != nullptr) 
        {
            delete g_engine;
            g_engine = nullptr;
        }
    };
}