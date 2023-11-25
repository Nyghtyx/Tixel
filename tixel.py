import os
import numpy as np
import random
import pygame

class Tile:
    """A Tile class used to represent a terrain tile.

    Attributes:
        tile_type (str): The type of the tile.
        image: The image of the tile.
        width (int): The width of the tile in pixels.
        height (int): The height of the tile in pixels.
        thickness (int): The thickness of the tile in pixels.
        coordinates (tuple): The isometric coordinates of the tile. Initialized to (0, 0).
        index (tuple): The index of the tile within the terrain matrix. Initialized to (0, 0).
        elevation (int): The elevation of the tile.
        mask: Pygame mask to detect click events.
        rect: Pygame rect to detect click events.
        scaled_image: Modified tile image to account for changes in the screen zoom.
        scaled_coordinates (tuple): Modified tile coordinates to account for changes in the screen zoom and panning.
        selected_tile (bool): True if the tile is currently selected and False otherwise.

    Methods:
        draw_tile: Draws the tile to the given screen and highlights it if it is selected.
        is_hovering: Checks if the mouse is hovering over the tile and returns True if it is.
        highlight: Highlights the tile with a semi-transparent shade.
    """

    def __init__(self, tile_type: str, path_to_image: str, width: int, height: int, thickness: int):
        """Initialize a Tile instance

        Args:
            tile_type (str): The type of the tile.
            path_to_image (str): The path to the image file for the tile.
            width (int): The width of the tile.
            height (int): The height of the tile.
            thickness (int): The thickness of the tile.
        """
        self.tile_type = tile_type
        self.image = pygame.image.load(path_to_image).convert_alpha()
        self.width = width
        self.height = height
        self.thickness = thickness
        self.coordinates = (0, 0)
        self.index = (0, 0)
        self.elevation = 1
        self.mask = None
        self.rect = None
        self.scaled_image = self.image
        self.scaled_coordinates = self.coordinates
        self.selected_tile = False

    def draw_tile(self, screen, zoom_factor: float, offset: list, coordinates: tuple = None):
        """Draw the tile on the screen and highlight it if it is selected.

        Args:
            screen: The pygame surface to draw the tile on.
            zoom_factor (float): The zoom factor for scaling the tile when zooming.
            offset (list): The panning offset as (x, y) coordinates.
            coordinates (tuple, optional): The coordinates where the tile should be drawn.
        """
        if coordinates is None:
            coordinates = self.coordinates

        # Scale image with zoom factor
        self.scaled_image = pygame.transform.scale(self.image,
                                                   (int(self.width * zoom_factor),
                                                    int(self.height * 2 * zoom_factor)))

        # Adjust coordinates to account for zoom_factor, panning and start centered on the screen
        self.scaled_coordinates = (coordinates[0] * zoom_factor + offset[0] + pygame.display.Info().current_w / 2,
                                   coordinates[1] * zoom_factor + offset[1] + pygame.display.Info().current_h / 4)

        # Draw the tile to the screen
        screen.blit(self.scaled_image, self.scaled_coordinates)

        # If the tile is selected, draw a highlight.
        if self.selected_tile:
            self.highlight(screen, zoom_factor, 200)

    def is_hovering(self, mouse_pos: tuple):
        """Check if the mouse is hovering over the tile.

        Args:
            mouse_pos (tuple): The current mouse position.

        Returns:
            bool: True if the mouse is hovering over the tile, False otherwise.
        """
        # Create a mask
        self.mask = pygame.mask.from_surface(self.scaled_image)

        # Create a rectangle
        self.rect = self.scaled_image.get_rect(topleft=self.scaled_coordinates)

        # Get relative position of the mouse with respect to the mask
        mask_pos = mouse_pos[0] - self.rect.x, mouse_pos[1] - self.rect.y

        # Return True if the mouse is within the mask
        return self.rect.collidepoint(mouse_pos) and self.mask.get_at(mask_pos)

    def highlight(self, screen, zoom_factor: float, alpha: int = 64):
        """Highlight the tile with a semi-transparent shade.

        Args:
            screen: The pygame surface to draw the highlight on.
            zoom_factor (float): The zoom factor used to scale the highlight when zooming.
            alpha (int, optional): The transparency of the highlight (0-255).
        """
        # Load highlight image (should be a tile of same dimensions as the terrain tiles)
        highlight_surface = pygame.image.load("assets/highlight.png").convert_alpha()
        # Set the alpha and scale the image
        highlight_surface.set_alpha(alpha)
        highlight_surface = pygame.transform.scale(highlight_surface,
                                                   (int(self.width * zoom_factor),
                                                    int(self.height * 2 * zoom_factor)))
        # Draw the highlight on the given screen at the current tile location
        screen.blit(highlight_surface, self.scaled_coordinates)


