import numpy as np
from image import Image

def adjust_brightness(image, factor):
    x_pixels, y_pixels, num_channels = image.array.shape
    #원래 이미지 손상시키지않게 빈 이미지 하나 생성
    new_image = Image(x_pixels= x_pixels, y_pixels=y_pixels, num_channels=num_channels)
    for x in range(x_pixels):
        for y in range(y_pixels):
            for c in range(num_channels):
                new_image.array[x,y,c] = image.array[x,y,c] * factor

    return new_image

def adjust_contrast(image, factor, mid):
    x_pixels, y_pixels, num_channels = image.array.shape
    #원래 이미지 손상시키지않게 빈 이미지 하나 생성
    new_image = Image(x_pixels= x_pixels, y_pixels=y_pixels, num_channels=num_channels)
    
    for x in range(x_pixels):
        for y in range(y_pixels):
            for c in range(num_channels):
                new_image.array[x,y,c] = (image.array[x,y,c]-mid) * factor
    
    return new_image

def blur(image , kernal_size):
    #kernal 1픽셀 주변을 정해 흐릿하게 함 3kernal 은 1픽셀 좌우, 상하,또는 대각선 2픽셀 의미, 홀수여야한다
    x_pixels, y_pixels, num_channels = image.array.shape
    new_image = Image(x_pixels= x_pixels, y_pixels=y_pixels, num_channels=num_channels)

    neighbor_range = karnel_size // 2

    for x in range(x_pixels):
        for y in range(y_pixels):
            for c in range(num_channels):
            
    
                total = 0
                # 범위 체크 min max로 픽셀 정한뒤, +1은 파이썬이 마지막 범위는 읽지 않기 때문
                for x_i in range(max(0,x-neighbor_range),min((x_pixels-1),(x+neighbor_range))+1):
                    for y_i in range(max(0,y-neighbor_range),min((y_pixels-1),(y+neighbor_range))+1):                       
                        total += image.array[x_i,y_i,c]
                new_image.array[x,y,c] = total / (kernal_size)

    return new_image

def apply_kernel(image, kernel):
    pass

def combine_image(image1, image2):
    pass

