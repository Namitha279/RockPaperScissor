import random
import cv2
import cvzone
from cvzone.HandTrackingModule import HandDetector
import time

# Initialize the webcam
cap = cv2.VideoCapture(0)
cap.set(3, 640)  # Set the width
cap.set(4, 480)  # Set the height

# Initialize hand detector
detector = HandDetector(maxHands=1)

# Initialize game variables
timer = 0
stateResult = False
startGame = False
scores = [0, 0]  # [AI, Player]
imgAI = None  # Initialize imgAI to None

# Define the winning score
winning_score = 2

# Load the blast image
blast_image = cv2.imread("C:/Users/blnam/PycharmProjects/OpencvPython/RockpaperScissor/Resources/pblast.png", cv2.IMREAD_UNCHANGED)
if blast_image is None:
    print("Error: Could not load blast_image.")
else:
    print("blast_image shape:", blast_image.shape)

# Define button properties
button_position = (500, 450)
button_size = (200, 50)
button_color = (0, 255, 0)
button_text = "Restart"

def draw_button(img, position, size, color, text):
    x, y = position
    w, h = size
    cv2.rectangle(img, position, (x + w, y + h), color, cv2.FILLED)
    cv2.putText(img, text, (x + 10, y + 35), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 3)

def is_inside_button(position, size, point):
    x, y = position
    w, h = size
    px, py = point
    return x <= px <= x + w and y <= py <= y + h

def resize_image_to_fit(img, max_width, max_height):
    height, width = img.shape[:2]
    aspect_ratio = width / height

    if width > max_width or height > max_height:
        if width > height:
            new_width = max_width
            new_height = int(new_width / aspect_ratio)
        else:
            new_height = max_height
            new_width = int(new_height * aspect_ratio)

        resized_img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)
        return resized_img
    return img

# Main loop
while True:
    imgBG = cv2.imread("C:/Users/blnam/PycharmProjects/OpencvPython/RockpaperScissor/Resources/BG.png")
    success, img = cap.read()

    if not success:
        print("Failed to capture image from webcam. Exiting...")
        break

    imgScaled = cv2.resize(img, (0, 0), None, 0.875, 0.875)
    imgScaled = imgScaled[:, 80:480]

    # Find Hands
    hands, img = detector.findHands(imgScaled)  # with draw

    if startGame:
        if stateResult is False:
            timer = time.time() - initialTime
            cv2.putText(imgBG, str(int(timer)), (605, 435), cv2.FONT_HERSHEY_PLAIN, 6, (255, 0, 255), 4)

            if timer > 3:
                stateResult = True
                timer = 0

                if hands:
                    playerMove = None
                    hand = hands[0]
                    fingers = detector.fingersUp(hand)
                    if fingers == [0, 0, 0, 0, 0]:
                        playerMove = 1  # Rock
                    elif fingers == [1, 1, 1, 1, 1]:
                        playerMove = 2  # Paper
                    elif fingers == [0, 1, 1, 0, 0]:
                        playerMove = 3  # Scissors

                    randomNumber = random.randint(1, 3)
                    imgAI = cv2.imread(f'C:/Users/blnam/PycharmProjects/OpencvPython/RockpaperScissor/Resources/{randomNumber}.png', cv2.IMREAD_UNCHANGED)

                    # Determine the winner
                    if (playerMove == 1 and randomNumber == 3) or \
                       (playerMove == 2 and randomNumber == 1) or \
                       (playerMove == 3 and randomNumber == 2):
                        scores[1] += 1  # Player wins
                    elif (playerMove == 3 and randomNumber == 1) or \
                         (playerMove == 1 and randomNumber == 2) or \
                         (playerMove == 2 and randomNumber == 3):
                        scores[0] += 1  # AI wins
                else:
                    imgAI = None

    imgBG[234:654, 795:1195] = imgScaled
    if stateResult and imgAI is not None:
        imgBG = cvzone.overlayPNG(imgBG, imgAI, (149, 310))

    cv2.putText(imgBG, str(scores[0]), (410, 215), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 6)
    cv2.putText(imgBG, str(scores[1]), (1112, 215), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 6)

    def overlay_blast_image(img):
        if blast_image is not None:
            resized_blast_image = resize_image_to_fit(blast_image, img.shape[1], img.shape[0])
            blast_height, blast_width = resized_blast_image.shape[:2]
            x_pos = random.randint(0, img.shape[1] - blast_width)
            y_pos = random.randint(0, img.shape[0] - blast_height)
            return cvzone.overlayPNG(img, resized_blast_image, (x_pos, y_pos))
        return img

    if scores[0] >= winning_score:
        cv2.putText(imgBG, "AI Wins!", (500, 350), cv2.FONT_HERSHEY_PLAIN, 7, (0, 0, 255), 10)
        imgBG = overlay_blast_image(imgBG)
        draw_button(imgBG, button_position, button_size, button_color, button_text)
        startGame = False

    if scores[1] >= winning_score:
        cv2.putText(imgBG, "Player Wins!", (500, 350), cv2.FONT_HERSHEY_PLAIN, 7, (0, 0, 255), 10)
        imgBG = overlay_blast_image(imgBG)
        draw_button(imgBG, button_position, button_size, button_color, button_text)
        startGame = False

    cv2.imshow("BG", imgBG)

    key = cv2.waitKey(1)
    if key == ord('s'):
        if scores[0] < winning_score and scores[1] < winning_score:
            startGame = True
            initialTime = time.time()
            stateResult = False
            imgAI = None  # Reset imgAI for the new game

    # Check for mouse click to restart the game
    def mouse_click(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            if is_inside_button(button_position, button_size, (x, y)):
                scores[0] = 0
                scores[1] = 0
                startGame = False

    cv2.setMouseCallback("BG", mouse_click)

# Release the webcam and close windows
cap.release()
cv2.destroyAllWindows()
