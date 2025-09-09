import cv2

# --- Read coordinates from file ---
coords = []
with open('coordinates.txt', 'r') as f:
    for line in f:
        # Ignore empty lines
        if line.strip():
            x_str, y_str = line.strip().split(',')
            coords.append((int(x_str), int(y_str)))

img = cv2.imread('test.jpg')  # Change as needed

font = cv2.FONT_HERSHEY_SIMPLEX
font_scale = 1
thickness = 2

blue_leeway = -30
red_leeway = 10

def cyclic_labels(n, cycle=8):
    return [(i % cycle) + 1 for i in range(n)]

labels = cyclic_labels(len(coords), 8)
labels_rev = list(reversed(labels))

for (x, y), blue_label, red_label in zip(coords, labels, labels_rev):
    # Blue label on the left
    cv2.putText(img, str(blue_label), (x + blue_leeway, y), font, font_scale, (255, 0, 0), thickness, cv2.LINE_AA)
    # Red label on the right
    cv2.putText(img, str(red_label), (x + red_leeway, y), font, font_scale, (0, 0, 255), thickness, cv2.LINE_AA)

# Optional: mark posts
# for (x, y) in coords:
#     cv2.circle(img, (x, y), 5, (0, 255, 0), -1)

cv2.imwrite('test_labeled.jpg', img)
cv2.imshow('Result', img)
print("Press any key to close the image window.")
cv2.waitKey(0)
cv2.destroyAllWindows()
