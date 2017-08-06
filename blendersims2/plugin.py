#!/usr/bin/python3
#-*- coding: utf-8 -*-

bl_info = {
    "name": "Sims 2 import plugin",
    "category": "Import-Export",
}

import bpy

from blendersims2.fileio.package import PackageManager
from blendersims2.sims2 import AddSims2DirectoriesToPackageManager

# Temporary code while sims2 is in a state of flux
#import imp
#imp.reload(blendersims2)

class Sims2Import(bpy.types.Operator):
    """Sims 2 importer"""              # blender will use this as a tooltip for menu items and buttons.
    bl_idname = "import.sims_2"        # unique identifier for buttons and menu items to reference.
    bl_label = "Sims 2 importer"       # display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # enable undo for the operator.
    
    # Set this before calling file selector to set the default search path. After file selector it will
    # store the file selected
    filepath = bpy.props.StringProperty(subtype='DIR_PATH') 

    def execute(self, context):
        """execute() is called by Blender when running the operator."""

        self.report({'INFO'}, "Found %d RCOLs" % len(self.packman.package_index))

        return {'FINISHED'}

    def invoke(self, context, event):
        """invoke() is the first function called on the operator. Here the package manager is initialised
           and packages are read. print functions will output to the console."""
           
        self.packman = PackageManager()
        AddSims2DirectoriesToPackageManager(self.packman)
        self.packman.ReadDBPFIndices()
        print("Found %d RCOLs" % len(self.packman.package_index))
        return self.execute(context)
        #context.window_manager.fileselect_add(self)
        #return {'RUNNING_MODAL'}
    
def register():
    bpy.utils.register_class(Sims2Import)

def unregister():
    bpy.utils.unregister_class(Sims2Import)

# This allows you to run the script directly from blenders text editor
# to test the addon without having to install it.
if __name__ == "__main__":
    register()
