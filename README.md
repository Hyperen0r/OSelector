PS: If you want a better looking version, visit this **[LINK](https://hyperen0r.github.io/OSelector/)**

# OSelector

**OSelector** is a tool to automatically generate a poser plugin for **OSA**
based on a folder, whether it is your entire data/ folder, or a mod folder. With this
plugin, you can easily and quickly play a single animation from any mod,
from a simple navigation menu displayed through **OSA UI**.
Whether you want an navigation menu for a mod containing 10 animations or
14000 animations from your entire data/ folder, the menu will be automatically generated
 and splitted into differents folders with appropriate name when possible. However, if you want
a better menu, you can edit it by :

* reorganizing folders and entries with a drag&drop functionality and a few other actions
* editing names of folders and entries
* editing icons displayed by the menu

Animations that can be played are the ones which are registered using FNIS. The plugin
is just an xml file, which is read by OSA, so no esp slot is taken. It also means that any
animation mod author can pack his mod with the generated plugin.
It will be ignored for those who do not have OSA installed, but those who do
can easily and quickly preview their animations.

This plugin use the *MyAnimation* functionality from **OSA**:

Description of MyAnimation from **OSA**:  

> MyANIMATION: functions exactly the same as MyEquip except it plays animations. 
> It's a text data poser mod without the need for rings. You can group your animations into categories however you like. 
> They can play directly from the list on the player character or on a target. Note that MyAnim is different from the animation engine, 
> the animation engine has lots of empowered features for animated scene creators where as MyAnim functions like a poser mode
> where it simply plays single animations.  
[Nexus Link](https://www.nexusmods.com/skyrim/mods/76744/?tab=description&topic_id=5756447)

##### Preview of an automatically generated menu after scanning a folder
[![tool_overview.png](https://s15.postimg.cc/nxieacmcb/tool_overview.png)](https://postimg.cc/image/iyuvvtijb/)


## Dependencies

* Works on **Oldrim** and **SSE**
* **[OSA](https://www.nexusmods.com/skyrim/mods/76744/?tab=description&topic_id=5756447)**
* At least a mod containing animations using **FNIS**,
otherwise there is no use to launch the tool.


## Installation

### Tool
* **[Download the tool](https://github.com/Hyperen0r/OSelector/releases)**

You can run the tool anywhere. Also it generates two files in the same folder:

* a config file named **conf.ini**
* a log file named **logs.log**

If you delete the config file, a new one will be automatically generated with the default
settings. You can edit this file to better suit your needs. For more information on this,
please refer **[to the Configuration section](https://github.com/Hyperen0r/OSelector#configurations)**

As for the log file, you can delete without worries, as it will be overwritten/generated
everytime you launch the tool. If you do not need it you can disable it in the conf.ini file.


### Generated plugin

When launching the tool for the first time (or after erasing the conf.ini file), the tool will
ask you if you use **Mod Organizer**. If you do, you have to specify the _mods/_ folder
of **Mod Organizer**. If you do so, the plugin will be installed in the _mods/_ folder,
which means you just have to refresh the left pane of __Mod Organizer__ and activate the plugin.
For the next time, if you generate a plugin with the same name, you don't need to do anything,
since the plugin is already activated and the old file will be overwritten.

If you don't use **Mod Organizer**, you can specify the _data/_ folder of your installation. 
You won't have to do anything. As for using other mod manager, I'm not sure how they store
mods. One way is to archive the generated plugin and install it with your mod manager
of your choice.


## Updating

* Delete your **conf.ini** file
* Replace the old .exe with the new .exe.


## Uninstalling

* Delete the **.exe**, the **conf.ini** and the **logs.log** files
* Detele the mod folder generated by the plugin

## Basic usage

* First step is to specify the folder you wish to scan for animations *(usually data/ or mods/)*.
It will register every animation using **FNIS**. It will automatically build a menu for you,
with appropriate names and structure so you don't have to edit it during step 2, unless you
want to improve it.

* During second step, the menu will be displayed. It is represented by a tree structure.
That's how it will be organized in-game. Next, if you want to improve it, you can edit the
tree by changing names, reorganizing folders and entries and changing their icon.
To prevent the screen from being cluttered with entries, at generation each page is limited
to 25 items (configurable). It means that the tool will organize the tree in such a way
that an folder cannot have more than 25 entries. But if you edit it yourself with **Drag&Drop**
this rule is not applied (Meaning you can force a page to have more than 25 entries). 

* The third and final step is the plugin generation, where you just have to click on
**Generate Plugin** and specify the name of your plugin.

If you make no edit to the tree, this process should not take more than two minute,
depending on your hardware and the number of animations. For example, I have currently
~14 000 animations installed. With the tool, it took only 18 seconds from opening
to the plugin's generation.


## Other functionalities

* You can also edit existing plugin by loading them. After this, you can scan other folders or
even load other plugins to add them to the menu and merge them. 

* **Cleanup** button is removing folders with 0 child. If a folder has only
one child, the child replace the folder.



## Usage In-Game

To use the plugin, you must have **OSA** installed. Then press **Enter** on your numpad to
open **OSA UI**. Then go to __Inspect Self > Interact > Animate > [NAME OF YOUR PLUGIN]__. Depending of the
number of animations and your PC, it can take some time to load the plugin.


## For who is this tool ?

* Anyone who want to quickly want to make navigation menu for a mod containing animations
or for his entire data folder.

* Anyone who want to make a navigation menu with better names and organization or to tweak an 
existing one .Also everyone can share his file, if he did a menu with better names and
organization, like Morra's Poser Pack. But the user have to have the animations installed.
Or the user can load the shared plugin and remove the animations he does not have.

* Mod Authors can use the tool to generate a poser plugin for theirs animation mod and 
add it to the package. So when a user has OSA and the mod, he can easily cycle
through his animations, without using rings. 



## How many animations ?

The tool should be able to handle a very large amount of animations. Each mod have usually one
**FNIS** file, containing information about animations. Some have more than one **FNIS** file.
However if one file contains more than 8 750 animations (It's a lot, the most I have seen
is ~2 750 from Halo's mod), I cannot guarantee that the menu will be well splitted.

I've tested with roughly 14 000 animations from differents mods and everything seemed fine.



## Animation supported
  Normally all animations using FNIS should work out of the box. (The xml file is just
  exposing animation id to OSA engine)
  
  I could test only the following :
  
* Basic animation (Pose)
* Sequence animation (Animation with multiple stages) 
* AnimObj animation (Animation with objects)



## Configurations

Some settings (like the max number of items per page) can be changed by editing
the conf.ini file. If you do not see one, launch the tool once.
It will automatically generate a new one.

### [CONFIG]
*Used to display dialog box to initialize settings when using for the first time*

> **bfirsttime** = False or True

*Does not do anything for now, except displaying informations concerning the installation of the plugin*
> **busemodorganizer** = True 

*Name of the last generated plugin for ease of use and navigation
(Dialog Box use this to find the path of the last plugin, and as a placeholder for next dialog name)*
> **lastname** = OSelector

### [PLUGIN]

*Default name for the plugin, if there is no last name*
>**name** = OSelector

*Default icon for package folders, which is the same as the mod folder*
>**defaultpackageicon** = omu_skyrim

*Default icon for folders*
>**defaultfoldericon** = omu_stickarmships

*Default icon for set folder*
>**defaultseticon** = omu_stickarmships

*Default icon for animation entries*
>**defaultanimationicon** = omu_sticktpose

*Max number of child per folder*
>**maxitemperpage** = 25

*Max string length for displayed names*
>**maxitemstringlength** = 25

### [PATHS]

*Default location for installing the generated plugin*
>**installfolder** = D:/Modding/Mod Organizer/Mod Organizer/mods

*__DO NOT CHANGE__, unless you know what you are doing*
>**pluginfolder** = meshes/0SA/_MyOSA/anim_1/

*__DO NOT CHANGE__, unless you know what you are doing (Currently not used)*
>**plugininstall** = meshes/0SA/mod/__install/plugin/

### [LOG]

*Explicit*
>**enabled** = True

*Print logs only if it is at least the specified level*
>**level** = DEBUG or INFO or WARNING or ERROR or CRITICAL


## Tools used

* IDE : [PyCharm Community Edition](https://www.jetbrains.com/pycharm/download/#section=windows)
* Python : 3.6 (PyInstaller does not support 3.7 for now)
* Libraries : PyQt (for the GUI) and PyInstaller (for the executable)



## FAQ

##### Q: There is bug ! / I have some ideas for improving/fixing the tool
**A:** If you want to report an issue or feature request, feel free to open a ticket through github.
To do so, go to **[ISSUES](https://github.com/Hyperen0r/OSelector/issues)**, click on _**New Issue**_
and chose one of the templates. 


##### Q: Would there be any benefit to using this over the Morra's Poser Pack?
**A:** Morra's poser pack is a very good poser plugin, with a great number of animations
and a very good menu. In fact, this kind of plugin is in some way the end goal of the tool.
However, you may find that some mods have been updated. Unless Morra
updates his plugin, you will be missing animations. That were the tool comes in handy, since
you can easily scan the mod folder and register all animations from it. If you wish to
keep Morra's menu but also adding animations from updated mods, you can do so by following
this procedure:

* Open PoserModule.xml (from Morra's Poser Pack)
* Delete the third three lines :
```
<global id="PoserModule"/>
<folderstyle fc="FFFFFF" h="h_bigdot_op" th="1.5" b="" lc="FFFFFF" h="!" sh="sq" sth="3" sb="000000" slc="!"/>
<entrystyle fc="FFFFFF" h="h_bigdot_op" th="1.5" b="" lc="FFFFFF" h="!" sh="ci" sth="3" sb="e86570" slc="FFFFFF"/>	
```
* Rename the file "PoserModule.myo"
* Launch the tool
* Load the file "PoserModule.myo"
* Then scan any folder you want, like one of the updated mod
* When asked, choose __"Append"__, and __"Yes"__ (to ignore already existing animations, so you don't have duplicates)
* New animations will be added, now you can merge the new ones with Morra's Poser pack.
* If there are empty folders (like a "Set X" without child), click multiple times on the
__"Cleanup"__ button, until there is no more.
* Once finished, clicked __"Generate Plugin"__
* Since a new plugin is generated, you should deactivate Morra's Poser Pack

##### Q: Why are some names weird ?
**A:** The Tool is supposed to handle all kind of animations using FNIS. But not every modders
follow the same naming guidelines. So to be the most accurate the tool is dependant of
the three following names:

* Package name (name of the mod)
* Module name (name of the FNIS file, for example for "FNIS_3ijou_List.txt", it will be "3ijou" )
* Animation name (More exactly name of the stage, like "EXT16")

These names are used to build the navigation menu.
There is some tweak applied to each of them to be more readable and understandable,
but this a functionality I want to improve.

Also, some names are very long which overlap with other entries from OSA UI. To prevent this,
each string is limited to 25 characters (also configurable)

And last thing, the tree is automatically cleaned up of every folder containing zero child,
or only one child (the child replace his parent). For now I haven't found a way to guess
which name is better (the child or the parent ?).

##### Q: I'm afraid to use an executable/ My anti-virus blocked your file
**A:** I had no problem with my antivirus (Avira), and the exe was clean on Virus Total. 
If you are suspicious, you can do the following:

* Check with **[Virus Total](https://www.virustotal.com/#/home/upload)**
* Check the source. **[Github link](https://github.com/Hyperen0r/OSelector)**
* Execute directly from source. In that case, please refer to **[Tools Used](##Tools-Used)**
to help you setup your environment.

## Known Bug

 - [ ] Menu entry is duplicated. Sometimes after closing and reopening, all menu entries are
 duplicated (even the one not generated with the tool)
 

## Thanks

* Thanks to CE0 and the OSA Team for this awesome engine/framework
