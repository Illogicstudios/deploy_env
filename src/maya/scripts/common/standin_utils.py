import os
import re

try:
    import pymel.core as pm
except:
    # Maya not found
    pass

def parse_standin(standin):
    standin_trsf = standin.getParent()
    trsf_name = standin_trsf.name()
    object_name = trsf_name

    # standin name
    standin_file_path = standin.dso.get()
    if not re.match(r".*\.ass", standin_file_path):
        return {"valid": False, "object_name": object_name}
    standin_file_name_ext = os.path.basename(standin_file_path)
    standin_file_name = os.path.splitext(standin_file_name_ext)[0]
    standin_name = re.sub("_" + standin_file_name.split('_')[-1], '', standin_file_name)

    # active variant and version
    path_version_dir = os.path.dirname(standin_file_path)
    path_variant_dir = os.path.dirname(path_version_dir)
    publish_ass_dir = os.path.dirname(path_variant_dir)
    variant = os.path.basename(path_variant_dir)
    active_variant = variant.split('_')[-1]
    active_version = os.path.basename(path_version_dir)

    # variants and versions
    standin_versions = {}
    path_asset_dir = os.path.dirname(path_variant_dir)
    for variant in os.listdir(path_asset_dir):
        variant_dir = path_asset_dir + "/" + variant
        if os.path.isdir(variant_dir):
            standin_versions[variant.split('_')[-1]] = []
            for version in os.listdir(variant_dir):
                version_dir = variant_dir + "/" + version
                if os.path.isdir(version_dir):
                    standin_versions[variant.split('_')[-1]].append((version, version_dir))

    for variant in standin_versions.keys():
        standin_versions[variant] = sorted(standin_versions[variant], reverse=True)

    return {
        "valid": True,
        "object_name": object_name,
        "standin_name": standin_name,
        "publish_ass_dir": publish_ass_dir,
        "active_variant": active_variant,
        "active_version": active_version,
        "standin_versions": standin_versions,
    }