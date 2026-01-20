@echo off
g++ -shared -o bin/engine.dll src/engine/exports.cpp -I ./src/include -static-libgcc -static-libstdc++ -m64 -luser32 -lgdi32 
echo "dll build success"