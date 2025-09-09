import cv2

# Global list to store coordinates
coords = []

# Mouse callback function
def click_event(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print(f"Clicked at: ({x}, {y})")
        coords.append((x, y))
        # Optionally, draw a small circle at the clicked point
        cv2.circle(img, (x, y), 3, (0, 255, 0), -1)
        cv2.imshow("Image", img)

# Load image
img = cv2.imread('test.jpg')  # Change to your image path

cv2.imshow("Image", img)
cv2.setMouseCallback("Image", click_event)

print("Click on the image. Press 'q' to quit and save.")

while True:
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break

cv2.destroyAllWindows()

# Save coordinates to a file
with open("coordinates.txt", "w") as f:
    for pt in coords:
        f.write(f"{pt[0]}, {pt[1]}\n")

print("Coordinates saved to coordinates.txt")
