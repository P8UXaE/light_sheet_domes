import numpy as np
import cv2
from scipy.ndimage import gaussian_filter
import skimage as sk
import copy
from scipy.spatial import Delaunay



class MyDelaunay(Delaunay):
    def __init__(self, points, delaunay_to_2D):
        super().__init__(points)
        self.delaunay_to_2D = delaunay_to_2D
        if delaunay_to_2D:
            self.simplices = self.convert_to_2D(self.simplices)
            
    def convert_to_2D(self, simplex):
        simplex_2D = []
        for i in simplex:
            simplex_2D.append([i[0], i[1], i[2]])
            simplex_2D.append([i[0], i[1], i[3]])
            simplex_2D.append([i[0], i[2], i[3]])
            simplex_2D.append([i[1], i[2], i[3]])
        return np.array(simplex_2D)

    def triangle_area(self, simplex): # At the moment only working in 2D triangles
        p1, p2, p3 = self.points[simplex]
        return 0.5 * np.abs(p1[0] * (p2[1] - p3[1]) + p2[0] * (p3[1] - p1[1]) + p3[0] * (p1[1] - p2[1]))

    def calculate_triangle_areas(self):
        return [self.triangle_area(simplex) for simplex in self.simplices]

    def largest_triangle_angle(self):
        largest_angles = []

        for simplex in self.simplices:
            p1, p2, p3 = self.points[simplex]

            # Calculate vectors
            v1 = p2 - p1
            v2 = p3 - p1
            v3 = p3 - p2

            # Calculate angles
            angle1 = np.arccos(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))
            angle2 = np.arccos(np.dot(-v1, v3) / (np.linalg.norm(v1) * np.linalg.norm(v3)))
            angle3 = np.pi - angle1 - angle2

            largest_angle = max(angle1, angle2, angle3)
            largest_angles.append(np.degrees(largest_angle))

        return largest_angles
    
    def largest_triangle_side(self):
        largest_sides = []
        
        for simplex in self.simplices:
            p1, p2, p3 = self.points[simplex]
            largest_side = max([np.sqrt((p1[0]-p1[1])**2+(p2[0]-p2[1])**2),
                                np.sqrt((p1[0]-p1[1])**2+(p3[0]-p3[1])**2),
                                np.sqrt((p2[0]-p2[1])**2+(p3[0]-p3[1])**2)])
            largest_sides.append(largest_side)
        
        return largest_sides


