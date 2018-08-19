import re
from util.Config import get_config
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

    def __init__(self, package="", module="", _type=TYPE.UNKNOWN, options=None, animId="", animFile="", animObj=""):
        if not options:
            options = []

        self.package = package
        self.module = module
        self.type = _type
        self.options = options

        self.stages = []
        self.stages_file = []
        self.stages_obj = []

        self.stages.append(animId)
        self.stages_file.append(animFile)
        self.stages_obj.append(animObj)

    def add_stage(self, animId, animFile, animObj):
        self.stages.append(animId)
        self.stages_file.append(animFile)
        self.stages_obj.append(animObj)

    def parse_name(self):
        return self.stages[0].rsplit("_", 2)[0][slice(0, get_config().getint("PLUGIN", "maxItemStringLength"))]

    def parse_stage_name(self, index=0):
        # TODO Improve naming for stages
        return self.stages[index][slice(-get_config().getint("PLUGIN", "maxItemStringLength"), None)]

    @staticmethod
    def parse_line(line):
        # See FNIS_FNISBase_List.txt for more information (in FNIS Behavior folder)
        regexp = re.compile(r"^(\S*)(?: -(\S*))? (\S*) (\S*)((?:\s(?:\S*))*)")
        found = regexp.search(line)
        if found:
            anim_type = found.group(1)  # Single word (s + b ...)
            anim_options = found.group(2)  # o,a,Tn,B.2, ...
            anim_id = found.group(3)  # ANIM_ID_ ...
            anim_file = found.group(4)  # <path/to/file>.hkx
            anim_obj = found.group(5)  # Chair Ball ...
            return Animation.get_anim_type_from_string(anim_type), Animation.get_options_from_string(
                anim_options), anim_id, anim_file, anim_obj
        return Animation.TYPE.UNKNOWN, [], "", "", ""

    @staticmethod
    def get_anim_type_from_string(string):
        for animType in Animation.TYPE:
            regexp = re.compile(animType.value)
            found = regexp.search(string)
            if found:
                return animType
        return Animation.TYPE.UNKNOWN

    @staticmethod
    def get_options_from_string(string):
        if string:
            options = []
            for animOptions in Animation.OPTION:
                regexp = re.compile(animOptions.value)
                found = regexp.search(string)
                if found:
                    options.append(animOptions)
        return [Animation.OPTION.NONE]