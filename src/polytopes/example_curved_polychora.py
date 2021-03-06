# -*- coding: utf-8 -*-
"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Render curved 4d polychoron examples
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright (c) 2018 by Zhao Liang.
"""
import os
import subprocess
from fractions import Fraction
from polytopes.models import Polychora
from polytopes.povray import pov_vector, pov_index_array1d


IMAGE_DIR = "polychora_frames"        # directory to save the frames
POV_EXE = "povray"                    # POV-Ray exe binary
SCENE_FILE = "polychora_curved.pov"   # the main scene file
IMAGE_SIZE = 600                      # image size in pixels
FRAMES = 1                            # number of frames
IMAGE_QUALITY_LEVEL = 11              # between 0-11
SUPER_SAMPLING_LEVEL = 5              # between 1-9
ANTIALIASING_LEVEL = 0.001            # lower for better quality
DATAFILE_NAME = "polychora-data.inc"  # export data to this file

data_file = os.path.join(os.getcwd(), "povray", DATAFILE_NAME)

if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

POV_COMMAND = " cd povray && " + \
              " {} +I{}".format(POV_EXE, SCENE_FILE) + \
              " +W{} +H{}".format(IMAGE_SIZE, IMAGE_SIZE) + \
              " +Q{}".format(IMAGE_QUALITY_LEVEL) + \
              " +A{}".format(ANTIALIASING_LEVEL) + \
              " +R{}".format(SUPER_SAMPLING_LEVEL) + \
              " +KFI0" + \
              " +KFF{}".format(FRAMES - 1) + \
              " -V" + \
              " +O../{}/".format(IMAGE_DIR) + "{}"

POV_TEMPLATE = """
#declare vertex_size = {};
#declare edge_size = {};
#declare camera_loc = {};
#declare obj_rotation = {};
#declare size_func = {};
#declare face_max= {};
#declare face_min = {};
#declare face_index = {};
#declare use_area_light = {};

// this macro is used for adjusting the size of edges
// according to their positions in the space.
#macro get_size(q)
  #local len = vlength(q);
  #if (size_func = 0)
    #local len = (1.0 + len * len) / 4;
  #else #if (size_func = 1)
    #local len = 2.0 * log(2.0 + len * len);
  #else
    #local len = 2.0 * log(1.13 + len * len);
  #end
  #end
  len
#end

#macro choose_face(i, face_size)
  #local chosen = false;
  #for (ind, 0, dimension_size(faces, 1) - 1)
    #if (i = ind)
      #if (face_size > face_min & face_size < face_max)
        #local chosen = true;
      #end
    #end
  #end
  chosen
#end

#declare vertices = {};

#declare edges = {};

#declare faces = {};
"""


def draw(coxeter_diagram,
         trunc_type,
         extra_relations=(),
         description="polychora",
         camera_loc=(0, 0, 180),
         rotation=(0, 0, 0),
         vertex_size=0.04,
         edge_size=0.02,
         size_func=0,
         face_index=(0,),
         face_max=3.0,
         face_min=0.5,
         use_area_light=False):
    """
    Export data to povray .inc file and call the rendering process.
    :param face_index: a list controls which types of faces are shown.
    :param face_max: only faces smaller than this threshold are shown.
    :param face_min: only faces larger than this threshold are shown.
    """
    P = Polychora(coxeter_diagram, trunc_type, extra_relations)
    P.build_geometry()
    vert_data, edge_data, face_data = P.get_povray_data()
    with open(data_file, "w") as f:
        f.write(POV_TEMPLATE.format(
            vertex_size,
            edge_size,
            pov_vector(camera_loc),
            pov_vector(rotation),
            size_func,
            face_max,
            face_min,
            pov_index_array1d(face_index),
            int(use_area_light),
            vert_data,
            edge_data,
            face_data))

    print("rendering {}: {} vertices, {} edges, {} faces".format(
        description,
        P.num_vertices,
        P.num_edges,
        P.num_faces))

    process = subprocess.Popen(
        POV_COMMAND.format(description),
        shell=True,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE)

    _, err = process.communicate()
    if process.returncode:
        print(type(err), err)
        raise IOError("POVRay error: " + err.decode("ascii"))


def main():
    draw((3, 2, 2, 3, 2, 3), (1, 0, 0, 0), description="5-cell",
         camera_loc=(0, 0, 6), vertex_size=0.08, rotation=(-30, 60, 0),
         edge_size=0.04, size_func=1)

    draw((3, 2, 2, 3, 2, 5), (1, 0, 0, 0), description="600-cell",
         camera_loc=(0, 0, 25), vertex_size=0.12, edge_size=0.04,
         size_func=2, face_max=4.0, face_min=3.0)

    draw((5, 2, 2, 3, 2, 3), (1, 0, 0, 1), description="runcinated-120-cell",
         camera_loc=(0, 0, 18), vertex_size=0.028, edge_size=0.014, face_min=20)


if __name__ == "__main__":
    main()
