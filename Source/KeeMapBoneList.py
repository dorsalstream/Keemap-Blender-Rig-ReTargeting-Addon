import bpy
import json   

class KEEMAP_BONE_UL_List(bpy.types.UIList): 
    """Demo UIList.""" 
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        # We could write some code to decide which icon to use here... 
        custom_icon = 'BONE_DATA' 
        
        # Make sure your code supports all 3 layout types if 
        if self.layout_type in {'DEFAULT', 'COMPACT'}: 
            layout.label(text=item.name, icon = custom_icon) 
        elif self.layout_type in {'GRID'}: 
            layout.alignment = 'CENTER' 
            layout.label(text="", icon = custom_icon) 
            
       
class KEEMAP_LIST_OT_NewItem(bpy.types.Operator): 
    """Add a new item to the list.""" 
    bl_idname = "keemap_bone_mapping_list.new_item" 
    bl_label = "Add a new item" 

    def execute(self, context): 
        index = context.scene.keemap_bone_mapping_list_index 
        context.scene.keemap_bone_mapping_list.add() 
        index = len(context.scene.keemap_bone_mapping_list)
        return{'FINISHED'}       
    
class KEEMAP_LIST_OT_DeleteItem(bpy.types.Operator): 
    """Delete the selected item from the list.""" 
    bl_idname = "keemap_bone_mapping_list.delete_item" 
    bl_label = "Deletes an item" 
    
    @classmethod 
    def poll(cls, context): 
        return context.scene.keemap_bone_mapping_list 
    
    def execute(self, context): 
        bone_mapping_list = context.scene.keemap_bone_mapping_list
        index = context.scene.keemap_bone_mapping_list_index 
        bone_mapping_list.remove(index) 
        index = min(max(0, index - 1), len(bone_mapping_list) - 1) 
        return{'FINISHED'}

class KEEMAP_LIST_OT_MoveItem(bpy.types.Operator): 
    """Move an item in the list.""" 
    bl_idname = "keemap_bone_mapping_list.move_item" 
    bl_label = "Move an item in the list" 
    direction: bpy.props.EnumProperty(items=(('UP', 'Up', ""), ('DOWN', 'Down', ""),)) 

    @classmethod 
    def poll(cls, context): 
        return context.scene.keemap_bone_mapping_list 
    
    def move_index(self): 
        """ Move index of an item render queue while clamping it. """ 
        scene = bpy.context.scene	
        index = scene.keemap_bone_mapping_list_index 
        list_length = len(bpy.context.scene.keemap_bone_mapping_list) - 1 # (index starts at 0) 
        new_index = index + (-1 if self.direction == 'UP' else 1) 
        index = max(0, min(new_index, list_length)) 
    
    def execute(self, context): 
        bone_mapping_list = context.scene.keemap_bone_mapping_list 
        scene = context.scene	
        index = scene.keemap_bone_mapping_list_index 
        neighbor = index + (-1 if self.direction == 'UP' else 1) 
        bone_mapping_list.move(neighbor, index) 
        self.move_index() 
        return{'FINISHED'}
    
class KEEMAP_LIST_OT_ReadInFile(bpy.types.Operator): 
    """Read in Bone Mapping File""" 
    bl_idname = "wm.keemap_read_file" 
    bl_label = "Read In Bone Mapping File" 

    def execute(self, context): 
        
        context.scene.keemap_bone_mapping_list_index = 0    
        bone_list = context.scene.keemap_bone_mapping_list
        bone_list.clear()
        
        KeeMap = bpy.context.scene.keemap_settings 
        filepath = bpy.path.abspath(KeeMap.bone_mapping_file)
        file = open(filepath, 'r')

        data = json.load(file)
        
        KeeMap.facial_capture = data['start_frame_to_apply']
        KeeMap.number_of_frames_to_apply = data['number_of_frames_to_apply']
        KeeMap.keyframe_every_n_frames = data['keyframe_every_n_frames']
        KeeMap.source_rig_name = data['source_rig_name']
        KeeMap.destination_rig_name = data['destination_rig_name']
        KeeMap.bone_mapping_file = data['bone_mapping_file']
        i = 0
        for p in data['bones']:
            bone_list.add()
            bone = bone_list[i]
            
            bone.name = p['name']
            bone.label = p['label']
            bone.description = p['description']
            bone.SourceBoneName = p['SourceBoneName']
            bone.DestinationBoneName = p['DestinationBoneName']
            bone.keyframe_this_bone = p['keyframe_this_bone']
            bone.CorrectionFactor.x = p['CorrectionFactorX']
            bone.CorrectionFactor.y = p['CorrectionFactorY']
            bone.CorrectionFactor.z = p['CorrectionFactorZ']
            bone.has_twist_bone = p['has_twist_bone']
            bone.TwistBoneName = p['TwistBoneName']
            bone.set_bone_position = p['set_bone_position']
            bone.set_bone_rotation = p['set_bone_rotation']
            bone.bone_rotation_application_axis = p['bone_rotation_application_axis']
            i = i + 1
        file.close()
        
        return{'FINISHED'}
     
