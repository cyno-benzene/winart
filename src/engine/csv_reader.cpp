#include "csv_reader.h"

#include <fstream>
#include <sstream>
#include <iostream>
#include "types.h"

// Frame1, num_rects, x1, y1, w1, h1, x2, y2, w2, h2
void read_coordinates_csv(
    std::vector<Frame>& input_vector,
    std::string file_path
) 
{
    std::ifstream fin(file_path);
    std::string line; 

    if (!fin.is_open())
    {
        std::cout << "Failed to open\n";
        return;
    }
    
    
    while (std::getline(fin, line)) 
    {
        std::stringstream sss(line);
        std::string word;
        
        Frame f;
        std::getline(sss, word, ','); f.id = std::stoi(word);
        std::getline(sss, word, ','); f.rectCount = std::stoi(word);

        // Read the coordinates into Rect structs
        for (int i = 0; i < f.rectCount; i++) 
        {
            Rect r;
            std::getline(sss, word, ','); r.x = std::stoi(word);
            std::getline(sss, word, ','); r.y = std::stoi(word);
            std::getline(sss, word, ','); r.w = std::stoi(word);
            std::getline(sss, word, ','); r.h = std::stoi(word);
            f.rects.push_back(r);
        }
        input_vector.push_back(f);
    }

    fin.close();
}

