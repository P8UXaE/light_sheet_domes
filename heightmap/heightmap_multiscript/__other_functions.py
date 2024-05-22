
# def get_3D_gaussian(array_3D):

#     def gaussian_2D(i, num, sigma):
#         blurred_i = sk.filters.gaussian(i, sigma=sigma, mode='nearest')
#         return num, blurred_i
    
#     def run_2D_gaussian(array_3D, sigma):
#         return_dict = {}
#         max_jobs = 5
#         pool = multiprocessing.Pool()
#         results = [pool.apply_async(gaussian_2D, args=(i,num, sigma)) for num, i in enumerate(array_3D)]
#         pool.close()
#         pool.join()

#         return_dict = {}
#         for result in results:
#             num, blurred_i = result.get()
#             if blurred_i is not None:
#                 return_dict[num] = blurred_i

#         blurred_array = np.array([return_dict[idx] for idx in sorted(return_dict.keys())])

#         return blurred_array
    
#     blurredXY = run_2D_gaussian(array_3D=array_3D, sigma=(20, 20))
#     blurredXY_r = common_functions.get_image_r(blurredXY)
#     blurredXYZ_r = run_2D_gaussian(array_3D=blurredXY_r, sigma=(20,0))

#     blurredXYZ = np.transpose(blurredXYZ_r, axes=(1,2,0))
#     blurredXYZ = common_functions.normalize_image(blurredXYZ, 65535).astype(np.uint16)

#     return blurredXYZ



# def gaussian_2D(i, num, sigma):
#     blurred_i = sk.filters.gaussian(i, sigma=sigma, mode='nearest')
#     return num, blurred_i

# ##### GAUSSIAN 2D OVER XY slices #####
# return_dict = {}
# max_jobs = 5  # Change this to the maximum number of concurrent processes you want
# pool = multiprocessing.Pool()  # Use all available cores
# results = [pool.apply_async(gaussian_2D, args=(i, num, (20,20))) for num, i in enumerate(hull_top_line)]
# pool.close()
# pool.join()

# # Get results in order
# return_dict = {}
# for result in results:
#     num, blurred_i = result.get()
#     if blurred_i is not None:
#         return_dict[num] = blurred_i

# gaussian_hull_top_line = np.array([return_dict[idx] for idx in sorted(return_dict.keys())])

# gaussian_hull_top_line_r = common_functions.get_image_r(gaussian_hull_top_line)

# ##### GAUSSIAN OVER 0 AXIS (VERTICAL) #####
# return_dict = {}
# max_jobs = 5  # Change this to the maximum number of concurrent processes you want
# pool = multiprocessing.Pool()  # Use all available cores
# results = [pool.apply_async(gaussian_2D, args=(i, num, (20,0))) for num, i in enumerate(gaussian_hull_top_line_r)]
# pool.close()
# pool.join()

# # Get results in order
# return_dict = {}
# for result in results:
#     num, blurred_i = result.get()
#     if blurred_i is not None:
#         return_dict[num] = blurred_i

# gaussian_hull_top_line_r = np.array([return_dict[idx] for idx in sorted(return_dict.keys())])
# gaussian_hull_top_line = np.transpose(gaussian_hull_top_line_r, axes=(1,2,0))

# # Make first x-y and then z gives the same as 3d.....
# # gaussian_hull_top_line = sk.filters.gaussian(hull_top_line, sigma=(0,20,20), mode='nearest')
# # gaussian_hull_top_line = sk.filters.gaussian(gaussian_hull_top_line, sigma=(20,0,0), mode='nearest')

# gaussian_hull_top_line = common_functions.normalize_image(gaussian_hull_top_line, 65535).astype(np.uint16)


