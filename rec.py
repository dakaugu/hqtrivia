import numpy as np
import cv2
from PIL import ImageGrab

bbox = (0, 550, 800, 1250)  # specific area in the screen

while True:
    img = ImageGrab.grab(bbox)
    img_np = np.array(img)

    frame = cv2.cvtColor(img_np, cv2.COLOR_BGR2RGB)

    cv2.imshow("Screen", frame)

    if cv2.waitKey(1) == 27:
        break

cv2.destroyAllWindows()