class Terrain:
    """A class used to represent a terrain with tiles, elevation, and operations on the terrain.

    Attributes:
        terrain_width (int): Width of the terrain in tiles.
        terrain_height (int): Height of the terrain in tiles.
        tile_width (int): Width of an individual tile in pixels.
        tile_height (int): Height of an individual tile in pixels.
        tile_thickness (int): Thickness of an individual tile in pixels.
        elevation_symbol (str): Symbol representing the tile type used for elevation.
        elevation (int): Maximum elevation in the terrain.
        elevation_iterations(int): Number of iterations performed to generate the elevation.
        tiles (list)L List of Tile objects representing all the terrain tiles.
        selected_tiles (lit): List of selected Tile objects.
        pointed_tile (Tile): The Tile object that is currently being pointed by the mouse.
        zoom_factor (float): The zoom factor for scaling the terrain when zooming.
        offset (list): The panning offset as (x, y) coordinates.
        base_layer (Numpy array): A Numpy array representing the base layer of the terrain.
        heightmap (Numpy array): A Numpy array representing the elevation map of the terrain.
        terrain (list[Numpy arrays]): List of Numpy arrays, each representing a terrain layer.

    Methods:
        generate_base_layer: Generate the base layer of the terrain based on tile probabilities.
        smooth_base_layer: Smooth the base layer to create a more natural terrain.
        generate_elevation: Generate terrain elevation based on the base layer.
        generate_tiles: Generate a list of Tile objects to represent the terrain.
        update_pointed_tile: Update the Tile being currently pointed by the mouse.
        update_zoom: Update the zoom factor of the terrain based on mouse wheel events.
        update_terrain_info: Update terrain parameters.
        update_selected_tiles: Update the list of selected tiles.
        change_selected_tile_type: Change the tile type of selected tiles.
        delete_tiles: Delete selected tiles. Note that base_layer tiles cannot be deleted.
        handle_events: Groups event-related methods.
        draw: Draw the terrain on the given screen.
        export_image: Export the current terrain as a PNG image.
        export_terrain_data: Export terrain data into a csv file.
    """
    def __init__(self, terrain_width: int, terrain_height: int, tile_width: int, tile_height: int, tile_thickness: int):
        """Initialize Terrain instance

        Args:
            terrain_width (int): The width of the terrain in tiles.
            terrain_height (int): The height of the terrain in tiles.
            tile_width (int): THe width of an individual tile.
            tile_height (int): The height of an individual tile.
            tile_thickness (int): The thickness of an individual tile.
        """
        self.terrain_width = terrain_width
        self.terrain_height = terrain_height
        self.tile_width = tile_width
        self.tile_height = tile_height
        self.tile_thickness = tile_thickness
        self.elevation_symbol = None
        self.elevation = 1
        self.elevation_iterations = 1
        self.tiles = []
        self.selected_tiles = []
        self.pointed_tile = None
        self.zoom_factor = 1
        self.offset = [0, 0]
        self.base_layer = np.full((self.terrain_width, self.terrain_height), fill_value="0", dtype=object)
        self.heightmap = None
        self.terrain = []

    def generate_base_layer(self, tile_probabilities: dict, tile_images: dict):
        """Generate the base layer of the terrain based on tile probabilities.

        Uses helper functions _generate_seed, _accumulate_probabilities, _assign_tile.

        Args:
            tile_probabilities (dict): Dictionary with tile types as keys and tile type probabilities as values.
            tile_images (dict): Dictionary with tile types as keys and path to the respective tile image as values.
        """
        # If any of the given terrain side values are negative, do nothing.
        if self.terrain_height < 0 or self.terrain_width < 0:
            return

        # Generate a seed
        seed = _generate_seed(self.terrain_height, self.terrain_width)

        # Generate accumulated probabilities of tiles
        accumulated_probabilities = _accumulate_probabilities(tile_probabilities)

        # Create an empty array to fill with tile type according to the seed
        self.base_layer = np.empty((self.terrain_width, self.terrain_height), dtype=object)

        # Iterate over the empty array and assign tiles
        for i in range(self.terrain_width):
            for j in range(self.terrain_height):
                self.base_layer[i, j] = _assign_tile(seed[i, j], accumulated_probabilities)
                # If _assign_tile returns None (can happen if probabilities do not sum up to 1),
                # fill with most probable tile type.
                if self.base_layer[i, j] is None:
                    most_probable_tile_type = "1"
                    for key, value in tile_probabilities.items():
                        if tile_probabilities[key] > tile_probabilities[most_probable_tile_type]:
                            most_probable_tile_type = key
                    self.base_layer[i, j] = most_probable_tile_type
        self.terrain = [self.base_layer]
        self.generate_tiles(tile_images)

    def smooth_base_layer(self, tile_types: list, tile_images: dict):
        """Smooth the base layer to create a more natural terrain.

        Uses helper functions _generate_unchecked_tiles, _get_neighbor_tiles, _set_to_neighbor_type.

        Args:
            tile_types (list): List with possible tile types.
            tile_images (dict): Dictionary with tile types as keys and path to the respective tile image as values.
        """
        # If a terrain does not exist yet, do nothing.
        if not self.tiles:
            return

        # If one of the terrain sides has size 1, do nothing.
        # Sides > 1 are necessary for nearest-neighbor calculations.
        elif self.terrain_width == 1 or self.terrain_height == 1:
            return

        # Get an unordered list of tile coordinates
        unchecked_tiles = _generate_unchecked_tiles(self.base_layer)

        # Iterate over the list of tile coordinates
        for coordinates in unchecked_tiles:
            i, j = coordinates
            # Look at the tile type of the neighbor tiles
            neighbors = _get_neighbor_tiles(self.base_layer, coordinates)
            # Set the tile type based on the tile types of the neighbor tiles
            self.base_layer[i, j] = _set_to_neighbor_type(neighbors, tile_types)

        self.terrain = [self.base_layer]
        self.generate_tiles(tile_images)

    def generate_elevation(self, tile_images: dict):
        """Generate terrain elevation based on the base layer.

        Uses helper functions _generate_heightmap.

        Args:
            tile_images (dict): Dictionary with tile types as keys and path to the respective tile image as values.
        """
        # If a terrain does not exist, do nothing.
        if not self.tiles:
            return
        # If an elevation tile type has not been chosen yet, do nothing.
        elif self.elevation_symbol is None:
            return
        # If one of the terrain sides has size 1, do nothing.
        # Sides > 1 are necessary for nearest-neighbor calculations used in _generate_heightmap.
        elif self.terrain_width == 1 or self.terrain_height == 1:
            return
        # If elevation or the number of iterations are negative, do nothing.
        elif self.elevation <= 0 or self.elevation_iterations < 0:
            return

        # Leave only the base layer tiles in the list of terrain tiles.
        for tile in self.tiles:
            if tile.elevation > 1:
                self.tiles.remove(tile)
        # Remove every layer from the terrain except the base layer.
        self.terrain = [self.terrain[0]]

        # Generate a heightmap.
        self.heightmap = _generate_heightmap(self.base_layer, self.elevation_symbol,
                                             self.elevation, self.elevation_iterations)

        # Set the elevation to the actual maximum vale in the heightmap.
        self.elevation = int(np.max(self.heightmap))

        # Iterate to generate the elevation terrain layers.
        for i in range(self.elevation):
            layer = np.empty((self.terrain_width, self.terrain_height), dtype=object)
            for j in range(self.terrain_width):
                for k in range(self.terrain_height):
                    if self.heightmap[j, k] > i:
                        layer[j, k] = self.elevation_symbol
                    else:
                        layer[j, k] = "0"
            self.terrain.append(layer)

        self.generate_tiles(tile_images)

    def generate_tiles(self, tile_images: dict):
        """Generate a list of Tile objects to represent the terrain.

        Uses helper functions _cart_to_iso.

        Args:
            tile_images (dict): Dictionary with tile types as keys and path to the respective tile image as values.
        """
        # Clear the tile list and selected tiles list
        self.tiles.clear()
        self.selected_tiles.clear()

        elevation_offset = 0
        # Iterate over the terrain and create a Tile instance for each position.
        for i in range(len(self.terrain)):
            for j in range(self.terrain_width):
                for k in range(self.terrain_height):
                    # Get the tile type of this cell
                    tile_type = self.terrain[i][j, k]
                    if tile_type == "0":
                        continue

                    # Create a tile class instance
                    tile = Tile(tile_type, tile_images[tile_type],
                                self.tile_width, self.tile_height, self.tile_thickness)

                    # Set tile elevation and index
                    tile.elevation = i + 1
                    tile.index = (j, k)

                    # Get the cartesian coordinates of the cell
                    cart_x, cart_y = j * tile.width / 2, k * tile.height

                    # Convert the cartesian coordinates to isometric coordinates
                    iso_x, iso_y = _cart_to_iso(cart_x, cart_y)

                    # Adjust the isometric coordinates to account for elevation
                    iso_y -= elevation_offset

                    # Set tile coordinates
                    tile.coordinates = (iso_x, iso_y)

                    # Add tile to terrain tiles
                    self.tiles.append(tile)

            elevation_offset += self.tile_thickness

    def update_pointed_tile(self, mouse_pos: tuple):
        """Update the Tile being currently pointed by the mouse.

        Args:
            mouse_pos (tuple): The current mouse position.
        """
        self.pointed_tile = None
        n = -1
        for tile in self.tiles:
            if tile.is_hovering(mouse_pos):
                # m is a calculation that is maximum for the tile "closer" to the user.
                # This is used to avoid highlighting several tiles when there is overlap between them.
                m = sum(tile.index) * tile.elevation
                if m > n:
                    self.pointed_tile = tile
                    n = m

    def update_zoom(self, event):
        """Update the zoom factor of the terrain based on mouse wheel events.

        Args:
            event: pygame event
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check if the mouse wheel is scrolled up and zoom in
            if event.button == 4:
                self.zoom_factor += 0.25
            # Check if the mouse wheel is scrolled down and zoom out
            elif event.button == 5:
                if self.zoom_factor <= 1:
                    self.zoom_factor -= 0.1
                else:
                    self.zoom_factor -= 0.25
                if self.zoom_factor < 0.1:
                    self.zoom_factor = 0.1

    def update_terrain_info(self, terrain_width: int, terrain_height: int, tile_width: int, tile_height: int,
                            tile_thickness: int, elevation: int, elevation_iterations: int):
        """Update terrain parameters.

        This method is specifically useful when the terrain parameters can change with buttons or input boxes.

        Args:
            terrain_width (int): Width of the terrain in tiles.
            terrain_height (int): Height of the terrain in tiles.
            tile_width (int): Width of an individual tile in pixels.
            tile_height (int): Height of an individual tile in pixels.
            tile_thickness (int): Thickness of an individual tile in pixels.
            elevation (int): Maximum elevation in the terrain.
            elevation_iterations(int): Number of iterations performed to generate the elevation.
        """

        self.terrain_width = terrain_width
        self.terrain_height = terrain_height
        self.tile_width = tile_width
        self.tile_height = tile_height
        self.tile_thickness = tile_thickness
        self.elevation = elevation
        self.elevation_iterations = elevation_iterations

    def update_selected_tiles(self, control_pressed: bool, left_mouse_pressed: bool):
        """Update the list of selected tiles.

        Args:
            control_pressed (bool): True if the left control keyboard button is pressed, False otherwise.
            left_mouse_pressed (bool): True if the left mouse button is pressed, False otherwise.
        """
        if self.tiles:
            # If mouse is pointing to a tile
            if self.pointed_tile is not None:
                # and the user left-clicks on the tile
                if left_mouse_pressed:
                    # and the control button is pressed
                    if control_pressed:
                        # unselect the tile if it was already selected.
                        if self.pointed_tile in self.selected_tiles:
                            self.pointed_tile.selected_tile = False
                            self.selected_tiles.remove(self.pointed_tile)
                    else:
                        # select the tile if it was not selected.
                        self.pointed_tile.selected_tile = True
                        self.selected_tiles.append(self.pointed_tile)
            # If user left-clicks while pressing control outside the terrain, unselected all tiles.
            if self.pointed_tile is None:
                if left_mouse_pressed and control_pressed:
                    for tile in self.selected_tiles:
                        tile.selected_tile = False
                    self.selected_tiles.clear()

    def change_selected_tile_type(self, tile_type: str, tile_images: dict):
        """Change the tile type of selected tiles.

        Args:
            tile_type (str): Tile type to change tile to.
            tile_images (dict): Dictionary with tile types as keys and path to the respective tile image as values.
        """
        if self.selected_tiles:
            for tile in self.selected_tiles:
                tile.tile_type = tile_type
                tile.image = pygame.image.load(tile_images[tile_type]).convert_alpha()
                tile.selected_tile = False
                self.terrain[tile.elevation - 1][tile.index] = tile_type
            self.selected_tiles.clear()

    def delete_tiles(self, event):
        """Delete selected tiles. Note that base_layer tiles cannot be deleted.

        Args:
            event: pygame event
        """
        # Delete selected tiles when pressing Del button.
        if event.type == pygame.KEYDOWN and event.key == pygame.K_DELETE:
            for tile in self.selected_tiles:
                # Base layer tiles cannot be deleted.
                if tile.elevation > 1:
                    for tile2 in self.tiles:
                        if tile.index == tile2.index and tile.elevation == tile2.elevation:
                            self.tiles.remove(tile2)
                    self.terrain[tile.elevation - 1][tile.index] = "0"
                    self.selected_tiles.remove(tile)

    def handle_events(self, event):
        """Groups event-related methods.

        Args:
            event: pygame event
        """
        self.update_zoom(event)
        self.delete_tiles(event)

    def draw(self, screen):
        """Draw the terrain on the given screen.

        Args:
            screen: pygame screen object
        """
        if self.tiles:
            # Iterate over all terrain tiles,
            for tile in self.tiles:
                # and call their draw method to draw them on the screen,
                tile.draw_tile(screen, self.zoom_factor, self.offset)
                # and highlight the tile that the mouse is pointing to.
                if self.pointed_tile is not None:
                    if self.pointed_tile.index == tile.index and self.pointed_tile.elevation == tile.elevation:
                        self.pointed_tile.highlight(screen, self.zoom_factor)

    def export_image(self, image_name: str):
        """Export the current terrain as a PNG image.

        Args:
            image_name (str): Name of the terrain to export as image.
        """

        # Calculate the width and height of the image in pixels
        image_width = (self.terrain_width + self.terrain_height) / 2 * self.tile_width + self.tile_width
        image_height = image_width / 2 + self.tile_thickness * self.elevation + self.tile_thickness
        # Create a pygame surface with the image dimensions
        surface = pygame.Surface((image_width, image_height), pygame.SRCALPHA)

        # Draw the tile images on the surface, updating the coordinates to be centered on the image.
        for tile in self.tiles:
            surface.blit(tile.image,
                         (tile.coordinates[0] + self.terrain_height * self.tile_width / 2,
                          tile.coordinates[1] + self.tile_width / 2 + self.tile_thickness * (self.elevation - 2)))

        # Save the surface as a PNG image. Note that my_terrains directory must exist.
        pygame.image.save(surface, f"my_terrains/{image_name}.png")

    def export_terrain_data(self, filename: str):
        """Export terrain data into a csv file.

        Creates a csv file containing the tile type matrix of each terrain layer and the terrain heightmap.

        Args:
            filename (str): The filename to store the data (i.e. my_terrains/filename.csv)
        """
        with open(f"my_terrains/{filename}.csv", "w") as file:
            for i in range(len(self.terrain)):
                if i == 0:
                    file.write("# Base layer\n")
                else:
                    file.write(f"# Elevation layer {i}\n")
                np.savetxt(file, self.terrain[i], fmt="%s", delimiter=",", comments="")

            if self.heightmap is not None:
                file.write("# Heightmap\n")
                np.savetxt(file, self.heightmap, fmt="%s", delimiter=",", comments="")


class Viewport:
    """A class that represents the viewport with display settings and event handling.

    Attributes:
        background_color (tuple): The background color of the viewport.
        fps (int): Frames per second for the viewport.
        quit (bool): A flag indicating when to quit the viewport.
        width (int): Width of the viewport window.
        height (int): Height of the viewport window.
        screen: Pygame screen object
        clock: Pygame clock object to control frame rate.
        buttons (list): List of Button objects.
        input_boxes (list): List of InputBox objects.

    Methods:
        create_button: Create a Button object and add it to the buttons list.
        create_input_box: Create an InputBox object and add it to the input_boxes list.
        generic_events: Handle generic events like closing the program with ESC key.
        handle_button_events: Handle mouse-click events for Button objects stored in the buttons list.
        handle_input_box_events: Handle events for InputBox objects stored in the input_boxes list.
    """
    def __init__(self):
        """Initialize the Viewport with display settings."""
        # Initialize pygame
        pygame.init()
        self.background_color = (202, 233, 241)
        self.fps = 60
        self.quit = False
        # Get screen width and height
        resolution = pygame.display.Info()
        self.width = resolution.current_w
        self.height = resolution.current_h
        # Create display object
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Tixel: A Tiled Terrain Generator.")
        # Create a clock object to control the frame rate
        self.clock = pygame.time.Clock()
        self.buttons = []
        self.input_boxes = []

    def create_button(self, coordinates: tuple, path_image: str, callback=None, path_pressed_image: str = None):
        """Create a Button object and add it to the buttons list.

        Args:
            coordinates (tuple): The coordinates of the button on the screen.
            path_image (str): The path to the image file for the button.
            callback (function, optional): The callback function to execute when the button is clicked.
            path_pressed_image (str, optional): The path to the image file for the button when it is being pressed.

        Returns:
            new_button: The created Button object.
        """
        new_button = Button(coordinates, path_image, callback, path_pressed_image)
        self.buttons.append(new_button)
        return new_button

    def create_input_box(self, coordinates: tuple, width: int, height: int, text: str, title: str = ""):
        """Create an InputBox object and add it to the input_boxes list.

        Args:
            coordinates (tuple): The coordinates of the input box on the screen.
            width (int): THe width of the input box.
            height (int): The height of the input box.
            text (str): The default text in the input box.
            title (str, optional): The title of the input box.

        Returns:
            new_input_box: The created InputBox object.
        """
        new_input_box = InputBox(coordinates, width, height, text, title)
        self.input_boxes.append(new_input_box)
        return new_input_box

    def generic_events(self, event):
        """Handle generic events like closing the program with ESC key.

        Args:
            event: Pygame event.
        """
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            self.quit = True

    def handle_button_events(self, event):
        """Handle mouse-click events for Button objects stored in the buttons list.

        Args:
            event: Pygame event.
        """
        for button in self.buttons:
            if event.type == pygame.MOUSEBUTTONDOWN:
                button.on_click(event)
            elif event.type == pygame.MOUSEBUTTONUP:
                button.on_release(event)

    def handle_input_box_events(self, event):
        """Handle events for InputBox objects stored in the input_boxes list.

        Args:
            event: Pygame event.
        """
        for input_box in self.input_boxes:
            input_box.handle_event(event)


class Button:
    """A class that represents a clickable button on the screen.

    Attributes:
        coordinates (tuple): The coordinates of the button on the screen.
        image: Pygame image object for the button.
        pressed (bool): Indicates if the button is currently pressed or not.
        pressed_image: Pygame image object for the button when pressed.
        rect: Pygame Rect for collision detection with mouse.
        callback (function, optional): The function to execute when the button is clicked.
        sprite: The current image (normal or pressed) of the button.

    Methods:
        on_click: Handle button click events and execute the callback function.
        on_release: Handle button release events.
        draw: Draw the button on the screen.
    """

    def __init__(self, coordinates: tuple, path_image: str, callback=None, path_pressed_image: str = None):
        """Initialize a Button instance.

        Args:
            coordinates (tuple): The coordinates of the button on the screen.
            path_image (str): The path to the image file for the button.
            callback (function, optional): The function to execute when the button is clicked.
            path_pressed_image (str, optional): The path to the image file for the button when it is being pressed.
        """
        self.coordinates = coordinates
        self.image = pygame.image.load(path_image).convert_alpha()
        self.pressed = False
        if path_pressed_image is None:
            self.pressed_image = self.image
        else:
            self.pressed_image = pygame.image.load(path_pressed_image).convert_alpha()
        self.rect = self.image.get_rect(topleft=coordinates)
        self.callback = callback
        self.sprite = self.image

    def on_click(self, event, argument=None):
        """Handle button click events and execute the callback function.

        Args:
            event: Pygame event.
            argument: An optional argument that will be returned if there is no callback function.
                      This argument just adds more flexibility to the button.

        Returns:
            The result of the callback function if any, or the provided argument if any.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.rect.collidepoint(event.pos):
                    self.sprite = self.pressed_image
                    self.pressed = True
                    if self.callback is not None:
                        self.callback()
                    elif argument is not None:
                        return argument

    def on_release(self, event):
        """Handle button release events.

        Args:
            event: Pygame event.
        """
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.sprite = self.image
                self.pressed = False

    def draw(self, screen):
        """Draw the button on the given screen.

        Args:
            screen: Pygame screen object.
        """
        screen.blit(self.sprite, self.coordinates)


