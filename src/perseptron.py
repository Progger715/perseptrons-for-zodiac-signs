import os
import random
from pathlib import Path
from PIL import Image

# Овен	Aries
# Телец	Taurus
# Близнецы	Gemini
# Рак	Cancer
# Лев	Leo
# Дева	Virgo
# Весы	Libra
# Скорпион	Scorpio
# Стрелец	Sagittarius
# Козерог	Capricorn
# Водолей	Aquarius
# Рыбы	Pisces
zodiac_signs = ["Aries", "Taurus", "Gemini",
                "Cancer", "Leo", "Virgo",
                "Libra", "Scorpio", "Sagittarius",
                "Capricorn", "Aquarius", "Pisces"]
image = ''
weights = []
w = 1
bias = 20


def init_weights():
    for z in range(12):
        weights.append([])
        for i in range(32):
            weights[z].append([])
            for j in range(32):
                weights[z][i].append(w)


def print_weights(number):
    for i in range(32):
        print(weights[number][i])


def open_image(name_image):
    try:
        path = Path(Path.cwd().parent, "picture", name_image)
        image = Image.open(path)
        return image
    except FileNotFoundError as ex:
        print("[FILE NOT FOUND]\t", ex)


def identify_image():
    width = image.size[0]
    height = image.size[1]
    pix = image.load()
    white_pixel = 255 * 3
    net = [0, 0, 0, 0, 0, 0]#, 0, 0, 0, 0, 0, 0]
    count = 0

    for x in range(width):
        for y in range(height):
            r = pix[x, y][0]
            g = pix[x, y][1]
            b = pix[x, y][2]
            color_pixel = (r + g + b)
            if color_pixel != white_pixel:
                count += 1
                s = 1
                # print(f"({x}, {y})\tr = {r}\tg = {g}\tb = {b}")
            else:
                s = 0
            for i in range(6):
                net[i] += s * weights[i][x][y]
    print("net = ", net)
    print("count = ", count)
    # print("choose_name_image = ", choose_name_image(net))
    return choose_name_image(net)


def choose_name_image(net):
    res = []
    for i in range(6):
        if net[i] >= bias:
            res.append([net[i], i])
    # print("res = ", res)
    if len(res) > 1:
        max = 0
        max_index = 0
        for i in range(len(res)):
            if res[i][0] > max:
                max = res[i][0]
                max_index = res[i][1]
        print("choose_name_image = ", zodiac_signs[max_index])
        return zodiac_signs[max_index]
    else:
        if len(res) > 0:
            print("choose_name_image = ", zodiac_signs[res[0][1]])
            return zodiac_signs[res[0][1]]
        else:
            print("choose_name_image = None")
            return None


def choose_name_image_bew(net):
    for i in range(6):
        if net[i] >= bias:
            return zodiac_signs[i]


def add_weight(number):
    pix = image.load()
    white_pixel = 255 * 3
    for x in range(image.size[0]):
        for y in range(image.size[1]):
            r = pix[x, y][0]
            g = pix[x, y][1]
            b = pix[x, y][2]
            color_pixel = (r + g + b)
            if color_pixel != white_pixel:
                weights[number][x][y] += 1


def reduce_weight(number):
    pix = image.load()
    white_pixel = 255 * 3
    for x in range(image.size[0]):
        for y in range(image.size[1]):
            r = pix[x, y][0]
            g = pix[x, y][1]
            b = pix[x, y][2]
            color_pixel = (r + g + b)
            if color_pixel != white_pixel:
                weights[number][x][y] -= 1


def train():
    path = Path(Path.cwd().parent, "picture")
    for _, _, files in os.walk(path):
        pass
    print(files, "\n")
    print("len(files)", len(files))

    for i in range(42):
        global image
        image = open_image(files[i])
        res = identify_image()
        try:
            if files[i].lower().startswith(res.lower()):
                print("\n[IN]\t", files[i].lower(), res.lower())
                number = zodiac_signs.index(res)
                print(number)
                add_weight(number)
                # print_weights(number)
            else:
                print("\n[OUT]\t", files[i].lower(), res.lower())
                number = zodiac_signs.index(res)
                print(number)
                reduce_weight(number)
                # print_weights(number)
        except Exception as ex:
            print("[TRAIN] net < bias\t", ex)


def train1():
    path = Path(Path.cwd().parent, "picture")
    for _, _, files in os.walk(path):
        pass
    print(files, "\n")
    print("len(files) =", len(files))

    for i in range(10000):
        global image
        number_file = random.randint(0, len(files)-1)
        image = open_image(files[number_file])
        res = identify_image()
        print("Image = ", files[number_file])
        if res is None:
            print(f"[None]")
            break
        # try:
        if files[number_file].lower().startswith(res.lower()):
            print(f"[TRUE]")
            number = zodiac_signs.index(res)
            print("number true image = ", number)
            add_weight(number)
            print()
            # print_weights(number)
        else:
            print("[FALSE]")
            number = zodiac_signs.index(res)
            print("number false image = ", number)
            reduce_weight(number)
            # print_weights(number)
            print()
        # except Exception as ex:
        #     print("[TRAIN] net < bias\t", ex)


init_weights()
# print("weight before training:")
# print_weights(1)
# image = open_image("gemini1.png")
# identify_image()
train1()

print("weight after training:")
print_weights(0)
