# -*- coding: utf-8 -*-
"""
Created on Fri Nov 10 13:31:55 2017

@author: Astrid
"""
import math as m
import pandas as pd

def auto_disc_calc_grid(steps, min_grid, max_grid, detail, stretch_factor):
    new_grid = list()
    total_width = sum(steps)
    ideal_min_width = total_width/(20+2*detail)

    # detail == 1    --> stretch = 1.8
    # detail == 100  --> stretch = 1.04
    if stretch_factor==0:
        MIN_DETAIL = 1
        MAX_DETAIL = 100
        MAX_STRETCH = 1.8
        MIN_STRETCH = 1.04
        b = (MAX_STRETCH - MIN_STRETCH)/((MIN_DETAIL - MAX_DETAIL)*(MIN_DETAIL - MAX_DETAIL))
        stretch_factor = b*(detail - MAX_DETAIL)*(detail - MAX_DETAIL) + MIN_STRETCH

    # first determine the left/right element sides
    left_side_dx = list();
    right_side_dx = list();
    for i in range(len(steps)):
        s = min_grid
        # did the user fix the grid sides?
        if min_grid != 0:
            s = min_grid
        else:
            s = ideal_min_width
        # check if layer width is less then 3*min_grid width
        if s*3 > steps[i]:
            s = steps[i]/3
        left_side_dx.append(s)
        right_side_dx.append(s)

    # Now loop again over all interior boundaries and check that the sizes of the neighboring cells are within the stretch factor ratio.
    for i in range(len(steps)-1):
        if right_side_dx[i] < left_side_dx[i+1]:
            ratio = left_side_dx[i+1]/right_side_dx[i]
            if ratio > stretch_factor:
                left_side_dx[i+1] = right_side_dx[i]*stretch_factor
            else:
                ratio = right_side_dx[i]/left_side_dx[i+1]
                if ratio > stretch_factor:
                    right_side_dx[i] = left_side_dx[i+1]*stretch_factor

    # Now for the actual discretization loop
    for i in range(len(steps)):
        effective_max_grid = max_grid
        # If the max_grid is already smaller than the grid on either side, simply ignore the max grid parameter
        if effective_max_grid != 0:
            if effective_max_grid < left_side_dx[i]*stretch_factor or effective_max_grid < right_side_dx[i]*stretch_factor:
                effective_max_grid = 0
        # iterative simple approach
        grid_from_left = list()
        grid_from_right = list()
        grid_from_left.append(left_side_dx[i])
        grid_from_right.append(right_side_dx[i])

        space_left = steps[i] - grid_from_left[0] - grid_from_right[0]
        # Check special case
        if space_left < steps[i]/3*stretch_factor:
            # we have a 3-element layer, so we are already done
            new_steps = list((grid_from_left[0], space_left, grid_from_right[0]))
            new_grid.append(new_steps)
            continue
        # Iteratively add grid to both sides until we have filled the space
        iterations = 1000
        while space_left > 1e-8 or iterations == 0:
            # special case if grid is the same on both sides
            if grid_from_left[-1] == grid_from_right[-1]:
                new_dx = grid_from_left[-1]*stretch_factor
                if new_dx*2 < space_left and (effective_max_grid == 0 or new_dx <= effective_max_grid):
                    grid_from_left.append(new_dx)
                    grid_from_right.append(new_dx)
                    space_left = space_left - 2*new_dx
            # Only discretize on left if we have smaller elements than the other side
            if grid_from_left[-1] < grid_from_right[-1]:
                # continue on left side
                new_dx = grid_from_left[-1]*stretch_factor
                # if we are within the constraints, add the grid element
                if new_dx < space_left and (effective_max_grid == 0 or new_dx <= effective_max_grid):
                    grid_from_left.append(new_dx)
                    space_left = space_left - new_dx
                # otherwise we don't add and wait what happens
            # Only discretize on right if we have smaller elements than the other side, here we have the chance to 'catch up' with the left side
            if grid_from_left[-1] > grid_from_right[-1]:
                # continue on right side
                new_dx = grid_from_right[-1]*stretch_factor
                # if we are within the constraints, add the grid element
                if new_dx < space_left and (effective_max_grid == 0 or new_dx <= effective_max_grid):
                    grid_from_right.append(new_dx)
                    space_left = space_left - new_dx
                    # otherwise we don't add and wait what happens
            # calculate remaining space
            space_left = steps[i] - sum(grid_from_left) - sum(grid_from_right)

            # Now we have to deal with several cases:
            #1. space_left < 0 ... we added too many elements and have to step back a bit
            #2. space_left > 1e-8 (the limit) but space_left is smaller than the biggest grid cells on both sides
            #3. space_left > 1e-8 and there is enough space to continue meshing (that's a simple continue)
            #3.1 we could continue meshing but we have reached the maximum grid size already on both sides

            # Case 1 : overshot, shouldn't happen
            if space_left < -1e-8:
                print('overshot!')

            # calculate the space needed at least
            needed_space = min([grid_from_left[-1]*stretch_factor, grid_from_right[-1]*stretch_factor])
            if space_left < needed_space:
                not_enough_space = True
            else:
                not_enough_space = False
            if grid_from_left[-1] == grid_from_right[-1]:
                if space_left < needed_space*2:
                    not_enough_space = True
                else:
                    not_enough_space = False

            # Case 2 : we don't have enough space for further meshing, this is the most critical case!
            if space_left > 1e-8 and not_enough_space:
                # Essentially we have to distribute the sum of the innermost 2 cells + space_left over 3 or 4 cells depending on the stretch factor
                available_space = space_left + grid_from_left[-1] + grid_from_right[-1]
                # now check if three cells would work
                dx = available_space/3
                if dx < grid_from_left[-1] and dx < grid_from_right[-1]:
                    # ok, proposal accepted
                    grid_from_left[-1] = dx
                    grid_from_left.append(dx)
                    grid_from_right[-1] = dx
                else:
                    dx = available_space/4
                    grid_from_left[-1] = dx
                    grid_from_left.append(dx)
                    grid_from_right[-1] = dx
                    grid_from_right.append(dx)
                space_left = 0;
                continue # done

            # Case 3 : ok, all good, go on with meshing
            # Case 3.1 : what if we have reached the maximum grid size already?
            if effective_max_grid != 0 and needed_space > effective_max_grid:
                # Now we have to distribute the remaining space into equidistant steps < effective_max_grid
                n = m.ceil(space_left/effective_max_grid)
                dx = space_left/n
                for j in range(n):
                    grid_from_left.append(dx)
                space_left = 0 # this will stop the iteration now
            iterations = iterations - 1
    

        # Adjust biggest element of the grid_from_left vector such, that the sum of all elements equals steps[i] exactly
        dx_adjust = steps[i] - sum(grid_from_left) - sum(grid_from_right)
        grid_from_left[-1] = (grid_from_left[-1] + dx_adjust)

        # Now create the new steps vector that contains the complete grid
        grid_from_right.reverse()
        new_steps = grid_from_left + grid_from_right
    
        # Finally! add the new steps
        new_grid.append(new_steps)
    return new_grid

