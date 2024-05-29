import shutil
import os

from factorio_dir import main_pth

filename = "hwdp_0.0.1"
filename_zipped = filename + ".zip"

shutil.make_archive(filename, 'zip', filename)


shutil.move(filename_zipped, os.path.join(main_pth, "mods", filename_zipped))