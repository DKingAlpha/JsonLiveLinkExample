# JsonLiveLink Example

This is an example of using JsonLiveLink plugin to stream animation data from python to Unreal Engine.

Animation data contains an subject name, and its bones definition and bone parents definition, as well as the bone transforms data.


Json Data Format Sent to JsonLiveLink:
```json
{
    <SUBJECT_NAME>: [
        // bone#1
        {
            "Name": <BONE_NAME>,
            "Parent": <BONE_PARENT_INDEX>,   // -1 means no parent
            "Location": [<X>, <Y>, <Z>],
            "Rotation": [<X>, <Y>, <Z>, <W>],
            "Scale": [<X>, <Y>, <Z>]
        }
        // for bone in bones
    ]
}
```


## Setup

1. Install JsonLiveLink plugin to your project. (git clone JsonLiveLink)
2. Enable plugin JsonLiveLink & LiveLink, restart project to build plugin
3. In Unreal Editor - Window - Virtual Production - LiveLink, add source JSON LiveLink, Press OK.


## Requirements

`pip3 install matplotlib`


## Usage

1. In main.py, edit `bones, subject name, xlim, ylim`
2. Run main.py. When you drag the points, there should be a green light on Live Link Panel.
3. To preview: open SKMesh, in preview scene settings, set Preview Controller to LiveLink Preview Controller, set Subject Name to the one you just set in main.py.
4. To use it in your game: Create an AnimBP for your skeletal mesh, add LiveLinkPose node, select subject name in detail panel. Save AnimBP. Drag the SKMesh to scene, set AnimBP to the one you just created.

## Bones definition

To automatically setup bones and parents, this script provides a function to generate bones definition and parents definition from a bones dictionary.

Bones dictionary is in a natural format as below

`BoneNode = dict[str, BoneNode|str|list[str]]`