class InputBox:
    """A class that represents an input box.

    Attributes:
        coordinates (tuple): THe coordinates of the input box on the screen.
        width (int): The width of the input box.
        height (int): Height of the input box.
        text (str): The text currently in the input box.
        text_x_offset = x offset used to adjust position of the text within the input box
        text_y_offset = y offset used to adjust position of the text within the input box
        title_x_offset = x offset used to adjust position of the title with respect to the input box
        title_y_offset = y offset used to adjust position of the title with respect to the input box
        color_inactive (tuple): Color of the text when the input box is not active.
        color_active (tuple): Color of the text when the input box is active.
        color: Current color of the text.
        title (str): Title of the input box that will be rendered on top of the box.
        text_surface: Pygame text surface for rendering the text of the input box.
        title_surface: Pygame text surface for rendering the title of the input box.
        rect: Pygame rect object for input box collision detection with mouse.
        active (bool): True if the input box is active, False otherwise.

    Methods:
        handle_event: Handle mouse and keyboard input events.
        draw: Draw the input box on the given screen.
    """
    def __init__(self, coordinates: tuple, width: int, height: int, text: str = "", title: str = ""):
        """Initialize an InputBox instance.

        Args:
            coordinates (tuple): The coordinates of the input box on the screen.
            width (int): The width of the input box.
            height (int): Height of the input box.
            text (str): The initial text in the input box.
            title (str, optional): The title of the input box.
        """
        self.coordinates = coordinates
        self.width = width
        self.height = height
        self.text = text
        self.text_x_offset = self.width / 2 - 7
        self.text_y_offset = self. height / 2 - 6
        self.title_x_offset = 0
        self.title_y_offset = - 20
        self.color_inactive = (169, 169, 169)
        self.color_active = (0, 0, 0)
        self.color = self.color_inactive
        self.title = title
        self.text_surface = pygame.font.SysFont("Calibri", 16).render(self.text, True, self.color)
        self.title_surface = pygame.font.SysFont("Calibri", 16).render(self.title, True, self.color_active)
        self.rect = pygame.rect.Rect(coordinates[0], coordinates[1], width, height)
        self.active = False

    def handle_event(self, event):
        """Handle mouse and keyboard events.

        Args:
            event: Pygame event.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            # If the mouse is over the input box rect.
            if event.button == 1:
                if self.rect.collidepoint(event.pos):
                    # Activate the box.
                    self.active = True
                    self.color = self.color_active
                else:
                    # Deactivate the box.
                    self.active = False
                    self.color = self.color_inactive

        # Handle writing in the input box.
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    self.active = False
                    self.color = self.color_inactive
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                # Render the text again.
        self.text_surface = pygame.font.SysFont("Calibri", 16).render(self.text, True, self.color)

    def draw(self, screen):
        """Draw the input box on the given screen.

        Args:
            screen: Pygame screen.
        """
        pygame.draw.rect(screen, (255, 255, 255), self.rect)
        screen.blit(self.text_surface,
                    (self.rect.x + self.text_x_offset, self.rect.y + self.text_y_offset))
        screen.blit(self.title_surface, (self.rect.x + self.title_x_offset, self.rect.y + self.title_y_offset))


class CheckBox:
    """A class that represents a checkbox.

    Attributes:
        coordinates (tuple): The coordinates of the checkbox on the screen.
        unchecked_image: Pygame image object for the checkbox when it is unchecked.
        checked_image: Pygame image object for the checkbox when it is checked.
        image: Current image of the checkbox.
        rect: Pygame rect object for collision detection with the mouse.
        checked (bool): True if checkbox is checked, False otherwise.

    Methods:
        on_click: Handle checkbox mouse click events.
        check: Check the checkbox.
        uncheck: Uncheck the checkbox.
        draw: Draw the checkbox on the given screen.
    """
    def __init__(self, coordinates: tuple, path_unchecked_image: str, path_checked_image: str):
        """Initialize a Checkbox instance.

        Args:
            coordinates (tuple): The coordinates of the checkbox on the screen.
            path_unchecked_image (str): The path to the image file for the checkbox when it is unchecked.
            path_checked_image (str): THe path to the image file for the checkbox when it is checked.
        """
        self.coordinates = coordinates
        self.unchecked_image = pygame.image.load(path_unchecked_image).convert_alpha()
        self.checked_image = pygame.image.load(path_checked_image).convert_alpha()
        self.image = self.unchecked_image
        self.rect = self.image.get_rect(topleft=coordinates)
        self.checked = False

    def on_click(self, event):
        """Handle checkbox mouse click events.

        Args:
            event: Pygame event.

        Returns:
            bool: True if the checkbox was checked.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.rect.collidepoint(event.pos):
                    self.check()
                    return True

    def check(self):
        """Check the checkbox."""
        if not self.checked:
            self.image = self.checked_image
            self.checked = True

    def uncheck(self):
        """Uncheck the checkbox"""
        if self.checked:
            self.image = self.unchecked_image
            self.checked = False

    def draw(self, screen):
        """Draw the checkbox on the given screen.

        Args:
            screen: Pygame screen object.
        """
        screen.blit(self.image, self.coordinates)


