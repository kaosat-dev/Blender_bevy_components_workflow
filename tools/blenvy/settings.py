import json
import bpy

def upsert_settings(name, data, overwrite=False):
    stored_settings = bpy.data.texts[name] if name in bpy.data.texts else None
    if stored_settings is None:
        stored_settings = bpy.data.texts.new(name)
        stored_settings.write(json.dumps(data))
    else:
        if overwrite:
            stored_settings.clear()  
            stored_settings.write(json.dumps(data))
        else:
            current_settings = json.loads(stored_settings.as_string())
            stored_settings.clear()
            current_settings = {**current_settings, **data}
            stored_settings.write(json.dumps(current_settings))

def load_settings(name):
    stored_settings = bpy.data.texts[name] if name in bpy.data.texts else None
    if stored_settings is not None:
        try:
            return json.loads(stored_settings.as_string())
        except:
            return None
    return None


# given the input (actual) settings, filters out any invalid/useless params & params that are equal to defaults
def generate_complete_settings_dict(settings, presets, ignore_list=[], preset_defaults=True):
    complete_preferences = {}    
    defaults = {}

    def filter_out(pair):
        key, value = pair
        if key in ignore_list:
            return False
        return True

    for k in presets.__annotations__:
        item = presets.__annotations__[k]
        default = item.keywords.get('default', None)
        if default is not None:
            defaults[k] = default
            if preset_defaults:
                complete_preferences[k] = default
    #print("defaults", defaults)
    

    for key in list(settings.keys()):
        if key in defaults and settings[key] != defaults[key]: # only write out values different from defaults
            value = getattr(settings, key, None) # this is needed for most of our settings (PropertyGroups)
            if value is None:
                value = settings[key] # and this for ...gltf settings
            complete_preferences[key] = value
            #print("setting", key, value, settings[key], settings)

    
    complete_preferences = dict(filter(filter_out, dict(complete_preferences).items()))

    return complete_preferences


# checks if old & new settings (dicts really) are identical
def are_settings_identical(old, new, white_list=None):
    if old is None and new is None:
        return True
    if old is None and new is not None:
        return False
    if old is not None and new is None:
        return False
    
    old_items = sorted(old.items())
    new_items = sorted(new.items())

    if white_list is not None:
        old_items_override = {}
        new_items_override = {}
        for key in white_list:
            if key in old:
                old_items_override[key] = old[key]
            if key in new:
                new_items_override[key] = new[key]
        old_items = sorted(old_items_override.items())
        new_items = sorted(new_items_override.items())

    return old_items == new_items


# if one of the changed settings is not in the white list, it gets discarded
def changed_settings(old, new, white_list=[]):
    if old is None and new is None:
        return []
    if old is None and new is not None:
        return new.keys()
    if old is not None and new is None:
        return []
    
    old_items = sorted(old.items())
    new_items = sorted(new.items())

    result  = []
    old_keys = list(old.keys())
    new_keys =list(new.keys())
    added =  list(set(new_keys) - set(old_keys))
    removed =  list(set(old_keys) - set(new_keys))

    result += added 
    result += removed
    for key in new.keys():
        if key in old:
            if new[key] != old[key]:
                result.append(key)

    

    return [key for key in list(set(result)) if key in white_list]