def adjust_ranges(selection_range, old_range, new_range, x_direction):
    # Calculate the differences in widths and heights and resulting movements of layers to the right/bottom of the modified range
    x_move = (new_range[2] - new_range[0]) - (old_range[2] - old_range[0])
    y_move = (new_range[3] - new_range[1]) - (old_range[3] - old_range[1])

    # x-direction
    if x_direction:
        #if selection is completely to the left of new selection, nothing has to be done
        if selection_range[2] < old_range[0]:
            return selection_range
        #if selection is completely to the right of the new selection, move all points
        if selection_range[0] > old_range[2]:
            selection_range[0] = selection_range[0] + x_move
            selection_range[2] = selection_range[2] + x_move
        else:
            # Now we have a few options:
            # 1. the selection is completely part of the modified range (oldRange)
            # 2. the modified range (oldRange) is completely part of the selection
            # 3. the right side of the selection is modified
            # 4. the left side of the selection is modified

            # (1) If this selection was entirely part of the selected range m_removed, it will become as big as the new range m_inserted
            # NOTE: oldRange(1) is always == oldRange(3) because of input parameters in auto_discretize_x (index, index)
            if selection_range[0] >= old_range[0] and selection_range[2] <= old_range[2]:
                selection_range[0] = new_range[0]
                selection_range[2] = new_range[2]
                # NOTE: if we cut out a section, left will be > then right, allowing us to remove deleted assignments later on
            # (2) If the selected range m_removed was a part of this selection, we only need to move the right boundary
            elif selection_range[0] <= old_range[0] and selection_range[2] >= old_range[2]:
                selection_range[2] = selection_range[2] + x_move
            #(3) and (4) are only valid if the new range is cut out if (newRange(3) - newRange(1)) < 0
            else:
            #Check for option (3)
                if selection_range[0] < old_range[0] and selection_range[2] <= old_range[2]:
                    selection_range[2] = old_range[0] - 1
            # otherwise option (4)
                else:
                    selection_range[0] = old_range[0]
                    selection_range[1] = selection_range[2] + x_move

    #y-direction
    else:
        # if selection is completely to the top of new selection, nothing has to be done
        if selection_range[3] < old_range[1]:
            return selection_range
        # if selection is completely to the bottom of the new selection, move all points
        if selection_range[1] > old_range[3]:
            selection_range[1] = selection_range[1] + y_move
            selection_range[3] = selection_range[3] + y_move
        else:
            # Now we have a few options:
            # 1. the selection is completely part of the modified range (m_removed)
            # 2. the modified range (m_removed) is completely part of the selection
            # 3. the bottom side of the selection is modified
            # 4. the top side of the selection is modified

            # (1) If this selection was entirely part of the selected range m_removed, it will become as big as the new range m_inserted
            # NOTE: oldRange(2) is always == oldRange(4) because of input parameters in auto_discretize_x (index, index)
            if selection_range[1] >= old_range[1] and selection_range[3] <= old_range[3]:
                selection_range[1] = new_range[1]
                selection_range[3] = new_range[3]
                # NOTE: if we cut out a section, top will be > then bottom, allowing us to remove deleted assignments later on
            # (2) If the selected range m_removed was a part of this selection, we only need to move the bottom boundary
            elif selection_range[1] <= old_range[1] and selection_range[3] >= old_range[3]:
                selection_range[2] = selection_range[3] + y_move
                # (3) and (4) are only valid if the new range is cut out if (newRange(4) - newRange(2)) < 0
            else:
                # check for option (3)
                if selection_range[1] < old_range[1] and selection_range[3] <= old_range[2]:
                    selection_range[3] = old_range[3] - 1
                    # otherwise option (4)
                else:
                    selection_range[1] = old_range[1]
                    selection_range[3] = selection_range[3] + y_move
    return selection_range