class TileInformation:
    """A class to manage and store information related to the terrain tiles and UI elements related to them.

    Attributes:
        tile_directory (str): The directory where tile images are stored.
        tile_types (list): A list of the existing tile types.
        tile_images (dict): A dictionary mapping tile types to their respective tile image paths.
        tile_buttons (dict): A dictionary mapping tile types to their respective UI buttons.
        tile_input_boxes (dict): A dictionary mapping tile types to their respective UI probability input boxes.
        tile_checkboxes (dict): A dictionary mapping tile types to their respective elevation checkboxes.
        tile_probabilities (dict): A dictionary storing tile types and their probabilities.

    Methods:
        gather_tile_information: Collect information about the available tile types and their images.
        create_tile_buttons: Create a UI button for each tile type.
        create_tile_probability_input_box: Create an input box for each tile type to specify their probabilities.
        create_elevation_tile_checkboxes: Create a checkbox for each tile type to specify the elevation tile type.
        update_tile_probability: Update the tile probability dictionary based on the input box values.
        handle_button_events: Handle events related to clicking tile type buttons.
        handle_input_box_events: Handle events related to tile type input boxes.
        handle_checkbox_events: Handle events related to elevation tile checkboxes.
        draw: Draw the UI elements on the screen.
    """
    def __init__(self, tile_directory: str, viewport: Viewport):
        """Initialize a TileInformation instance.

        Args:
            tile_directory (str): The directory where tiles images are stored.
            viewport (Viewport): An instance of the Viewport class.
        """
        self.tile_directory = tile_directory
        self.tile_types = []
        self.tile_images = {}
        self.tile_buttons = {}
        self.tile_input_boxes = {}
        self.tile_checkboxes = {}
        self.tile_probabilities = {}
        self.gather_tile_information()
        self.create_tile_buttons(viewport)
        self.create_tile_probability_input_boxes(viewport)
        self.create_elevation_tile_checkboxes(viewport)

    def gather_tile_information(self):
        """Collect information about the available tile types and their images."""
        i = 0
        for tile_file in os.listdir(self.tile_directory):
            i += 1
            self.tile_types.append(str(i))
            tile_image_path = os.path.join(self.tile_directory, tile_file)
            if os.path.isfile(tile_image_path):
                # Create a dictionary that contains the path to the image of each tile type
                self.tile_images[str(i)] = tile_image_path

    def create_tile_buttons(self, viewport: Viewport):
        """Create a UI button for each tile type.

        Args:
            viewport (Viewport): An instance of the Viewport class.
        """
        for i in range(len(self.tile_types)):
            self.tile_buttons[self.tile_types[i]] = Button(
                (viewport.width / 20, 40 * (i + 1)),
                path_image=self.tile_images[self.tile_types[i]])
            self.tile_buttons[self.tile_types[i]].pressed_image = pygame.transform.scale_by(
                self.tile_buttons[self.tile_types[i]].image, 0.75)

    def create_tile_probability_input_boxes(self, viewport: Viewport):
        """Create an input box for each tile type to specify their probabilities.

        Args:
            viewport (Viewport): An instance of the Viewport class.
        """
        for i in range(len(self.tile_types)):
            self.tile_input_boxes[self.tile_types[i]] = viewport.create_input_box(
                coordinates=(viewport.width / 20 + 50, 40 * (i + 1.15)),
                width=93,
                height=20,
                text=str(round(1 / len(self.tile_types), 2)))

        self.tile_input_boxes[self.tile_types[0]].title = "Tile Probability"
        self.tile_input_boxes[self.tile_types[0]].title_surface = pygame.font.SysFont("Calibri", 16) \
            .render(self.tile_input_boxes[self.tile_types[0]].title, True,
                    self.tile_input_boxes[self.tile_types[0]].color_active)
        self.tile_input_boxes[self.tile_types[0]].title_x_offset -= 2

    def create_elevation_tile_checkboxes(self, viewport: Viewport):
        """Create a checkbox for each tile type to specify the elevation tile type.

        Args:
            viewport (Viewport): An instance of the Viewport class.
        """
        for i in range(len(self.tile_types)):
            self.tile_checkboxes[self.tile_types[i]] = CheckBox(
                coordinates=(viewport.width / 20 - 42, 39 * (i + 1.4)),
                path_unchecked_image="assets/checkbox.png",
                path_checked_image="assets/checkbox_selected.png"
            )

    def update_tile_probability(self):
        """Update the tile probability dictionary based on the input box values."""
        for i in range(len(self.tile_types)):
            try:
                self.tile_probabilities[self.tile_types[i]] = float(self.tile_input_boxes[self.tile_types[i]].text)
            except ValueError:
                self.tile_probabilities[self.tile_types[i]] = 0

    def handle_button_events(self, event):
        """Handle events related to clicking tile type buttons.

        Args:
            event: Pygame event.
        """
        new_tiles = []
        for key, value in self.tile_buttons.items():
            new_tile_type = value.on_click(event, key)
            value.on_release(event)
            new_tiles.append(new_tile_type)
        return new_tiles

    def handle_input_box_events(self, event):
        """Handle events related to tile type input boxes.

        Args:
            event: Pygame event.
        """
        for input_box in self.tile_input_boxes.values():
            input_box.handle_event(event)

    def handle_checkbox_events(self, event):
        """Handle events related to elevation tile checkboxes.

        Args:
            event: Pygame event.
        """
        for checkbox in self.tile_checkboxes.values():
            response = checkbox.on_click(event)
            if response:
                for checkbox2 in self.tile_checkboxes.values():
                    if checkbox2 != checkbox:
                        checkbox2.uncheck()

    def draw(self, screen):
        """Draw the UI elements on the given screen.

        Args:
            screen: Pygame screen object.
        """
        for button in self.tile_buttons.values():
            button.draw(screen)
        for input_box in self.tile_input_boxes.values():
            input_box.draw(screen)
        for checkbox in self.tile_checkboxes.values():
            checkbox.draw(screen)


