# OSelector

**OSelector** is a tool to generate a poser plugin for **OSA**. You can easily generate
a plugin for any mod you have installed, allowing you to test every animation using **FNIS**
through **OSA UI**.
The plugin is an xml file using the *MyAnimation* functionality.

Description of MyAnimation from **OSA**:  

> MyANIMATION: functions exactly the same as MyEquip except it plays animations. 
> It's a text data poser mod without the need for rings. You can group your animations into categories however you like. 
> They can play directly from the list on the player character or on a target. Note that MyAnim is different from the animation engine, 
> the animation engine has lots of empowered features for animated scene creators where as MyAnim functions like a poser mode
> where it simply plays single animations.  
[Nexus Link](https://www.nexusmods.com/skyrim/mods/76744/?tab=description&topic_id=5756447)

If you use OSA, you surely have seen the plugin made by Morra
(Available on LL : Morra's Poser Pack). This tool does not replace it. Morra put time and effort
to make a clean navigation menu, which this tool struggle to make out of the box. However, this tool should
make the process more easy and quick.

*NOTE: This does not take an esp slot. It is just one xml file read by OSA*

![Tool Overview](ressources/tool_overview.png)

## How does it works ?

* First step is to scan the folder of your choice (usually data/ or mods/).
It will register every animation using **FNIS**

* During second step, a tree structure will be displayed. It represents the navigation menu
you will see in game. You can make some edit, changing name and modifying the organization (limited functionality for now).
To prevent the screen from being cluttered with entries, each page is limited to 25 items at generation.
It means that the tool will organize the treein such a way that no more than 25 items are displayed.
But if you edit it yourself, this rule is not applied (Meaning you can force a page to have more than 25 entries). 

* The third and final step is the plugin generation, where you just have to click a button.

If you use Mod Organizer, the plugin should be installed in your mods folder. Then you just have to
activate it in Mod Organizer. 



## For who is this tool ?

Anyone who want to make an easy navigation menu for a mod containing animations.
Anyone who want to make to tweak a navigation menu with better names and organization.

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

Some settings (like the max number of items per page) can be changed by editing the conf.ini file. If you do not see one, launch the tool once.
It will automatically generate a new one.



## FAQ



## Known Bug

 - [ ] Menu entry is duplicated. Sometimes after closing and reopening, all menu entries are
 duplicated (even the one not generated with the tool)
