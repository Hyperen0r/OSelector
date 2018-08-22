PS: If you want a better looking version, visit this **[LINK](https://hyperen0r.github.io/OSelector/)**

# OSelector

**OSelector** is a tool to automatically generate a poser plugin for **OSA**
based on a folder, whether it is your entire data/ folder, or a mod folder. With this
plugin, OSA UI will be able to display a navigation menu, allowing you to play single
animation. With this tool, you can easily and quickly play an animation from any mod,
with a simple navigation menu. Whether you want an navigation menu for a folder
containing 10 animations or 14000 animations from your entire data/, 
the menu will be automatically splitted into differents folder with appropriate name
if possible. However, if you want a better menu, you can edit the menu by :

* reorganizing folders and entries with a drag&drop functionality and a few other actions
* editing names of the folder and entries
* editing icon displayed by the menu

Animations that can be played are the ones which are registered using FNIS. The plugin
is just an xml file, which is read by OSA, so no esp taken. It also means that any
animation mod author can pack with his mod the generated plugin.
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



## How does it works ?

There is three major step :

* First step is to scan the folder of your choice *(usually data/ or mods/)*.
It will register every animation using **FNIS**

* During second step, a tree structure will be displayed. It represents the navigation menu
you will see in game. You can make some edit to it, change name and modify the organization.
To prevent the screen from being cluttered with entries, each page is limited to 25 items (configurable)
at generation. It means that the tool will organize the tree in such a way that no more
than 25 items are displayed. But if you edit it yourself, this rule is not applied
(Meaning you can force a page to have more than 25 entries). 

* The third and final step is the plugin generation, where you specify the
name of your plugin.

If you use Mod Organizer, the plugin should be installed in your mods folder. Then you just have to
activate it in Mod Organizer.

You can also load existing plugin and tweak it.



## Usage In-Game

To use the plugin, you must have **OSA** installed. Then press **Enter** on your numpad to
open **OSA UI**. Then go to __Inspect Self > Interact > Animate > [NAME OF YOUR PLUGIN]__. Depending of the
number of animations and your PC, it can take some time to load the plugin.


## For who is this tool ?

Anyone who want to make an easy navigation menu for a mod containing animations
or for his entire data folder.

Anyone who want to make a navigation menu with better names and organization or to tweak an 
existing one

* Mod Users can just launch the tool to have a menu for every or some animations. Everyone 
can share his file, if he did some edit (better names and organization, like Morra's Poser Pack).

* Mod Author can add this file to their mod, so when a user has OSA and his mods, he can easily
cycle through his animations. 



## How many animations ?

The tool should be able to handle a very large amount of animations. Each mod have usually one
**FNIS** file, containing information about animations. Some have more than one **FNIS** file.
However if one file contains more than 8 750 animations (It's a lot, the most I have seen
is ~2 750 from Halo's mod), I cannot guarantee anything.

I've tested with roughly 14 000 animations and everything seemed fine.



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



## Tools used

* IDE : [PyCharm Community Edition](https://www.jetbrains.com/pycharm/download/#section=windows)
* Python : 3.6 (PyInstaller does not support 3.7 for now)
* Libraries : PyQt (for the GUI) and PyInstaller (for the executable)



## FAQ

##### Q: There is bug ! / I have some ideas for improving/fixing the tool
**A** If you want to report an issue or feature request, feel free to open a ticket through github.
To do so, go to **[ISSUES](https://github.com/Hyperen0r/OSelector/issues)**, click on _**New Issue**_
and chose one of the templates. 

##### Q: Why some names are so weird ?
**A:** The Tool is supposed to handle all kind of animations using FNIS. But not every modder follow
the same naming guidelines. So the tool is dependant of the three following names:

* Package name (name of the mod)
* Module name (name of the FNIS file, for example for "FNIS_3ijou_List.txt", it will be "3ijou" )
* Animation name (More exactly name of the stage, like "EXT16")

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