# Start of helper functions.
def _generate_seed(width: int, height: int = None):
    """Generate a numpy array filled with random numbers between 0 and 1 to be used as seed.

    Args:
        width: The width of the terrain to generate (in tiles).
        height: The height of the terrain to generate (in tiles).

    Returns:
        seed: A numpy array of size width x height filled with random numbers between 0 and 1.

    """
    # Create a numpy array filled with random numbers
    seed = np.random.rand(height, width)
    return seed


def _accumulate_probabilities(probabilities: dict):
    """Generate a dictionary mapping the tile types to their accumulated probability of appearing.

    This function takes a dictionary with tile types and probabilities as key-value pairs
    and calculates the accumulated probability for each tile.

    Args:
        probabilities (dict): Dictionary mapping the tile types to their probabilities of appearing in the base layer.

    Returns:
        cumulative_probabilities (dict): Dictionary with tile types as keys and their accumulated probability as values.
    """
    # Create a dictionary with cumulative probabilities
    cumulative_probabilities = {}
    accum_probability = 0
    for key, value in probabilities.items():
        accum_probability += value
        cumulative_probabilities[key] = accum_probability

    return cumulative_probabilities


def _assign_tile(number: float, accum_probabilities: dict):
    """Assign a tile to a cell given a value and its accumulated probability of appearing.

    Args:
        number (float): Seed value of the cell. Must be between 0 and 1.
        accum_probabilities (dict): Dictionary having tiles as keys and their accumulated probabilities as values.

    Returns:
        key (str): The tile type to assign.
    """
    for key, value in accum_probabilities.items():
        if number < value:
            return key


