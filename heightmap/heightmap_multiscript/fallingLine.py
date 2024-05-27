import subprocess
import os



# time_dome = str(4)
time_dome = str(1)
dome_number = str(99)
# folder_and_dome = str('./../../../../Desktop/dome70_fallinglineMove/70_denoised_tp')
folder_and_dome = str('./../../../../Desktop/dome'+dome_number+'_tp'+time_dome+'/'+dome_number+'_denoised_tp')

wd = folder_and_dome + time_dome


subprocess.run(["python3", "get_lines.py", wd])

print('Run gaussians hull top line')

subprocess.run(["python3", "get_gaussian.py", wd, 'hull_top_line'])

print('Run gaussians sum masks')

subprocess.run(["python3", "get_gaussian.py", wd, 'sum_top_line'])

print("Shape finder 1")

subprocess.run(["python3", "shape_finder_2D_1.py", wd, 'n'])

print("Shape finder 2")

subprocess.run(["python3", "shape_finder_2D_1.py", wd, 'r'])

print("Sum both dots")

subprocess.run(["python3", "sum_arrays.py", wd, 'apical_dots', '0'])

print('Run gaussians dots')

subprocess.run(["python3", "get_gaussian.py", wd, 'apical_dots_total'])

moveLine = '0'

print("Shape finder second time 1")

subprocess.run(["python3", "shape_finder_2D_2.py", wd, 'apical_dots_total', 'n', moveLine])

print("Shape finder second time 2")

subprocess.run(["python3", "shape_finder_2D_2.py", wd, 'apical_dots_total', 'r', moveLine])

print("Sum both dots")

subprocess.run(["python3", "sum_arrays.py", wd, 'apical_dots', '1'])

print('Run gaussians dots 2')

subprocess.run(["python3", "get_gaussian.py", wd, 'apical_dots_total'])






