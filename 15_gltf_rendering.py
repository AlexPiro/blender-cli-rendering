# blender --background --python 01_cube.py --render-frame 1 -- </path/to/output/image> <resolution_percentage> <num_samples>

import bpy
import os
import sys
import math

working_dir_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(working_dir_path)

import utils


def get_output_file_path() -> str:
    return bpy.path.relpath(str(sys.argv[sys.argv.index('--') + 1]))


def get_resolution_percentage() -> int:
    return int(sys.argv[sys.argv.index('--') + 2])


def get_num_samples() -> int:
    return int(sys.argv[sys.argv.index('--') + 3])

def enable_gpus(device_type, use_cpus=False, tile_size=()):
    preferences = bpy.context.preferences
    cycles_preferences = preferences.addons["cycles"].preferences
    cycles_preferences.get_devices()
    # cuda_devices = cycles_preferences.devices[0]
    # opencl_devices = cycles_preferences.devices[1]
    # optix_devices = cycles_preferences.devices[2]


    # if device_type == "CUDA":
    #     devices = cuda_devices
    # elif device_type == "OPENCL":
    #     devices = opencl_devices
    # elif device_type == "Optix":
    #     devices = optix_devices
    # else:
    #     raise RuntimeError("Unsupported device type")

    activated_gpus = []

    for device in cycles_preferences.devices:
        if device.type == "CPU":
            device.use = use_cpus
        else:
            device.use = True
            activated_gpus.append(device.name)

    cycles_preferences.compute_device_type = device_type
    bpy.context.scene.cycles.device = "GPU"
    
    # if len(tile_size) > 0:
    #     bpy.context.scene.render.tile_x = tile_size[0]
    #     bpy.context.scene.render.tile_y = tile_size[1]

    return activated_gpus


if __name__ == "__main__":
    # Args
    output_file_path = get_output_file_path()
    resolution_percentage = get_resolution_percentage()
    num_samples = get_num_samples()

    #enable GPU rendering
    
    enable_gpus("OPTIX", tile_size=(512, 512))

    # Setting

    script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
    rel_path = "assets/models/output.gltf"
    scenepath = os.path.join(script_dir, rel_path)


    # bpy.ops.wm.read_factory_settings(use_empty=True)

    # Manually delete the cube for now 
    bpy.data.objects.remove(bpy.data.objects["Cube"], do_unlink=True)

    # Import the GLTF model
    bpy.ops.import_scene.gltf(filepath=scenepath)

    # Setup the camera
    camera_object = bpy.data.objects["Camera"]
    camera_object.location = (0, 0, 51)
    camera_object.rotation_euler = (0, 0, 0)

    # Setup the lighting
    light_object = bpy.data.objects['Light']
    light_object.location = (0, 0, 10)
    light_object.rotation_euler = (0, 0, 0)

    light_object.data.type = 'SUN'
    light_object.data.energy = 1.5
    light_object.data.angle = math.pi / 2

    scene = bpy.context.scene
    utils.set_output_properties(scene, resolution_percentage, output_file_path)
    utils.set_cycles_renderer(scene, camera_object, num_samples)
