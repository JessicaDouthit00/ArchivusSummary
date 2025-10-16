import cv2
import json

# Path to blank form (user changes this)
img_path = "blank_form.png"
output_json = "template.json"

fields = []
current_points = []

def draw_box(event, x, y, flags, param):
    global current_points
    if event == cv2.EVENT_LBUTTONDOWN:
        current_points.append((x, y))
        if len(current_points) == 2:
            # Ask for field name in terminal
            field_name = input("Enter field name for this box: ")
            x1, y1 = current_points[0]
            x2, y2 = current_points[1]
            fields.append({
                "name": field_name,
                "coords": [min(x1,x2), min(y1,y2), max(x1,x2), max(y1,y2)]
            })
            print(f" Added {field_name} at {fields[-1]['coords']}")
            current_points = []

# Load blank form
img = cv2.imread(img_path)
cv2.namedWindow("Template Creator")
cv2.setMouseCallback("Template Creator", draw_box)

print(" Click top-left and bottom-right of each field")
print(" Press 's' to save and exit, 'q' to quit without saving")

while True:
    cv2.imshow("Template Creator", img)
    key = cv2.waitKey(1) & 0xFF
    if key == ord("s"):
        with open(output_json, "w") as f:
            json.dump(fields, f, indent=2)
        print(f" Template saved to {output_json}")
        break
    elif key == ord("q"):
        print("Quit without saving")
        break

cv2.destroyAllWindows()
