#include <iostream>
#include "csv_reader.h"
#include "window_engine.h"
#include "types.h"

int main() 
{
    std::cout << "Loading coordinates..." << std::endl;
    std::vector<Frame> allFrames;

    read_coordinates_csv(allFrames, "frame.csv");

    if (allFrames.empty()) {
        std::cout << "No data found!" << std::endl;
        return 1;
    }

    std::cout << "Initializing Engine..." << std::endl;
    WindowEngine engine;

    engine.init(500); // Create a pool of 500 potential windows

    std::cout << "Playing! Press ESC to stop." << std::endl;
    engine.run_animation(allFrames);

    return 0;
}

// g++ main.cpp lib/csv_reader.cpp -I ./include -o generator.exe -luser32 -lgdi32 -unicode