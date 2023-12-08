import cv2
import apriltag
import argparse
import math

# Goal - setup functions that will allow the robot to center itself between two april tags

cap = cv2.VideoCapture(0)


def normalize_coordinates(image, coordinates):
    height, width = image.shape[:2]
    image_center = [int(width/2), int(height/2)]
    # Subtract the center of frame from the input coordinates, making center of frame read [0, 0]
    coordinates[0] -= image_center[0]
    coordinates[1] -= image_center[1]
    return coordinates

def draw_apriltag(image, results):
    # Draw lines around the Apriltags
    for tag in results:
        corner = tag[7]
        image = cv2.line(image,
                        (int(corner[0][0]), int(corner[0][1])),
                        (int(corner[1][0]), int(corner[1][1])), 255, 2)
        image = cv2.line(image,
                        (int(corner[1][0]), int(corner[1][1])),
                        (int(corner[2][0]), int(corner[2][1])), 255, 2)
        image = cv2.line(image,
                        (int(corner[2][0]), int(corner[2][1])),
                        (int(corner[3][0]), int(corner[3][1])), 255, 2)
        image = cv2.line(image,
                        (int(corner[3][0]), int(corner[3][1])),
                        (int(corner[0][0]), int(corner[0][1])), 255, 2)
    return image

def calculate_april_angle(vector1, vector2, origin):
    # Calculate vectors relative to the origin
    vector1_relative = [vector1[0] - origin[0], vector1[1] - origin[1]]
    vector2_relative = [vector2[0] - origin[0], vector2[1] - origin[1]]

    # Calculate dot product
    dot_product = vector1_relative[0] * vector2_relative[0] + vector1_relative[1] * vector2_relative[1]

    # Calculate magnitudes
    magnitude1 = math.sqrt(vector1_relative[0]**2 + vector1_relative[1]**2)
    magnitude2 = math.sqrt(vector2_relative[0]**2 + vector2_relative[1]**2)

    # Calculate the angle in radians
    angle_radians = math.acos(dot_product / (magnitude1 * magnitude2))

    # Convert the angle to degrees
    angle_degrees = math.degrees(angle_radians)

    return angle_degrees

def draw_april_angle(image, results):
    for tag in results:
        corner = tag[7]
        angle = calculate_april_angle([corner[3][0], corner[3][1]], [corner[1][0], corner[1][1]], [corner[0][0], corner[0][1]])
        print(angle)
        angle = int(angle)
        image = cv2.putText(image, f"{angle}", (int(corner[0][0]), int(corner[0][1])), cv2.FONT_HERSHEY_SIMPLEX, 1, 255, 2)
    return image

def create_coord_pair(results):
    coordinate_list = []
    if len(results) < 2:
        print("Not enough April Tags!")
        return False
    for coord in results:
        coordinates = coord[6]
        coordinate_list.append(coordinates)
    coordinate_list = coordinate_list[:2]
    for coord in coordinate_list:
        coord = normalize_coordinates(image, coord)
    return coordinate_list

def movement_command(coord_pair, threshold):
    coord_sum = coord_pair[0][0]+coord_pair[1][0]
    if coord_sum < threshold and coord_sum > -threshold:
       print("You are now centered")
       return
    elif coord_sum > threshold:
        print("Turn left!")
        return
    elif coord_sum < -threshold:
        print("Turn right!")
        return


while True:
    ret, image = cap.read()
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    options = apriltag.DetectorOptions(families="tag36h11")
    detector = apriltag.Detector(options)
    results = detector.detect(image)

    # If an april tag is detected, print out its center coordinates
    if not results:
        cv2.imshow("output",image)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
        continue
    coordinate_list = create_coord_pair(results)
    if coordinate_list is not False:
       movement_command(coordinate_list, 50)
    image = draw_apriltag(image, results)
    image = draw_april_angle(image, results)
    cv2.imshow("output",image)
    if cv2.waitKey(1) & 0xFF == ord("q"):
            break