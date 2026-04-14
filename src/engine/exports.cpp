#include "../include/window_engine.h"
#include "../include/types.h"

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
    }
    
    __declspec(dllexport) void RenderFrame(Rect* rects, int count)
    {
        if (g_engine != nullptr) 
        {
            g_engine->render_raw(rects, count);
        }
    }

    __declspec(dllexport) void RenderLayer(int layerId, Rect* rects, int count)
    {
        if (g_engine != nullptr)
        {
            g_engine->render_layer(layerId, rects, count);
        }
    }

    __declspec(dllexport) void SetLayerConfig(int id, int z_order, bool visible)
    {
        if (g_engine != nullptr)
        {
            LayerConfig config = { id, z_order, visible };
            g_engine->set_layer_config(config);
        }
    }

    __declspec(dllexport) void SetTransparencyMode(bool enable, unsigned char r, unsigned char g, unsigned char b)
    {
        if (g_engine != nullptr)
        {
            g_engine->set_transparency(enable, r, g, b);
        }
    }

    __declspec(dllexport) void GrowPool(int additionalCount)
    {
        if (g_engine != nullptr)
        {
            g_engine->grow_pool(additionalCount);
        }
    }
    
    __declspec(dllexport) int PollEvents(MouseEvent* outEvents, int maxCount)
    {
        if (g_engine != nullptr)
        {
            return g_engine->poll_events(outEvents, maxCount);
        }
        return 0;
    }

    __declspec(dllexport) void CloseEngine()
    {
        if (g_engine != nullptr) 
        {
            delete g_engine;
            g_engine = nullptr;
        }
    }
}
