# TIXEL: A Tiled Terrain Generator
#### Video Demo: https://www.youtube.com/watch?v=9l7Q7JIx7v4
#### Description:
Tixel is an isometric tiled terrain generator that allows the user to generate random terrains by inputting some parameters.

I am a fan of isometric view strategy games such as Final Fantasy Tactics Advanced or Tactics Arena Online and I got interested in terrain generation so I decided to combine both into my final project and create this isometric terrain generator.

At first, I considered simply doing an ASCII terrain generator by assigning ASCII characters to each terrain type but that was limitating the scope to 2D terrains and I really wanted to do isometric to give that sensation of depth while also wanted to add elevation (i.e. mountains) to the terrain. Thus, I decided to draw some simple isometric terrain tiles (that come as default in the "tiles" directory) and use them as prototypes.

I realized I needed a way to visualize the terrain and I decided to use pygame since is a library I was interested in learning.

The project folder contains two python files: tixel.py and main.py.
tixel.py is the file that contains all the class and function declarations while main.py contains the main loop to run the software. tixel.py contains 7 class declarations and 9 helper functions. Note that the tixel.py classes and functions are stand alone and can be imported and used independently without the need of an user interface.
#### Classes:
##### class Tile:
This class is used to represent a terrain tile. It stores a lot of information for each terrain tile such as its tile type, image, width, height, thickness or coordinates, between others.
The class also contains three methods: draw_tile, is_hovering and highlight that facilitate the representation of the terrain on the screen.
##### class Terrain:
This class is used to represent a terrain and is the heart of the project. Here, in this project, a terrain can be understood as a group of Tile instances and, in fact, one of the Terrain class attributes is a list of the Tile instances that make it. Some other important attributes of the Terrain class are:
 - The base_layer that represents the first layer of the terrain or ground.
 - The heightmap that represents the elevation at each terrain cell.
 - The terrain that is a list with each of the terrain layers containing the assigned tile type at each terrain cell.

This class contains three methods that are used to randomly generate the terrain.
 - Generate_base_layer: Creates a random seed that it is then used to generate the base layer of the terrain using user input tile probabilities.
 - Smooth_base_layer: Uses a nearest neighbor algorithm to smooth the random noise of the base layer. The algorithm basically looks at random cells in the terrain and changes their tile type to the most frequent tile type of their neighbors.
 - Generate elevation: Generates the elevation (mountains) of the terrain based on which tile type the user has selected as mountain tile and the maximum elevation that the user has chosen. The algorithm that it uses is also based on nearest neighbors but in this case, the elevation at each cell is set to the average elevation of all neighbor cells. Therefore the elevation is effectively eroded more and more with each iterations of the terrain through the algorithm.

 The rest of the methods are used to draw the terrain on the screen, update attributes values, handle user input events, and export the terrain in image or csv form.
##### classes Viewport, Button, InputBox and Checkbox:
These classes all represent different elements of the user interface or the viewport itself. They come with different attributes that contain dimensions, booleans to check if the element has been pressed or it is currently active, callback functions, and images to represent them on screen.
##### class TileInformation:
This class gathers tile information about all the available tile types (i.e. grass, wanter, sand, etc.) and stores it in several list and dictionary attributes. Additionally, if there is a viewport, it creates UI elements to allow the user to set the probability of each tile, choosing an elevation tile or changing all selected tiles to a certain tile type.
#### Usage:
Before running the main function, the user can choose to use their own isometric tile images instead of the default ones. To do so, the default images contained in the "tiles" directory should be simply subtituted with the tile images that the user wants to use. Note that the user can choose to use as many or as few tiles as they want since the TileInformation class will gather the image information for the new tiles and automatically update the UI buttons for them. Additionally, the user should update the size of the highlight.png image in "assets" directory to match the size of their tiles.

Once the main function runs, the user interface will be shown. Initially, the user interface will only have two regions.
On the top left, a region with a button per each available tile type is shown. Each tile type button has a checkbox on its left that allows the user to choose which tile type will be considered as elevation tile. This choice will be critical in the future when the user generates the elevation for the terrain. Additionally, each tile type button has an input box on their right titled "Tile Probability". Here, the user can input the desired probability of each tile type to appear when generating the base layer. If the probability of a tile type is set to 0, it will not appear in the base layer.
On the top right, several input boxes and a button that reads " Generate Terrain Base Layer" are shown. Here the user can input a terrain size (measured in tiles) and the width, height and thickness of the tiles in pixels. The values of tile width, height, and thickness that appear by default correspond to the values of the default tile set, but if the user wants to use a custom tile set, it will need to modify these values accordingly. Once the user has configured the parameters with their preferences, they can click in the button "Generate Terrain Base Layer" and a random terrain with only one layer will be generated and appear on screen.

Upon generating the base layer, two more buttons and two more input boxes will appear on the top right region of the viewport. The button "Smooth Terrain Base Layer" is used to smooth the noise of the base layer in order to get a more natural terrain. Once the user has smoothed the terrain to their liking, they can choose the maximum amount of elevation (in tiles) that they want by inputing the value in the "Elevation" input box and a number of iterations in the "Iterations" input box. These parameters, together with the elevation tile (choosen from the checkboxes on the top left), are used to generate the terrain elevation when the user click on the "Generate Terrain Elevation" button and greatly affect the final look of the generated mountains. The user should experiment with different values of elevation and iterations to achieve their desired look.

The user can edit tiles directly on the terrain by selecting the tiles and clicking of the tile type button (top left region) of the tile type they want that tile to change to. Note that before creating elevation, one can edit the base layer to have more or less elevation tiles and this will change the area where elevation will be generated giving more flexibility to the user. This feature can also be used to edit in decoration tiles, create rivers, shores, etc.

Finally on the top of the viewport, two buttons and an input box are used to export the terrain. The "Terrain Name" will be used to name the exported files. The "Generate Terrain Image" generates a PNG image of the terrain that it is saved in "my_terrains" directory. The "Export Terrain Data" creates a csv with the tile types at each position of each terrain elevation layer and the heightmap in "my_terrains" directory.
#### Controls:
Mouse:
 - Left-click: Select tile (can drag mouse while pressing left click to select multiple tiles).
               Click buttons, input boxes, checkboxes...
 - Scroll wheel: Zoom in and out of the terrain.
 - Right-click: Press right-click and drag mouse to pan around the terrain.
 - Hold left Ctrl + Left-click: Unselect a selected tile or if clicking outside the terrain, unselect all selected tiles.

Keyboard:
 - Write in input boxes.
 - Delete: Delete selected tile. Note tiles from the base layer cannot be deleted.
 - ESC: Exit
