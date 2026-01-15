import math

def generate_test_csv(filename="frame.csv", num_frames=100, num_rects=10):
    with open(filename, "w") as f:
        for frame_id in range(1, num_frames + 1):
            rects = []
            for i in range(num_rects):
                # Calculate wave pattern
                x = 100 + (i * 80)
                # Offset the sine wave based on frame_id to animate it
                y = 300 + int(math.sin((frame_id / 10.0) + (i * 0.5)) * 100)
                w = 50
                h = 50
                rects.extend([x, y, w, h])
            
            # Format: ID, Count, x1, y1, w1, h1, ...
            line = f"{frame_id},{num_rects}," + ",".join(map(str, rects))
            f.write(line + "\n")

if __name__ == "__main__":
    generate_test_csv()
    print("frame.csv generated")