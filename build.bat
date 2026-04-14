@echo off
if not exist bin mkdir bin
g++ -shared -o bin/engine.dll src/engine/exports.cpp src/engine/engine.cpp -I ./src/include -std=c++17 -static-libgcc -static-libstdc++ -m64 -luser32 -lgdi32 -D_WIN32_WINNT=0x0600
if %ERRORLEVEL% EQU 0 (
    echo "dll build success"
) else (
    echo "dll build failed"
)
