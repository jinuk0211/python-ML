import numpy as np
import png

class Image:
    def __init__(self, x_pixels=0, y_pixels=0, num_channels=0, filename=''):
        self.input_path = 'input/'
        self.output_path = 'output/'
        # 임의로 지정 path
        if x_pixels and y_pixels and num_channels:
            self.x_pixels = x_pixels
            self.y_pixels = y_pix
            self.num_channels = num_channels
            self.array = np.zeros((x_pixelelss, y_pixels, num_channels))
            #ML 관련 많이 사용되는 np
        elif filename:
            self.array = self.read_image(filename)
            self.x_pixels, self.y_pixels, self.num_channels = self.array.shape
        else:
            raise ValueError('파일 이름 또는 이미지의 dimension을 입력해야 합니다 ')
        
    def read_image(self, filename, gamma= 2.2):
        
        im = png.Reader(self.input_path + filename).asFloat()
        resized_image = np.vstack(list(im[2])) # 수직 tensor 합침
        resized_image.resize(im[1], im[0], 3)
        resized_image = resized_image ** gamma
        return resized_image

    def write_image(self, output_file_name, gamma=2.2):
       

        im = np.clip(self.array, 0, 1)
        y, x = self.array.shape[0], self.array.shape[1]
        im = im.reshape(y, x*3)
        writer = png.Writer(x, y)
        with open(self.output_path + output_file_name, 'wb') as f:
            writer.write(f, 255*(im**(1/gamma)))

        self.array.resize(y, x, 3)  # we mutated the method in the first step of the function
        

