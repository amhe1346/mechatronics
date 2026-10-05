import cv2
import numpy as np
import color_change

# sudo apt update
#sudo apt install python3-opencv python3-numpy
#cd /path/to/the/script
#python3 color_rec_video.py

# Add your video path here
# this might need to be updated
from picamera2 import Picamera2

picam2 = Picamera2()
picam2.configure(
    picam2.create_preview_configuration(
        main={"size": (640, 480), "format": "RGB888"}
    )
)
picam2.start()



while True:

    img = picam2.capture_array()

   

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Red range 1
    lower_red1 = np.array([0, 40, 40])
    upper_red1 = np.array([10, 255, 255])

    red_mask1 = cv2.inRange(hsv, lower_red1, upper_red1)

    # Red range 2
    lower_red2 = np.array([170, 40, 40])
    upper_red2 = np.array([179, 255, 255])

    red_mask2 = cv2.inRange(hsv, lower_red2, upper_red2)

    red_mask = cv2.bitwise_or(red_mask1, red_mask2)


    lower_green = np.array([35, 50, 50])
    upper_green = np.array([85, 255, 255])

    green_mask = cv2.inRange(hsv, lower_green, upper_green)


    lower_blue = np.array([90, 50, 50])
    upper_blue = np.array([130, 255, 255])

    blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)


    lower_yellow = np.array([18, 60, 40])
    upper_yellow = np.array([40, 255, 255])

    yellow_mask = cv2.inRange(hsv, lower_yellow, upper_yellow)


    color_boxes = {
        "Red": (0, 0, 255),
        "Green": (0, 255, 0),
        "Blue": (255, 0, 0),
        "Yellow": (0, 255, 255)
    }

    def detect_color(mask, color_name, image):

        box_color = color_boxes[color_name]

        contours, _ = cv2.findContours(
            mask,
            cv2.RETR_TREE,
            cv2.CHAIN_APPROX_SIMPLE
        )

        largest_contour = max(contours, key=cv2.contourArea, default=None)
        if largest_contour is None:
            return 0

        largest_area = cv2.contourArea(largest_contour)
        if largest_area <= 300:
            return largest_area

        x, y, w, h = cv2.boundingRect(largest_contour)
        cv2.rectangle(image, (x, y), (x + w, y + h), box_color, 2)

        (text_width, text_height), _ = cv2.getTextSize(
            color_name,
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            2
        )

        text_y = y + text_height + 5
        cv2.rectangle(
            image,
            (x, y),
            (x + text_width + 8, y + text_height + 10),
            box_color,
            -1
        )
        cv2.putText(
            image,
            color_name,
            (x + 2, text_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 0, 0),
            2
        )

        return largest_area
                    
    red_area = detect_color(red_mask, "Red", img)
    detect_color(green_mask, "Green", img)
    blue_area = detect_color(blue_mask, "Blue", img)
    yellow_area = detect_color(yellow_mask, "Yellow", img)

    color, area = max(
        (("Red", red_area), ("Blue", blue_area), ("Yellow", yellow_area)),
        key=lambda detection: detection[1]
    )

    if area <= 300:
        color_change.turnOff()
    elif color == "Red":
        color_change.red()
    elif color == "Blue":
        color_change.blue()
    else:
        color_change.yellow()



    cv2.imshow("Color Recognition", img)

    cv2.imshow("Color Recognition Video", img)

    if cv2.waitKey(25) & 0xFF == ord('q'):
        break

picam2.stop()
cv2.destroyAllWindows()