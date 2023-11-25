import tixel
import pygame


def main():
    # Create the viewport
    viewport = tixel.Viewport()

    # Create input boxes
    terrain_name_input = viewport.create_input_box(coordinates=(viewport.width / 3 + 50, 58), width=120, height=20,
                                                   text="My_Terrain", title="Terrain Name")
    terrain_name_input.text_x_offset = 0
    elevation_input = viewport.create_input_box(coordinates=(viewport.width - 317, 205), width=65, height=20,
                                                text="8", title="Elevation")
    elevation_input.title_x_offset += 3
    elevation_iterations_input = viewport.create_input_box(coordinates=(viewport.width - 233, 205), width=65, height=20,
                                                           text="3", title="Iterations")
    elevation_iterations_input.title_x_offset += 1
    terrain_width_input = viewport.create_input_box(coordinates=(viewport.width - 545, 58), width=40, height=20,
                                                    text="32", title=" Terrain Size")
    terrain_width_input.title_x_offset += 6
    terrain_height_input = viewport.create_input_box(coordinates=(viewport.width - 490, 58), width=40, height=20,
                                                     text="32", title="")
    tile_width_input = viewport.create_input_box(coordinates=(viewport.width - 433, 58), width=65, height=20,
                                                 text="32", title="Tile Width")
    tile_width_input.title_x_offset -= 1
    tile_height_input = viewport.create_input_box(coordinates=(viewport.width - 350, 58), width=72, height=20,
                                                  text="16", title="Tile Height")
    tile_height_input.title_x_offset += 1
    tile_thickness_input = viewport.create_input_box(coordinates=(viewport.width - 260, 58), width=93, height=20,
                                                     text="7", title="Tile Thickness")
    tile_thickness_input.title_x_offset += 1

    # Create Terrain
    terrain = tixel.Terrain(terrain_width=int(terrain_width_input.text),
                            terrain_height=int(terrain_height_input.text),
                            tile_width=int(tile_width_input.text),
                            tile_height=int(tile_height_input.text),
                            tile_thickness=int(tile_thickness_input.text))

    # Create terrain generation buttons
    base_layer_button = viewport.create_button(
        coordinates=(viewport.width - 150, 25),
        path_image="assets/generate_base_layer.png",
        callback=lambda: terrain.generate_base_layer(tile_information.tile_probabilities, tile_information.tile_images),
        path_pressed_image="assets/generate_base_layer_pressed.png"
    )

    smooth_base_layer_button = viewport.create_button(
        coordinates=(viewport.width - 150, 100),
        path_image="assets/smooth_base_layer.png",
        callback=lambda: terrain.smooth_base_layer(tile_information.tile_types, tile_information.tile_images),
        path_pressed_image="assets/smooth_base_layer_pressed.png"
    )

    generate_terrain_elevation_button = viewport.create_button(
        coordinates=(viewport.width - 150, 175),
        path_image="assets/generate_terrain_elevation.png",
        callback=lambda: terrain.generate_elevation(tile_information.tile_images),
        path_pressed_image="assets/generate_terrain_elevation_pressed.png"
    )

    # Create terrain export buttons
    generate_terrain_image_button = viewport.create_button(
        coordinates=(viewport.width / 6, 25),
        path_image="assets/generate_image.png",
        callback=lambda: terrain.export_image(terrain_name_input.text),
        path_pressed_image="assets/generate_image_pressed.png"
    )
    export_terrain_data_button = viewport.create_button(
        coordinates=(viewport.width / 4 + 25, 25),
        path_image="assets/export_terrain.png",
        callback=lambda: terrain.export_terrain_data(terrain_name_input.text),
        path_pressed_image="assets/export_terrain_pressed.png"
    )

    # Create tile information object
    tile_information = tixel.TileInformation(tile_directory="tiles", viewport=viewport)

    # Set a default elevation symbol
    tile_information.tile_checkboxes["1"].check()
    terrain.elevation_symbol = "1"

    # Define some booleans to track the state of some key presses
    left_button_pressed = False
    right_button_pressed = False
    lctrl_button_pressed = False

    # Start viewport update loop
    while not viewport.quit:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    left_button_pressed = True
                elif event.button == 3:
                    right_button_pressed = True
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    left_button_pressed = False
                elif event.button == 3:
                    right_button_pressed = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_LCTRL:
                lctrl_button_pressed = True
            elif event.type == pygame.KEYUP and event.key == pygame.K_LCTRL:
                lctrl_button_pressed = False

            # Handle generic events
            viewport.generic_events(event)
            # Handle input boxes events
            viewport.handle_input_box_events(event)
            # Handle button events
            viewport.handle_button_events(event)
            # Handle checkboxes events
            tile_information.handle_checkbox_events(event)
            if terrain.tiles:
                # Handle tile information button events
                new_tile_type = tile_information.handle_button_events(event)
                for tile_type in new_tile_type:
                    if tile_type is not None:
                        terrain.change_selected_tile_type(tile_type, tile_information.tile_images)
            # Handle terrain object related events
            terrain.handle_events(event)

        # Update tile probability
        tile_information.update_tile_probability()

        # Update elevation tile
        for key, value in tile_information.tile_checkboxes.items():
            if value.checked:
                terrain.elevation_symbol = key

        # Update terrain information
        try:
            terrain.update_terrain_info(terrain_width=int(terrain_width_input.text),
                                        terrain_height=int(terrain_height_input.text),
                                        tile_width=int(tile_width_input.text),
                                        tile_height=int(tile_height_input.text),
                                        tile_thickness=int(tile_thickness_input.text),
                                        elevation=int(elevation_input.text),
                                        elevation_iterations=int(elevation_iterations_input.text))
        except ValueError:
            pass

        # Update selected tiles
        terrain.update_selected_tiles(lctrl_button_pressed, left_button_pressed)

        # Get current mouse position
        mouse_pos = pygame.mouse.get_pos()

        # Get mouse position relative to last frame
        rel_x, rel_y = pygame.mouse.get_rel()

        # Check if right mouse button is pressed and if there is a terrain on screen to pan:
        if right_button_pressed and terrain.tiles:
            terrain.offset[0] += rel_x
            terrain.offset[1] += rel_y

        # Update which tile the mouse is hovering over
        terrain.update_pointed_tile(mouse_pos)

        # Fill the screen with background color
        viewport.screen.fill(viewport.background_color)

        # Draw terrain
        terrain.draw(viewport.screen)

        # Draw input boxes to the screen
        for input_box in viewport.input_boxes[3:]:
            input_box.draw(viewport.screen)
        if terrain.tiles:
            for input_box in viewport.input_boxes[:3]:
                input_box.draw(viewport.screen)

        viewport.screen.blit(pygame.font.Font(None, 20).render("x", True, (0, 0, 0)), (viewport.width - 501, 61))

        # Draw buttons to screen
        base_layer_button.draw(viewport.screen)
        if terrain.tiles:
            smooth_base_layer_button.draw(viewport.screen)
            generate_terrain_elevation_button.draw(viewport.screen)
            generate_terrain_image_button.draw(viewport.screen)
            export_terrain_data_button.draw(viewport.screen)

        for button in tile_information.tile_buttons.values():
            button.draw(viewport.screen)

        # Draw checkboxes to screen
        for checkbox in tile_information.tile_checkboxes.values():
            checkbox.draw(viewport.screen)

        viewport.screen.blit(pygame.font.SysFont("Arial", 16).render("Elevation", True, (0, 0, 0)),
                             (viewport.width / 20 - 65, 15))
        viewport.screen.blit(pygame.font.SysFont("Arial", 16).render("tile", True, (0, 0, 0)),
                             (viewport.width / 20 - 46, 30))

        # Update the display
        pygame.display.flip()

        # Limit the frame rate
        viewport.clock.tick(viewport.fps)

    # Quit game upon exiting the loop
    pygame.quit()


if __name__ == "__main__":
    main()
