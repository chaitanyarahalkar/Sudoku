from __future__ import division
import numpy as np
from cv2 import *


def cmp_height(x, y):
    _, _, _, hx = boundingRect(x)
    _, _, _, hy = boundingRect(y)
    return hy - hx


def cmp_width(x, y):
    _, _, wx, _ = boundingRect(x)
    _, _, wy, _ = boundingRect(y)
    return wy - wx


def sort_rectangle_contour(a):
    """
    Given a list of four points that represent a quad, this function returns
    the list sorted from top to bottom, then left to right.
    """
    # sort by y
    a = a[np.argsort(a[:, 1])]
    # put in groups
    a = np.reshape(a, (2, 2, 2))
    # sort rows by x
    a = np.vstack([row[np.argsort(row[:, 0])] for row in a])
    # undo shape transformation
    a = np.reshape(a, (4, 1, 2))
    return a


def process(frame):

    #
    # preprocessing
    #
    gray = cvtColor(frame, COLOR_BGR2GRAY)
    binary = adaptiveThreshold(gray, 255,
                               ADAPTIVE_THRESH_GAUSSIAN_C,
                               THRESH_BINARY, 11, 2)
    blurred = medianBlur(binary, 3)
    inverse = bitwise_not(blurred)
    contours, _ = findContours(inverse, RETR_TREE,
                               CHAIN_APPROX_SIMPLE)

    #
    # try to find the sudoku
    #
    sudoku_area = 0
    sudoku_contour = None
    for cnt in contours:
        area = contourArea(cnt)
        x, y, w, h = boundingRect(cnt)
        if (0.7 < w / h < 1.3            # aspect ratio
                and area > 150 * 150     # minimal area
                and area > sudoku_area   # biggest area on screen
                and area > .5 * w * h):  # fills bounding rect
            sudoku_area = area
            sudoku_contour = cnt

    #
    # separate sudoku from background
    #
    if sudoku_contour is not None:

        # first we make sure the found contour can be approximated by a quad
        perimeter = arcLength(sudoku_contour, True)
        approx = approxPolyDP(sudoku_contour, 0.1 * perimeter, True)

        if len(approx) == 4:
            # successfully approximated
            # we now transform the sudoku to a fixed size 450x450
            # plus 50 pixel border and remove the background
            mask = np.zeros(gray.shape, np.uint8)
            drawContours(mask, [sudoku_contour], 0, 255, -1)
            mask_inv = bitwise_not(mask)
            separated = bitwise_or(mask_inv, blurred)
            imshow('separated', separated)

            square = np.float32([[50, 50], [500, 50], [50, 500], [500, 500]])
            approx = np.float32([i[0] for i in approx])  # conversion
            approx = sort_rectangle_contour(approx)

            m = getPerspectiveTransform(approx, square)
            transformed = warpPerspective(separated, m, (550, 550))
            imshow('transformed', transformed)



    ## --------------------
    # sobel x-axis
    # sobel_x = Sobel(img, -1, 1, 0)
    # kernel_x = np.array([[1]] * 15, dtype='uint8')

    # closing x-axis
    # sobel_x = dilate(sobel_x, kernel_x)

    # generate mask for x
    # contours, hierarchy = findContours(
    #     sobel_x, RETR_TREE, CHAIN_APPROX_SIMPLE)
    # sorted_contours = sorted(contours, cmp=cmp_height)

    # fill biggest 10 on mask
    # mask_x = np.zeros(img.shape, np.uint8)
    # for c in sorted_contours[:10]:
    #     drawContours(mask_x, [c], 0, 255, -1)

    # sobel y-axis
    # sobel_y = Sobel(img, -1, 0, 1)
    # kernel_y = np.array([[[1]] * 15], dtype='uint8')

    # closing y-axis
    # sobel_y = dilate(sobel_y, kernel_y)

    # generate mask for x
    # contours, hierarchy = findContours(
    #     sobel_y, RETR_TREE, CHAIN_APPROX_SIMPLE)
    # sorted_contours = sorted(contours, cmp=cmp_width)

    # fill biggest 10 on mask
    # mask_y = np.zeros(img.shape, np.uint8)
    # for c in sorted_contours[:10]:
    #     drawContours(mask_y, [c], 0, 255, -1)

    # imshow('matrix', bitwise_and(mask_x, mask_y))

    drawContours(frame, [sudoku_contour], 0, 255)
    imshow('Input', frame)


def solve_sudoku_in_picture(filename):
    pic = imread(filename, CV_LOAD_IMAGE_GRAYSCALE)
    process(pic)
    waitKey(0)


def solve_sudoku_in_video():
    cap = VideoCapture(0)
    while(True):
        _, frame = cap.read()
        process(frame)
        if waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()


if __name__ == '__main__':
    # solve_sudoku_in_picture('pics/sudoku.jpg')
    solve_sudoku_in_video()
    destroyAllWindows()
