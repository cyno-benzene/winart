#ifndef TYPES_H
#define TYPES_H

#include <vector>


struct Rect
{
    int x, y, w, h;
    unsigned char r, g, b, a;
    int layer_id;
};


struct LayerConfig {
    int id;
    int z_order;
    bool visible;
};


struct Frame
{
    int id;
    int rectCount;
    std::vector<Rect> rects;
};

enum EventType {
    MOUSE_DOWN = 1,
    MOUSE_UP = 2,
    MOUSE_MOVE = 3,
    KEY_DOWN = 4,
    KEY_UP = 5
};

struct EngineEvent {
    int type;
    int x;
    int y;
    int button; // Mouse button OR key code
};

#endif