class KEEMAP_LIST_OT_SaveToFile(bpy.types.Operator): 
    """Save Out Bone Mapping File""" 
    bl_idname = "wm.keemap_save_file" 
    bl_label = "Save Bone Mapping File" 

    def execute(self, context): 
        #context.scene.bone_mapping_list.clear() 
        KeeMap = bpy.context.scene.keemap_settings 
        filepath = bpy.path.abspath(KeeMap.bone_mapping_file)
        file = open(filepath, 'w+')
        
        rootParams = {
        "start_frame_to_apply":KeeMap.start_frame_to_apply,
        "number_of_frames_to_apply":KeeMap.number_of_frames_to_apply,
        "keyframe_every_n_frames":KeeMap.keyframe_every_n_frames,
        "source_rig_name":KeeMap.source_rig_name,
        "destination_rig_name":KeeMap.destination_rig_name,
        "bone_mapping_file":KeeMap.bone_mapping_file
        } 
        bone_list = context.scene.keemap_bone_mapping_list
        jsonbones = {}
        jsonbones['bones'] = []
        for bone in bone_list:
            jsonbones['bones'].append({
                'name': bone.name,
                'label': bone.label,
                'description': bone.description,
                'SourceBoneName': bone.SourceBoneName,
                'DestinationBoneName': bone.DestinationBoneName,
                'keyframe_this_bone': bone.keyframe_this_bone,
                'CorrectionFactorX': bone.CorrectionFactor.x,
                'CorrectionFactorY': bone.CorrectionFactor.y,
                'CorrectionFactorZ': bone.CorrectionFactor.z,
                'has_twist_bone': bone.has_twist_bone,
                'TwistBoneName': bone.TwistBoneName,
                'set_bone_position': bone.set_bone_position,
                'set_bone_rotation': bone.set_bone_rotation,
                'bone_rotation_application_axis': bone.bone_rotation_application_axis,
            })
        jsonbones.update(rootParams)
        print(jsonbones)
        json.dump(jsonbones, file)  
        file.close()
        return{'FINISHED'} 
    
	
	
def register():
    bpy.utils.register_class(KEEMAP_BONE_UL_List)
    bpy.utils.register_class(KEEMAP_LIST_OT_NewItem)
    bpy.utils.register_class(KEEMAP_LIST_OT_DeleteItem)
    bpy.utils.register_class(KEEMAP_LIST_OT_MoveItem)
    bpy.utils.register_class(KEEMAP_LIST_OT_ReadInFile)
    bpy.utils.register_class(KEEMAP_LIST_OT_SaveToFile)


def unregister():
    bpy.utils.unregister_class(KEEMAP_BONE_UL_List)
    bpy.utils.unregister_class(KEEMAP_LIST_OT_NewItem)
    bpy.utils.unregister_class(KEEMAP_LIST_OT_DeleteItem)
    bpy.utils.unregister_class(KEEMAP_LIST_OT_MoveItem)
    bpy.utils.unregister_class(KEEMAP_LIST_OT_ReadInFile)
    bpy.utils.unregister_class(KEEMAP_LIST_OT_SaveToFile)