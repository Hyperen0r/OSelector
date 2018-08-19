# OSelector

**OSelector** is a tool to generate a poser plugin for **OSA**. You can easily generate a plugin for any mod you have installed,
allowing you to test every animation using **FNIS**. The plugin is an xml file which is read by **OSA** and by
using the *MyAnimation* functionality, you can play animation from OSA UI :  

Description of MyAnimation from **OSA**:  

> MyANIMATION: functions exactly the same as MyEquip except it plays animations. 
> It's a text data poser mod without the need for rings. You can group your animations into categories however you like. 
> They can play directly from the list on the player character or on a target. Note that MyAnim is different from the animation engine, 
> the animation engine has lots of empowered features for animated scene creators where as MyAnim functions like a poser mode
> where it simply plays single animations.  
[Nexus Link](https://www.nexusmods.com/skyrim/mods/76744/?tab=description&topic_id=5756447)

If you use OSA, you surely have seen the plugin made by Morra (Available on LL : Morra's Poser Pack)

## How does it works ?

* First step is to scan the folder of your choice (usually data/ or mods/). It will register every animation usign **FNIS**

* During second step, a tree structure will be displayed. It represents the navigation menu you will see in game. You can
make some edit(change name, modify the structure (limited functionalities for now)). To prevent the screen from being cluttered with
**OSA UI**, each page are limited to 25 items. It means that the tool will organize the tree in such a way that no more than 25 items are displayed.

* The third and final step is the plugin generation, where you just have to click a button.



## Animation supported
  Animations can be applied only to the player. For animations with multiple actors, no npc will join,
  only the animation for the specified actor will be played.
  
* Basic animation (Pose)
* Sequence animation (Animation with multiple stages) 
* AnimObj animation (Animation with objects)


## Configurations

Some settings (like the max number of items per page) can be changed by editing the conf.ini file. If you do not see one, launch the tool once.
It will automaticaly generate a new one.
