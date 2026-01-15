#ifndef CSV_READER_H
#define CSV_READER_H

#include <string>
#include <vector>
#include "types.h"

void read_coordinates_csv(
    std::vector<Frame>& input_vector, 
    std::string file_path
);

#endif