def _generate_unchecked_tiles(terrain: np.ndarray):
    """Return a shuffled list of tile coordinates.

    Args:
        terrain: The terrain of which the list of tile coordinates need to be shuffled.

    Returns:
        coordinates (list): The shuffled list of coordinates.
    """
    height, width = terrain.shape
    coordinates = []
    for i in range(height):
        for j in range(width):
            coordinates.append((i, j))

    random.shuffle(coordinates)
    return coordinates


def _get_neighbor_tiles(terrain: np.ndarray, position: tuple):
    """Return a list with the tile types of a given tile neighbors.

    Args:
        terrain: The terrain where the tile and neighbors are located.
        position (tuple): The positional coordinates of the tile in the terrain.

    Returns:
        neighbors (list): List with the tile types of all neighbors.
    """
    # Get current terrain layer
    height, width = terrain.shape

    # Get coordinates
    i, j = position

    # First row tiles
    if i == 0:
        # Top left corner
        if j == 0:
            neighbors = [terrain[i, j + 1],
                         terrain[i + 1, j],
                         terrain[i + 1, j + 1]]
        # Top right corner
        elif j == width - 1:
            neighbors = [terrain[i, j - 1],
                         terrain[i + 1, j],
                         terrain[i + 1, j - 1]]
        # Top edge
        else:
            neighbors = [terrain[i, j - 1],
                         terrain[i + 1, j],
                         terrain[i + 1, j - 1],
                         terrain[i + 1, j + 1],
                         terrain[i, j + 1]]
    # Last row tiles
    elif i == height - 1:
        # Bottom left corner
        if j == 0:
            neighbors = [terrain[i, j + 1],
                         terrain[i - 1, j],
                         terrain[i - 1, j + 1]]
        # Bottom right corner
        elif j == width - 1:
            neighbors = [terrain[i, j - 1],
                         terrain[i - 1, j],
                         terrain[i - 1, j - 1]]
        # Bottom edge
        else:
            neighbors = [terrain[i, j - 1],
                         terrain[i - 1, j],
                         terrain[i - 1, j - 1],
                         terrain[i - 1, j + 1],
                         terrain[i, j + 1]]
    # First column tiles
    elif j == 0:
        neighbors = [terrain[i - 1, j],
                     terrain[i - 1, j + 1],
                     terrain[i, j + 1],
                     terrain[i + 1, j + 1],
                     terrain[i + 1, j]]
    # Last column tiles
    elif j == width - 1:
        neighbors = [terrain[i - 1, j],
                     terrain[i - 1, j - 1],
                     terrain[i, j - 1],
                     terrain[i + 1, j - 1],
                     terrain[i + 1, j]]
    # Middle tiles
    else:
        neighbors = [terrain[i, j - 1],
                     terrain[i + 1, j - 1],
                     terrain[i + 1, j],
                     terrain[i + 1, j + 1],
                     terrain[i, j + 1],
                     terrain[i - 1, j + 1],
                     terrain[i - 1, j],
                     terrain[i - 1, j - 1]]

    return neighbors


