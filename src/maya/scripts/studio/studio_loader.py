import os
import pymel.core as pm


def run():
    studio_filepath = (os.path.dirname(__file__) + "/assets/studio.mb").replace("\\","/")
    # Find existing and remove reference if found
    for ref in pm.listReferences():
        if ref == studio_filepath:
            ref.remove()
            return
    # If studio not existing create reference
    pm.createReference(studio_filepath)
