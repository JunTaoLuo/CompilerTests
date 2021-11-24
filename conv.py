from PIL import Image, ImageEnhance
import math
import numpy as np

def write_2d_array(array, file, array_name):
    n = len(array)
    f = open(file, "w")
    f.write(f'int {array_name}_size = {n};\n')
    f.write(f'int[][] {array_name} = alloc_array(int[],{array_name}_size);\n')
    for i in range(n):
        f.write(f'{array_name}[{i}] = alloc_array(int,{array_name}_size);\n')
        for j in range(n):
            f.write(f'{array_name}[{i}][{j}] = {array[i][j]};\n')
    f.close()

if __name__ == "__main__":
    filter_size = 8
    filter_index = [[0 for c in range(filter_size)] for r in range(filter_size)]
    for i in range(filter_size):
        for j in range(filter_size):
            filter_x = i-filter_size/2 if i >= filter_size/2 else filter_size/2-i-1
            filter_y = j-filter_size/2 if j >= filter_size/2 else filter_size/2-j-1
            filter_index[i][j] = filter_x + filter_y

    filter_dist = [[0 for c in range(filter_size)] for r in range(filter_size)]
    for i in range(filter_size):
        for j in range(filter_size):
            filter_dist[i][j] = filter_index[i][j]**2

    sigma = 6
    filter = [[0 for c in range(filter_size)] for r in range(filter_size)]
    scale = 0
    for i in range(filter_size):
        for j in range(filter_size):
            filter[i][j] = int(math.exp(-filter_dist[i][j]/sigma**2)*32)
            scale += filter[i][j]
    print(f'scale = {scale}')

    write_2d_array(filter, './filter.c', 'filter')

    img_size = 40
    img = Image.open('./cat.jpeg').convert('L').resize((img_size, img_size))
    enhancer = ImageEnhance.Contrast(img)
    new_img = enhancer.enhance(2)
    new_img.save('./gray_cat.jpg')

    img_pix = np.asarray(new_img)
    write_2d_array(img_pix, './image.c', 'image')

    convolution = np.ndarray((img_size-filter_size, img_size-filter_size), dtype=np.uint8)
    for i in range(img_size-filter_size):
        for j in range(img_size-filter_size):
            sum = 0
            for x in range(filter_size):
                for y in range(filter_size):
                    sum += img_pix[i+x][j+y]*filter[x][y]
            convolution[i][j] = int(sum/scale)
    write_2d_array(convolution, './convolution.c', 'convolution')

    blur = Image.fromarray(convolution, 'L')
    img.save('./blur_cat.jpg')