def modify_X_steps(new_steps, old_left_col, old_right_col, x_steps, rows, assignments):
    # Replace discretisation in X direction by newly created discretisation steps
    xsteps_new = x_steps[:]
    xsteps_new[old_left_col-1:old_right_col] = new_steps
    # Loop over all assignments and update the assignments
    old_range = [old_left_col-1, 0, old_right_col-1, rows-1 ]; #[left top right bottom]
    new_range = [old_left_col-1, 0, old_left_col+len(new_steps)-2, rows-1]; #[left top right bottom]
    assignments_new = pd.DataFrame(columns=['line','type','range','name'])
    assignments_new[['line','type','name']] = assignments[['line','type','name']]
    for i in range(assignments.shape[0]):
        select_range = assignments.loc[i,'range'][:]
        assignments_new.loc[i,'range'] = adjust_ranges(selection_range=select_range, old_range=old_range, new_range=new_range, x_direction=True)
    return assignments_new, xsteps_new

def modify_Y_steps(new_steps, old_top_row, old_bottom_row, cols, y_steps, assignments):
    # Replace discretisation in Y direction by newly created discretisation steps
    ysteps_new = y_steps[:]
    ysteps_new[old_top_row:old_bottom_row+1] = new_steps
    # Loop over all assignments and update the assignments
    old_range = [0, old_top_row-1, cols-1, old_bottom_row-1]; #[left top right bottom]
    new_range = [0, old_top_row-1, cols-1, old_top_row+len(new_steps)-2]; #[left top right bottom]
    assignments_new = pd.DataFrame(columns=['line','type','range','name'])
    for i in range(assignments.shape[0]):
        select_range = assignments.loc[i,'range'][:]
        assignments_new.loc[i,'range'] = adjust_ranges(selection_range=select_range, old_range=old_range, new_range=new_range, x_direction=False)
    return assignments_new, ysteps_new

def discr_X(xsteps, ysteps, column, assignments, param_discr):
    # first calculate new grid suggestion
    new_grid_column = auto_disc_calc_grid(steps=list([xsteps[column-1]]), min_grid=param_discr['min_grid'], max_grid=param_discr['max_grid'], detail=param_discr['detail'], stretch_factor=param_discr['stretch factor'])[0]
    # now update the assignments
    assignments_new, xsteps_new = modify_X_steps(new_steps=new_grid_column, old_left_col=column, old_right_col=column, x_steps=xsteps, rows=len(ysteps), assignments=assignments)
    return xsteps_new, assignments_new

def discr_Y(xsteps, ysteps, row, assignments, param_discr):
    # first calculate new grid suggestion
    new_grid_row = auto_disc_calc_grid(steps=list([ysteps[row-1]]), min_grid=param_discr['min_grid'], max_grid=param_discr['max_grid'], detail=param_discr['detail'], stretch_factor=param_discr['stretch factor'])[0]
    # now update the assignments
    assignments_new, ysteps_new = modify_Y_steps(new_steps=new_grid_row, old_top_row=row, old_bottom_row=row, cols=len(xsteps), y_steps=ysteps, assignments=assignments)
    return ysteps_new, assignments_new