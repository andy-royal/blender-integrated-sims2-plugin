#!/usr/bin/python3
#-*- coding: utf-8 -*-

bl_info = {
    "name": "Sims 2 import plugin",
    "category": "Import-Export",
}

import bpy
from bpy.props import IntProperty, CollectionProperty #, StringProperty 
from bpy.types import Panel, UIList

from blendersims2.fileio.package import PackageManager
from blendersims2.sims2 import AddSims2DirectoriesToPackageManager

class Sims2UIListPanel(Panel):
    """Creates a Panel in the Scene properties window"""
    bl_idname = "OBJECT_PT_Sims2_Object_select"
    bl_label = "Sims2"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    
    def draw(self, context):
        layout = self.layout
        scn = bpy.context.scene

        rows = 2

        row = layout.row()
        row.template_list("UL_items", "", scn, "custom", scn, "custom_index", rows=rows)

        row = layout.row()
        row.operator("custom.cres_list_action", text="SCAN").action = 'SCAN'
        
class UL_items(UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        #split = layout.split(0.3)
        #split.label("Index: %d" % (index))
        #split.prop(item, "name", text="", emboss=False, translate=False, icon='BORDER_RECT')
        layout.prop(item, "name", text="", emboss=False, translate=False)
        #layout.prop(item, "value", text="", emboss=False, translate=False)

    def invoke(self, context, event):
        pass

class Uilist_actions(bpy.types.Operator):
    bl_idname = "custom.cres_list_action"
    bl_label = "CRES List Action"

    action = bpy.props.EnumProperty(
        items=(
            ('SCAN', "Scan", ""),
        )
    )

    def invoke(self, context, event):

        DEBUG = False
        
        scn = context.scene

        if self.action == 'SCAN':
            
            self.report({'INFO'}, 'Clearing list')
            scn.custom.clear()
            self.report({'INFO'}, 'List cleared')
 
            packman = scn.packman
#            AddSims2DirectoriesToPackageManager(packman)
#            packman.ReadDBPFIndices()

            gen = packman.getAllObjects()
            
            #for _ in range(10):
            #    group, name = next(gen)
            index = 0
            for group, name in gen:

                if group >= (1 << 31):
                    group -= (1 << 32);

                item = scn.custom.add()
                item.name = name
                item.value = group
                index += 1

                if DEBUG:
                    if index % 20 == 0:
                        self.report({'INFO'}, '%d items added to list' % index)
            
            self.report({'INFO'}, '%d items added to list' % index)

        return {"FINISHED"}

class ObjectRefItem(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(name="Object Name", default="Unknown")
    value = bpy.props.IntProperty(name="Group", default=22, subtype='UNSIGNED')

def register_RCOL():
    bpy.utils.register_class(Sims2UIListPanel)
    bpy.utils.register_class(UL_items)
    bpy.utils.register_class(Uilist_actions)
    bpy.utils.register_class(ObjectRefItem)
    bpy.types.Scene.custom = CollectionProperty(type=ObjectRefItem)
    bpy.types.Scene.custom_index = IntProperty()
    bpy.types.Scene.packman = PackageManager()
    AddSims2DirectoriesToPackageManager(bpy.types.Scene.packman)
    bpy.types.Scene.packman.ReadDBPFIndices()

def unregister():
    bpy.utils.unregister_class(Sims2UIListPanel)
    bpy.utils.unregister_class(UL_items)
    bpy.utils.unregister_class(Uilist_actions)
    bpy.utils.unregister_class(ObjectRefItem)
    del bpy.types.Scene.custom
    del bpy.types.Scene.custom_index
    del bpy.types.Scene.packman

# This allows you to run the script directly from blenders text editor
# to test the addon without having to install it.
if __name__ == "__main__":
    register_RCOL()
