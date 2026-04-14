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
    MOUSE_MOVE = 3
};

struct MouseEvent {
    int type;
    int x;
    int y;
    int button; // 0 for left, 1 for right, etc.
};

#endif
