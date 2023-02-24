import json
from math import degrees

import bpy
import bpy_extras


bl_info = {
    "name": "Export Animation to Asper",
    "author": "Ishant Pundir",
    "version": (1, 0, 0),
    "blender": (2, 83, 4),
    "location": "VIEW_3D",
    "description": "Export animation that Asper can understand",
    "warning": "",
    "wiki_url": "",
    "support": "COMMUNITY",
    "category": "Import-Export",
}


class PositionExporter(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    """ This class goes through the animation timeline & export all positions """
    bl_idname = "object.asper_position_exporter"
    bl_label = "Asper position exporter"
    filename_ext = ".json"

    def _get_position_for_frame(self, context, frame:int):
        # Go the frame in timeline
        context.scene.frame_set(frame)
        master_bone = context.scene.objects['master-control'].pose.bones.get('master-bone')
        position = master_bone.rotation_euler
        
        head_pan = position.x
        head_roll = -position.z
        base = position.y

        return degrees(head_pan), degrees(head_roll), degrees(base)

    def save_json(self, data):
        with open(file=self.filepath, mode='w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        
    def execute(self, context):
        positions = {
            'total_frames': context.scene.export_end_frame - context.scene.export_start_frame,
            'fps': context.scene.render.fps,
            'pan': [],
            'roll': [],
            'turn': []
        }
        
        print(f"Export frames from {context.scene.export_start_frame} -- {context.scene.export_end_frame}")
        
        for frame in range(context.scene.export_start_frame, context.scene.export_end_frame + 1):
            pan, roll, turn = self._get_position_for_frame(context, frame)
            positions['pan'].append(pan)
            positions['roll'].append(roll)
            positions['turn'].append(turn)
        
        
        self.save_json(positions)
        return {'FINISHED'}

exportStartFrame = bpy.props.IntProperty(
    name="Start frame", default=0,
    min=0, max=bpy.context.scene.frame_end
)

exportEndFrame = bpy.props.IntProperty(
    name="End frame", default=bpy.context.scene.frame_end,
    min=0, max=bpy.context.scene.frame_end
)

class AsperPanel(bpy.types.Panel):
    """Creates a Panel"""
    bl_label = "Asper"
    bl_idname = "PT_Asper"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Asper"
    
    def draw(self, context):
        layout = self.layout
        layout.label(text="Asper controller")
        
        col = self.layout.column()
        
        for (prop_name, _) in PROPS:
            col.prop(context.scene, prop_name)
        
        
        row = layout.row()
        row.operator(PositionExporter.bl_idname, text="Export to json", icon="CONSOLE")


CLASSES = [
    AsperPanel,
    PositionExporter
]

PROPS = [
    ('export_start_frame', exportStartFrame),
    ('export_end_frame', exportEndFrame)
]


def register():
    for prop_name, prop_value in PROPS:
        setattr(bpy.types.Scene, prop_name, prop_value)

    for c in CLASSES: bpy.utils.register_class(c)

def unregister():
    for prop_name, _ in PROPS:
        delattr(bpy.types.Scene, prop_name)
        
    for c in CLASSES: bpy.utils.unregister_class(c)

if __name__ == "__main__":
    register()