class dotim():
    def __init__(self, image, is2D=False, treat_3D_as_2D=False):
        if isinstance(image, str):
            # If 'image' is a string, it's treated as a file path
            self.im = sk.io.imread(image)
        elif isinstance(image, np.ndarray):
            # If 'image' is a numpy array, it's already loaded
            self.im = image
        else:
            # Handle other cases or raise an error if needed
            raise ValueError("Invalid image type. 'image' should be a file path (string) or a numpy array.")
        self.is2D = is2D # This contains True if the image is in 2D or false if the image is in 3D (spatial)
        self.nDim = len(self.im.shape) # Just contains the shape of the image
        self.time_dim = False # This will be False if there is no time dimension or true if there is time dimension
        self.treat_3D_as_2D = treat_3D_as_2D # If the 3D image should be treated as 3D or 2D
        
        if self.nDim > 4: # If there are more than four dimensions, there is no process available
            raise ValueError("Dimensions shoudl not exceed 4 (t, z, y, x)")
        
        self.sDim = self.nDim
        
        if self.nDim == 3 and is2D == True: # If image is 2D and it has 3 dimensions, it means that there is time dimension
            self.time_dim = True
            self.sDim -= 1
        elif self.nDim == 4 and is2D == False: # If image is 3D and there are 4 dimensions, it means there is time
            self.time_dim = True
            self.sDim -= 1
        
        if self.time_dim == True:
            self.working_image_shape = self.im.shape[1:]
        else:
            self.working_image_shape = self.im.shape
        
        
        
        
        
        self.dotted_image = None # This will contain the processed dotted image
        # self.coords = None # This will contain the coordinates of the dots in the processed image
        # self.filtered_simplices = None # This will contain the IDs of the triangles that are filtered
        self.mask = None # This will contain the mask of the image
        
        
    def hi(self):
        '''
        Prints the value of nDim, the dimensions of the image.
        '''
        print(f"Your image has {self.nDim} dimensions. It contains {self.sDim} spatial dimensions. Time is {self.time_dim}.")
        
    def __poolAndMax2D(self, input, binshape=(2,2), v=''):
        '''
        Convolutes the image and saves the positions of the brightests pixels.
        '''
        v = v.count('+')
        shapeY, shapeX = input.shape[0], input.shape[1] # Original shape of the image
        while shapeY % binshape[0] != 0: # If the image Y dimension is not even
            zero_plane = np.zeros_like(input[:binshape[0] - input.shape[0] % binshape[0], :]) # Create a 2D plane that matches the size of the data
            input = np.concatenate([zero_plane, input], axis=0) # Concatenate the zero-filled plane with the original data
            print(f"Modify Y: {input.shape}, added layer.") if v > 0 else None
            shapeY = input.shape[0]
        while shapeX % binshape[1] != 0: # If the image X dimension is not even
            zero_plane = np.zeros_like(input[:, :binshape[1] - input.shape[1] % binshape[1]]) # Create a 2D plane that matches the size of the data
            input = np.concatenate([zero_plane, input], axis=1) # Concatenate the zero-filled plane with the original data
            print(f" Modify X: {input.shape}, added layer.") if v > 0 else None
            shapeX =  input.shape[1]
            
        print(input.shape) if v > 0 else None

        shapeY, shapeX = input.shape[0], input.shape[1] # Recompute the shape (new shape)
        newY, newX = int(shapeY/binshape[0]), int(shapeX/binshape[1]) # The new dimensions that the image will have
        # print(shapeY, shapeX, newY, newX)
        poolList = []
        maxList = [[0 for _ in range(newX)] for _ in range(newY)] # Create a nested list to save the coordinates
        print(f"Convolution from {shapeY} {shapeX} to {len(maxList)} {len(maxList[0])}") if v else None

        c = 0
        perc = 0
        total = int(newX*newY)
        for y in range(0, shapeY, binshape[0]):
            for x in range(0, shapeX, binshape[1]):
                patch = input[y:y+binshape[0], x:x+binshape[1]] # Create the patch of pool dimension
                poolList.append(patch.max()) # Get the max value of the patch and append it to the list
                
                indices = np.unravel_index(np.argmax(patch), patch.shape) # Find the indices of the max value
                maxList[int(y / binshape[0])][int(x / binshape[1])] = (y + indices[0], x + indices[1]) # Add the coordinates in the position of the patch in the list
                
                c+=1
                print(f"{c}/{total}, {perc}%", end="\r") if int(c*100/total) > perc and v > 1 else None 
                perc += 1 if int(c*100/total) > perc else 0
                
        
        print(f"{c}/{total}, {perc}%, DONE!") if v > 1 else None
                
        poolArray = np.array(poolList)
        poolArray = np.reshape(poolArray, (newY, newX))
        maxList = np.array(maxList)
        
        return poolArray, maxList, binshape

    def __deconv2D(self, input, maxList, binshape=(2,2), v=''):
        '''
        Upvonvolve the image using the list where the pixel whas the brightest.
        '''
        v = v.count('+')
        shapeY, shapeX = maxList.shape[0], maxList.shape[1]
        newY, newX = int(maxList.shape[0]*binshape[0]), int(maxList.shape[1]*binshape[1])
        print(f"Deconvolution from {shapeY} {shapeX} to {newY} {newX}") if v > 0 else None
        
        output = [[0 for _ in range(newX)] for _ in range(newY)] # Nested list of size input * pool

        c = 0
        perc = 0
        total = int(shapeY*shapeX)
        for y in range(0, shapeY):
            for x in range(0, shapeX):
                indices = maxList[y, x]
                output[indices[0]][indices[1]] = input[y, x] # Add the value of the pixel to the position of the max pixel of the convolution
                
                c+=1
                print(f"{c}/{total}, {perc}%", end="\r") if int(c*100/total) > perc and v > 1 else None 
                perc += 1 if int(c*100/total) > perc else 0
                
        
        print(f"{c}/{total}, {perc}%, DONE!") if v > 1 else None
        
        output = np.array(output)

        return output
        
    def __poolAndMax3d(self, input, binshape=(2,2,2), v=''):
        '''
        Do 3D convolution.
        '''
        v = v.count('+')
        # Make the 3D stack binnable by the size
        while input.shape[0] % binshape[0] != 0: # If the image Y dimension is not even
            zero_plane = np.zeros_like(input[:binshape[0] - input.shape[0] % binshape[0], :, :]) # Create a 2D plane that matches the size of the data
            input = np.concatenate([zero_plane, input], axis=0) # Concatenate the zero-filled plane with the original data
            print(f"Modify Z: {input.shape}, added layer.") if v > 0 else None
        while input.shape[1] % binshape[1] != 0: # If the image X dimension is not even
            zero_plane = np.zeros_like(input[:, :binshape[1] - input.shape[1] % binshape[1], :]) # Create a 2D plane that matches the size of the data
            input = np.concatenate([zero_plane, input], axis=1) # Concatenate the zero-filled plane with the original data
            print(f"Modify Y: {input.shape}, added layer.") if v > 0 else None
        while  input.shape[2] % binshape[2] != 0: # If the image X dimension is not even
            zero_plane = np.zeros_like(input[:, :, :binshape[2] - input.shape[2] % binshape[2]]) # Create a 2D plane that matches the size of the data
            input = np.concatenate([zero_plane, input], axis=2) # Concatenate the zero-filled plane with the original data
            print(f"Modify X: {input.shape}, added layer.") if v > 0 else None

        print(input.shape) if v > 0 else None
        
        shapeZ, shapeY, shapeX = input.shape[0], input.shape[1], input.shape[2] # Compute the shape (new shape)
        newZ, newY, newX = int(shapeZ/binshape[0]), int(shapeY/binshape[1]), int(shapeX/binshape[2]) # The new dimensions that the image will have
        # print(shapeY, shapeX, newY, newX)
        poolList = []
        maxList = [[[0 for _ in range(newX)] for _ in range(newY)] for _ in range(newZ)]
        print(f"Convolution from {shapeZ} {shapeY} {shapeX} to {len(maxList)} {len(maxList[0])} {len(maxList[0][0])}") if v > 0 else None

        c = 1
        total = int(newZ*newY*newX)
        for z in range(0, shapeZ, binshape[0]):
            for y in range(0, shapeY, binshape[1]):
                for x in range(0, shapeX, binshape[2]):
                    patch = input[z:z+binshape[0], y:y+binshape[1], x:x+binshape[2]]
                    poolList.append(patch.max())
                    
                    indices = np.unravel_index(np.argmax(patch), patch.shape)
                    maxList[int(z / binshape[0])][int(y / binshape[1])][int(x / binshape[2])] = (z + indices[0], y + indices[1], x + indices[2])
                    
                    print(f"{c}/{total}", end="\r") if v > 1 else None
                    c+=1
                    
        print(f"{total}/{total}, DONE!") if v > 1 else None
                
        poolArray = np.array(poolList)
        poolArray = np.reshape(poolArray, (newZ, newY, newX))
        maxList = np.array(maxList)
        
        return poolArray, maxList, binshape

    def __deconv3d(self, input, maxList, binshape=(2,2,2), v=''):
        '''
        Do 3D upconvolution.
        '''
        v = v.count('+')
        shapeZ, shapeY, shapeX = maxList.shape[0], maxList.shape[1], maxList.shape[2]
        newZ, newY, newX = int(maxList.shape[0]*binshape[0]), int(maxList.shape[1]*binshape[1]), int(maxList.shape[2]*binshape[2])
        print(f"Deconvolution from {shapeZ} {shapeY} {shapeX} to {newZ} {newY} {newX}") if v > 0 else None
        
        output = [[[0 for _ in range(newX)] for _ in range(newY)] for _ in range(newZ)]
        
        c = 1
        total = int(shapeZ*shapeY*shapeX)
        for z in range(0, shapeZ):
            for y in range(0, shapeY):
                for x in range(0, shapeX):
                    indices = maxList[z, y, x]
                    output[indices[0]][indices[1]][indices[2]] = input[z, y, x]
                    
                    print(f"{c}/{total}", end="\r") if v > 1 else None
                    c+=1
                    
        print(f"{total}/{total}, DONE!") if v > 1 else None
        
        output = np.array(output)

        return output  
    
    def __conv_deconv_process_2D(self, i, times, binshape=(2,2), v=0):
        '''
        Process that will be repeated in case of multiple 2D images.
        '''
        poolList = [0 for _ in range(times)] # Contains the binned
        maxList = [0 for _ in range(times)] # Contains the coordinates of the max intensity pixel
        deconv = [0 for _ in range(times)]
        
        c = 0
        for t in range(times): # CONVOLUTION
            print(f"Convolving: {c+1}/{times}") if v > 0 else None
            if c == 0:
                
                pool_n, maxList_n, _ = self.__poolAndMax2D(i, binshape=binshape)
            else:
                pool_n, maxList_n, _ = self.__poolAndMax2D(poolList[c-1], binshape=binshape)
            poolList[t] = pool_n
            maxList[t] = maxList_n
            c+=1
        
        # MAKE THE MASK
        lastPool = cv2.GaussianBlur(poolList[c-1], (3, 3), 0) # Gaussian
        mean = lastPool.mean()
        pooled_mask = copy.copy(lastPool)
        pooled_mask[lastPool > mean] = 255 # Threshold by the mean of the gaussian
        pooled_mask[lastPool <= mean] = 0
        
        c = times
        for t in range(times): # UPCONVOLUTION
            print(f"Deconvolving: {c}/{times}") if v > 0 else None
            if c == times:
                deconv_n = self.__deconv2D(pooled_mask, maxList[c-1], binshape=binshape) # Deconvolve using the binned mask image and the position of the brightest pixel
            else:
                deconv_n = self.__deconv2D(deconv[times-c-1], maxList[c-1], binshape=binshape)
            deconv[t] = deconv_n
            c-=1
        
        return deconv_n
    
    def __conv_deconv_process_3D(self, i, times, binshape=(2,2,2), v=0):
        poolList = [0 for _ in range(times)]
        maxList = [0 for _ in range(times)]
        deconv = [0 for _ in range(times)]
        
        c = 0
        for t in range(times): # CONVOLUTION
            print(f"Convolving: {c+1}/{times}") if v > 0 else None
            if c == 0:
                pool_n, maxList_n, _ = self.__poolAndMax3d(i, binshape=binshape)
            else:
                pool_n, maxList_n, _ = self.__poolAndMax3d(poolList[c-1], binshape=binshape)
                
            poolList[t] = pool_n
            maxList[t] = maxList_n
            c+=1
            
        # MAKE THE MASK
        lastPool = gaussian_filter(poolList[c-1], sigma=2)
        mean = lastPool.mean()
        pooled_mask = copy.copy(lastPool)
        pooled_mask[lastPool > mean] = 255
        pooled_mask[lastPool <= mean] = 0
        
        c = times
        for t in range(times): # UPCONVOLUTION
            print(f"Deconvolving: {c}/{times}") if v > 0 else None
            if c == times:
                deconv_n = self.__deconv3d(pooled_mask, maxList[c-1], binshape=binshape)
            else:
                deconv_n = self.__deconv3d(deconv[times-c-1], maxList[c-1], binshape=binshape)
                
            deconv[t] = deconv_n
            c-=1
        
        return deconv_n
    
        '''
        pool = None
        max_list = None
        deconv = None

        # Convolution
        for t in range(times):
            print(f"Convolving: {t + 1}/{times}") if v > 0 else None
            pool, max_list, _ = self.__poolAndMax3d(i if t == 0 else pool, binshape=binshape)

        # Make the mask
        last_pool = gaussian_filter(pool, sigma=2)
        mean = last_pool.mean()
        pooled_mask = np.where(last_pool > mean, 255, 0)

        # Deconvolution
        for t in range(times):
            print(f"Deconvolving: {times - t}/{times}") if v > 0 else None
            deconv = self.__deconv3d(pooled_mask if t == 0 else deconv, max_list, binshape=binshape)

        return deconv
        '''
        
    
    def conv_deconv(self, times=3, binshape=(2, 2), v=''):
        '''
        Will make the convolution process n amount of times. It will  make it using the pool size.
        If the image is in 2D, the pool should be (2, 2). But if in 3D, it should be (2, 2, 2).
        It calls a subfunction called __conv_deconv_process (2D or 3D) as many times a needed depending
        if we deal with a single 2D or 3D image or multiple timepoints.
        '''
        v = v.count('+')
        output = []
        
        if len(binshape) != self.sDim and self.treat_3D_as_2D is False: # BINSHAPE CORRECTION
            print("Your binning dimension and image dimension do not coincide.")
            if self.sDim == 2 and self.time_dim is False: # CASE 2D AND NO TIME
                binshape = (2,2)
                print(f"Your binning dimension will be {binshape}")
                
            if self.sDim == 2 and self.time_dim is True: # CASE 2D AND TIME
                binshape = (2,2)
                print(f"Your binning dimension will be {binshape}")
                
            if self.sDim == 3 and self.time_dim is False: # CASE 3D AND NO TIME AND TREAT 3D
                binshape = (2,2,2)
                print(f"Your binning dimension will be {binshape}")
                
            if self.sDim == 3 and self.time_dim is True: # CASE 3D AND TIME AND TREAT 3D
                binshape = (2,2,2)
                print(f"Your binning dimension will be {binshape}")
            
        if self.treat_3D_as_2D is True:
        
            if self.sDim == 3 and self.time_dim is False and len(binshape) != self.sDim-1: # CASE 3D AND NO TIME AND TREAT 2D
                binshape = (2,2)
                print(f"Your binning dimension will be {binshape}")
            
            if self.sDim == 3 and self.time_dim is True and len(binshape) != self.sDim-1: # CASE 3D AND TIME AND TREAT 2D
                binshape = (2,2)
                print(f"Your binning dimension will be {binshape}")



        if self.sDim == 2 and self.time_dim is False: # CASE 2D AND NO TIME
            output = self.__conv_deconv_process_2D(self.im, times, binshape)
            
        if self.sDim == 2 and self.time_dim is True: # CASE 2D AND TIME
            counter = 0
            total = self.im.shape[0]
            for i in self.im: # Do the convolution process for every image
                output.append(self.__conv_deconv_process_2D(i, times, binshape))
                counter += 1
                print(f"{counter}/{total}", end="\r") if v > 0 else None
            
        if self.sDim == 3 and self.time_dim is False and self.treat_3D_as_2D is False: # CASE 3D AND NO TIME AND TREAT 3D
            output = self.__conv_deconv_process_3D(self.im, times, binshape, v)
            
        if self.sDim == 3 and self.time_dim is False and self.treat_3D_as_2D is True: # CASE 3D AND NO TIME AND TREAT 2D
            counter = 0
            total = self.im.shape[0]
            for i in self.im: # Do the convolution process for every image
                output.append(self.__conv_deconv_process_2D(i, times, binshape))
                counter += 1
                print(f"{counter}/{total}", end="\r") if v > 0 else None
            
        if self.sDim == 3 and self.time_dim is True and self.treat_3D_as_2D is False: # CASE 3D AND TIME AND TREAT 3D
            counter = 0
            total = self.im.shape[0]
            for i in self.im: # Repeat the process as many times as timepoints
                output.append(self.__conv_deconv_process_3D(i, times, binshape))
                counter += 1
                print(f"{counter}/{total}", end="\r") if v > 0 else None

        if self.sDim == 3 and self.time_dim is True and self.treat_3D_as_2D is True: # CASE 3D AND TIME AND TREAT 2D
            counter = 0
            total = self.im.shape[0]
            for i in self.im: # Repeat the process as many times as timepoints
                output_i = []
                for j in i: # Repeat the process for every image
                    output_i.append(self.__conv_deconv_process_2D(j, times, binshape))
                counter += 1
                print(f"{counter}/{total}", end="\r") if v > 0 else None
                output.append(output_i)

        self.dotted_image = np.array(output)
            
        return self.dotted_image
        
    def get_coords(self, i):
        coords = np.transpose(np.nonzero(i != 0))
        
        return coords
        
    def delaunay(self, i, threshold_area, threshold_angle, delaunay_to_2D=True):
        '''
        '''  
        tri = MyDelaunay(i, delaunay_to_2D)
        # Calculate triangle areas and largest angles
        triangle_areas = np.array(tri.calculate_triangle_areas())
        largest_angles = np.array(tri.largest_triangle_angle())

        # Create masks based on thresholds
        mask_area = (triangle_areas - triangle_areas.mean()) < threshold_area * triangle_areas.std()
        mask_angle = largest_angles < threshold_angle

        # Combine masks using logical AND (you can also use | for OR)
        combined_mask = mask_area & mask_angle

        filtered_simplices = tri.simplices[combined_mask]

        
        return filtered_simplices
        
    def bresenham_line(self, x1, y1, x2, y2):
        points = []

        dx = abs(x2 - x1)
        dy = abs(y2 - y1)

        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1

        error = dx - dy
        x, y = x1, y1

        while True:
            points.append((x, y))
            if x == x2 and y == y2:
                break
            e2 = 2 * error
            if e2 > -dy:
                error -= dy
                x += sx

            if e2 < dx:
                error += dx
                y += sy

        return points
    
    def bresenham_line_3d(self, x1, y1, z1, x2, y2, z2):
        ListOfPoints = []
        ListOfPoints.append((x1, y1, z1))
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        dz = abs(z2 - z1)
        if (x2 > x1):
            xs = 1
        else:
            xs = -1
        if (y2 > y1):
            ys = 1
        else:
            ys = -1
        if (z2 > z1):
            zs = 1
        else:
            zs = -1
    
        # Driving axis is X-axis"
        if (dx >= dy and dx >= dz):        
            p1 = 2 * dy - dx
            p2 = 2 * dz - dx
            while (x1 != x2):
                x1 += xs
                if (p1 >= 0):
                    y1 += ys
                    p1 -= 2 * dx
                if (p2 >= 0):
                    z1 += zs
                    p2 -= 2 * dx
                p1 += 2 * dy
                p2 += 2 * dz
                ListOfPoints.append((x1, y1, z1))
    
        # Driving axis is Y-axis"
        elif (dy >= dx and dy >= dz):       
            p1 = 2 * dx - dy
            p2 = 2 * dz - dy
            while (y1 != y2):
                y1 += ys
                if (p1 >= 0):
                    x1 += xs
                    p1 -= 2 * dy
                if (p2 >= 0):
                    z1 += zs
                    p2 -= 2 * dy
                p1 += 2 * dx
                p2 += 2 * dz
                ListOfPoints.append((x1, y1, z1))
    
        # Driving axis is Z-axis"
        else:        
            p1 = 2 * dy - dz
            p2 = 2 * dx - dz
            while (z1 != z2):
                z1 += zs
                if (p1 >= 0):
                    y1 += ys
                    p1 -= 2 * dz
                if (p2 >= 0):
                    x1 += xs
                    p2 -= 2 * dz
                p1 += 2 * dy
                p2 += 2 * dx
                ListOfPoints.append((x1, y1, z1))
                
        return ListOfPoints

    
    def get_mask(self, times=3, binshape=(2,2), morph_close_k=20, morph_open_k=10, m_ball=5, threshold_area=0.1, threshold_angle=90, v=''): # Fer el bucle aquí, el de mirar les dimensions de la imatge!!!
        '''
        Get the mask of the image created from the points obtained from the convolution.
        
        - times is the amount of convolutions done. If the dots are already computed, there is no need.
        
        - binshape is the size of the binning done at each convolution.  If the dots are already computed, there is no need.
        
        - morph_close_k is the kernel size that will be used for 2D images or slices.
        
        - morph_open_k is the kernel size that will be used for 2D images or slices.
        
        - m_ball is the kernel size that will be used for 3D images.
        
        - threshold_area is the threshold used to discard or keep the resulting triangles from the Delaunay operation (area-based): mask_area = (triangle_areas - triangle_areas.mean()) < threshold_area * triangle_areas.std()
        
        - threshold_angle is the threshold used to discard or keep the resulting triangles from the Delaunay operation (angle-based): mask_angle = largest_angles < threshold_angle

        - v means verbose. To keep track of the process: v='+'.

        '''
        
        mask = []
        
        if self.dotted_image is None:
            self.dotted_image = self.conv_deconv(times, binshape, v)
        
    
        if self.sDim == 2 and self.time_dim is False: ### CASE 2 SPACE DIMS AND 0 TIME DIMS
            coords = self.get_coords(self.dotted_image) 
            mask = np.zeros((self.dotted_image.shape[0], self.dotted_image.shape[1]))
            if len(coords) > 10:
                filtered_simplices = self.delaunay(coords, threshold_area, threshold_angle, delaunay_to_2D=False)
                
                
                for i in filtered_simplices: # Iterate over the triangles and put 1 to the lines that unite the dots
                    to_1 = self.bresenham_line(*coords[i][0], *coords[i][1])
                    to_1 += list(self.bresenham_line(*coords[i][1], *coords[i][2]))
                    to_1 += list(self.bresenham_line(*coords[i][0], *coords[i][2]))
                    for j in to_1:
                        mask[j] = 1
                mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((morph_close_k, morph_close_k))) 
                mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((morph_open_k, morph_open_k)))

                mask = np.resize(mask, self.working_image_shape)
            
            
        if self.sDim == 2 and self.time_dim is True: ### CASE 2 SPACE DIMS AND 1 TIME DIMS
            mask = []
            for i in self.dotted_image:
                coords = self.get_coords(i)
                mask_i = np.zeros((i.shape[0], i.shape[1]))
                if len(coords) > 10:                
                
                    filtered_simplices = self.delaunay(coords, threshold_area, threshold_angle, delaunay_to_2D=False)
                
                    
                    for j in filtered_simplices: # Iterate over the triangles and put 1 to the lines that unite the dots
                        to_1 = self.bresenham_line(*coords[j][0], *coords[j][1])
                        to_1 += list(self.bresenham_line(*coords[j][1], *coords[j][2]))
                        to_1 += list(self.bresenham_line(*coords[j][0], *coords[j][2]))
                        for k in to_1:
                            mask_i[k] = 1
                    mask_i = cv2.morphologyEx(mask_i, cv2.MORPH_CLOSE, np.ones((morph_close_k, morph_close_k))) 
                    mask_i = cv2.morphologyEx(mask_i, cv2.MORPH_OPEN, np.ones((morph_open_k, morph_open_k)))

                mask_i = np.resize(mask_i, self.working_image_shape)

                mask.append(mask_i)

        
        if self.sDim == 3 and self.time_dim is False and self.treat_3D_as_2D is False: ### CASE 3 SPACE DIMS AND 0 TIME DIMS AND TREAT 3D
            coords = self.get_coords(self.dotted_image)
            mask = np.zeros((self.dotted_image.shape[0], self.dotted_image.shape[1], self.dotted_image.shape[2]))
            if len(coords) > 10:
                filtered_simplices = self.delaunay(coords, threshold_area, threshold_angle, delaunay_to_2D=True)
                
                
                for i in filtered_simplices:
                    to_1 = self.bresenham_line_3d(*coords[i][0], *coords[i][1])
                    to_1 += list(self.bresenham_line_3d(*coords[i][1], *coords[i][2]))
                    to_1 += list(self.bresenham_line_3d(*coords[i][0], *coords[i][2]))
                    for j in to_1:
                        mask[j] = 1
                        
                mask = sk.morphology.binary_closing(mask, footprint=sk.morphology.ball(m_ball))
                mask = sk.morphology.binary_opening(mask, footprint=sk.morphology.ball(m_ball))

                mask = np.resize(mask, self.working_image_shape)
            
            
        if self.sDim == 3 and self.time_dim is False and self.treat_3D_as_2D is True: ### CASE 3 SPACE DIMS AND 0 TIME DIMS AND TREAT 2D
            mask = []
            for i in self.dotted_image:
                coords = self.get_coords(i)
                mask_i = np.zeros((i.shape[0], i.shape[1]))
                if len(coords) > 10:
                    filtered_simplices = self.delaunay(coords, threshold_area, threshold_angle, delaunay_to_2D=False)
                    
                    
                    for j in filtered_simplices:
                        to_1 = self.bresenham_line(*coords[j][0], *coords[j][1])
                        to_1 += list(self.bresenham_line(*coords[j][1], *coords[j][2]))
                        to_1 += list(self.bresenham_line(*coords[j][0], *coords[j][2]))
                        for k in to_1:
                            mask_i[k] = 1
                        
                    mask_i = cv2.morphologyEx(mask_i, cv2.MORPH_CLOSE, np.ones((morph_close_k, morph_close_k))) 
                    mask_i = cv2.morphologyEx(mask_i, cv2.MORPH_OPEN, np.ones((morph_open_k, morph_open_k)))
                
                mask.append(mask_i)

            mask = np.resize(mask, self.working_image_shape)
            
            
        if self.sDim == 3 and self.time_dim is True and self.treat_3D_as_2D is False: ### CASE 3 SPACE DIMS AND 1 TIME DIMS AND TREAT 3D
            mask = []
            for i in self.dotted_image:
                coords = self.get_coords(i)
                mask_i = np.zeros((i.shape[0], i.shape[1], i.shape[2]))
                if len(coords) > 10:
                    filtered_simplices = self.delaunay(coords, threshold_area, threshold_angle, delaunay_to_2D=True)
                    
                    
                    for j in filtered_simplices:
                        to_1 = self.bresenham_line_3d(*coords[j][0], *coords[j][1])
                        to_1 += list(self.bresenham_line_3d(*coords[j][1], *coords[j][2]))
                        to_1 += list(self.bresenham_line_3d(*coords[j][0], *coords[j][2]))
                        for k in to_1:
                            mask_i[k] = 1
                            
                    mask_i = sk.morphology.binary_closing(mask_i, footprint=sk.morphology.ball(m_ball))
                    mask_i = sk.morphology.binary_opening(mask_i, footprint=sk.morphology.ball(m_ball))

                    mask_i = np.resize(mask_i, self.working_image_shape)
                    
            mask.append(mask_i)
            
        
        
        if self.sDim == 3 and self.time_dim is True and self.treat_3D_as_2D is True: ### CASE 3 SPACE DIMS AND 1 TIME DIMS AND TREAT 2D
            mask = []
            for i in self.dotted_image:
                mask_i = []
                for j in i:
                    coords = self.get_coords(j)
                    mask_j = np.zeros((j.shape[0], j.shape[1]))
                    if len(coords) > 10: ## Otherwise the delaunay does not work
                        filtered_simplices = self.delaunay(coords, threshold_area, threshold_angle, delaunay_to_2D=False)
                        
                        for k in filtered_simplices:
                            to_1 = self.bresenham_line(*coords[k][0], *coords[k][1])
                            to_1 += list(self.bresenham_line(*coords[k][1], *coords[k][2]))
                            to_1 += list(self.bresenham_line(*coords[k][0], *coords[k][2]))
                            for l in to_1:
                                mask_j[l] = 1
                                
                        mask_j = cv2.morphologyEx(mask_j, cv2.MORPH_CLOSE, np.ones((morph_close_k, morph_close_k))) 
                        mask_j = cv2.morphologyEx(mask_j, cv2.MORPH_OPEN, np.ones((morph_open_k, morph_open_k)))
                        
                    mask_i.append(mask_j)

                mask_i = np.resize(mask_i, self.working_image_shape)

                mask.append(mask_i)
        
        self.mask = np.array(mask)

        return self.mask



    