def _set_to_neighbor_type(neighbors: list, tiles: list):
    """Return the most frequent tile type of given tile neighbors

    Args:
        neighbors (list): List with the tile types of the tile neighbors
        tiles (list): List with possible tile types

    Returns:
        most_frequent (str): Most frequent neighbor tile type.
    """
    # Dictionary to keep track of the counts of each tile type
    tile_count = {tile_type: 0 for tile_type in tiles}

    # Count the tile type
    for neighbor in neighbors:
        tile_count[neighbor] += 1

    # Find the tile type with the most frequency
    # Start with the first tile type
    most_frequent = list(tile_count.keys())[0]

    # If tile type count is greater set it as most frequent
    for tile in tile_count:
        if tile_count[tile] > tile_count[most_frequent]:
            most_frequent = tile
        # If there are two tiles with same count choose one randomly
        elif tile_count[tile] == tile_count[most_frequent]:
            if random.random() > 0.5:
                most_frequent = tile

    return most_frequent


def _generate_heightmap(terrain: np.ndarray, elevation_symbol: str, elevation: int, iterations: int):
    """Generate a heightmap with a maximum value lower or equal to the specified elevation

    Args:
        terrain: The terrain to generate a heightmap for.
        elevation_symbol (str): The tile symbol on top of which elevation will be generated. (i.e. mountain symbol).
        elevation (int): The maximum possible value of elevation.
                   The actual value will depend on the terrain constraints and iterations.
        iterations (int): Number of iterations to smooth out the elevation.

    Returns:
        heightmap: A Numpy array indicating the elevation value at each tile position.
    """
    width, height = terrain.shape
    # Generate a numpy array filled with zeros.
    heightmap = np.zeros((width, height))

    # Iterate over the terrain array and if the tile symbol is equal to the elevation symbol,
    # substitute the 0 in the heightmap array to the elevation value.
    for i in range(width):
        for j in range(height):
            if terrain[i, j] == elevation_symbol:
                heightmap[i, j] = elevation

    # Next step is to smooth the heightmap.
    for _ in range(iterations):
        # Iterate over the heightmap
        for i in range(width):
            for j in range(height):
                # If the current position is not elevation skip to next position
                if heightmap[i, j] == 0:
                    continue
                # Else get the value of their neighbors and the current tile
                else:
                    values = _get_neighbor_tiles(heightmap, (i, j))
                    values.append(heightmap[i, j])

                    # Set the value of the current position to the average
                    heightmap[i, j] = (sum(values) / len(values))

    # Return heightmap with truncated values
    return np.trunc(heightmap)


def _cart_to_iso(x, y):
    """Convert cartesian coordinates to isometric coordinates.

    Args:
        x: x value of cartesian coordinate.
        y: y value of cartesian coordinate.

    Returns:
        iso_x: x value of isometric coordinate.
        iso_y: y value of isometric coordinate.
    """
    iso_x = x - y
    iso_y = (x + y) / 2
    return iso_x, iso_y


def _load_tile_images(tile_images: dict):
    """Load the tile images from png files and stores them in a dictionary.

    This function uses pygame.image.load() method to load the images.

    Args:
        tile_images (dict): Dictionary containing the tile types as keys
                     and the path to their corresponding png image as values.

    Returns:
        tiles (dict): Dictionary containing the tile types as keys and the loaded images as values.
    """
    tiles = {}
    for key, value in tile_images.items():
        tiles[key] = pygame.image.load(value).convert_alpha()
    return tiles