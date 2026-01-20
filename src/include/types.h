#ifndef TYPES_H
#define TYPES_H

#include <vector>


struct Rect
{
    int x, y, w, h;
    unsigned char r, g, b, a;
};


struct Frame
{
    int id;
    int rectCount;
    std::vector<Rect> rects;
};

#endif
