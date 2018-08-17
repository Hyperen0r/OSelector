import re
from enum import Enum

class Animation:

    class TYPE(Enum):
        BASIC = "^(b)"
        ANIM_OBJ = "^(fu|fuo|o)"
        SEQUENCE = "^(s|so)"
        ADDITIVE = "^(\+)"
        OFFSET = "^(ofa)"
        PAIRED = "^(pa)"
        KILLMOVE = "^(km)"
        UNKNOWN = ""

    class OPTION(Enum):
        ACYCLIC = "(?:,|-)a"
        ANIM_OBJ = "(?:,|-)o"
        TRANSITION = "(?:,|-)Tn"
        HEAD_TRACKING = "(?:,|-)h"
        BLEND_TIME = "(?:,|-)(B\d*\.\d*)"
        KNOWN = "(?:,|-)k"
        BSA = "(?:,|-)bsa"
        STICKY_AO = "(?:,|-)st"
        DURATION = '(?:,|-)(D\d*\.\d*)'
        TRIGGER = "(?:,|-)(T[^\/]*\/\d*\.\d*)"
        NONE = ""

    def __init__(self, _type=TYPE.UNKNOWN, options=[], animId="", animFile="", animObj=""):
        self.stages = []
        self.stages_file = []
        self.stages_obj = []

        self.type = _type
        self.options = options
        self.stages.append(animId)
        self.stages_file.append(animFile)
        self.stages_obj.append(animObj)

        self.name = self.stages[0].rsplit("_", 2)[0]

    def addStage(self, animId, animFile, animObj):
        self.stages.append(animId)
        self.stages_file.append(animFile)
        self.stages_obj.append(animObj)

    @staticmethod
    def parseLine(line):
        # See FNIS_FNISBase_List.txt for more information (in FNIS Behavior <Version>/Meshes/Character/animations/FNISBase
        regexp = re.compile(r"^(\S*)(?: -(\S*))? (\S*) (\S*)((?:\s(?:\S*))*)")
        found = regexp.search(line)
        if found:
            type = found.group(1)  # Single word (s + b ...)
            options = found.group(2)  # o,a,Tn,B.2, ...
            animId = found.group(3)  # ANIM_ID_ ...
            animFile = found.group(4)  # <path/to/file>.hkx
            animObj = found.group(5)  # Chair Ball ...
            return Animation.getAnimTypeFromString(type), Animation.getOptionsFromString(
                options), animId, animFile, animObj
        return Animation.TYPE.UNKNOWN, [], "", "", ""

    @staticmethod
    def getAnimTypeFromString(string):
        for animType in Animation.TYPE:
            regexp = re.compile(animType.value)
            found = regexp.search(string)
            if found:
                return animType
        return Animation.TYPE.UNKNOWN

    @staticmethod
    def getOptionsFromString(string):
        if string:
            options = []
            for animOptions in Animation.OPTION:
                regexp = re.compile(animOptions.value)
                found = regexp.search(string)
                if found:
                    options.append(animOptions)
        return [Animation.OPTION.NONE]

