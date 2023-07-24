import random
import numpy as np
from matplotlib import pyplot as plt
import networkx as nx


def make_map(env_size=(30, 40)):
    """Generates random map"""
    min_size = env_size[0]
    max_size = env_size[1]
    world_size = random.randint(min_size, max_size)
    world = np.zeros((world_size, world_size))
    min_room_size = 4   # The smallest size a room can be
    max_room_dim = world_size   # The largest dimension a room can have
    extra_door_probability = 0.02   # For any two rooms connected by a door, each wall block separating the two
                                    # rooms has this probability of becoming an additional door
    door_removal_probability = 0.75   # Each set of doors between two rooms that is not necessary to ensure full
                                      # connectedness (each non-cut edge) has this probability of being removed

    def grow(x, y, x_padding, y_padding):
        """Grows out a room from a seed"""
        x_vals = []
        y_vals = []
        queue = [(y, x)]
        for (curr_y, curr_x) in queue:
            if world[curr_y, curr_x] == 0 and abs(curr_y - y) <= y_padding and abs(curr_x - x) <= x_padding:
                world[curr_y, curr_x] = r
                y_vals.append(curr_y)
                x_vals.append(curr_x)
                queue.extend([(curr_y - 1, curr_x), (curr_y + 1, curr_x), (curr_y, curr_x - 1), (curr_y, curr_x + 1)])
        return x_vals, y_vals

    # checks to
    def is_tail(x, y):
        """Checks if there is a 1 unit thick segment of a room"""
        return not ((world[y + 1, x] == r and world[y, x + 1] == r) or (
                world[y + 1, x] == r and world[y, x - 1] == r) or
                    (world[y - 1, x] == r and world[y, x + 1] == r) or (world[y - 1, x] == r and world[y, x - 1] == r))

    def check_single(x, y):
        """Checks if a valid room can be grown from a specific location"""
        # Check if normal room can be generated
        for a in range(int((max_room_dim - 1) / 2)):
            for b in range(int((max_room_dim - 1) / 2)):
                x_vals, y_vals = grow(x, y, int((max_room_dim - 1) / 2) - a, int((max_room_dim - 1) / 2) - b)
                if all(not (is_tail(x_vals[j], y_vals[j])) for j in range(len(x_vals))) and len(
                        x_vals) >= min_room_size:
                    for k in range(len(x_vals)):
                        world[y_vals[k], x_vals[k]] = 0
                    return True
                for k in range(len(x_vals)):
                    world[y_vals[k], x_vals[k]] = 0

        # Check if corridor can be generated
        for c in range(int((max_room_dim - 1) / 2) + 1):
            x_vals, y_vals = grow(x, y, 0, int((max_room_dim - 1) / 2) - c)
            for k in range(len(x_vals)):
                world[y_vals[k], x_vals[k]] = 0
            if len(x_vals) >= min_room_size:
                return True

            x_vals, y_vals = grow(x, y, int((max_room_dim - 1) / 2) - c, 0)
            for k in range(len(x_vals)):
                world[y_vals[k], x_vals[k]] = 0
            if len(x_vals) >= min_room_size:
                return True

        return False

    def check_valid():
        """Checks if there is some location from which a valid room can be grown"""
        for x in range(world_size):
            for y in range(world_size):
                if check_single(x, y):
                    return True
        return False

    def dfs_helper(vertex, deleted, connected):
        """Uses DFS to find the nodes (rooms) that remain connected after a specific edge
        (set of doors between two rooms) has been removed"""
        connected.append(vertex)
        for edge in edges:
            if edge[0] == vertex and not (edge[1] in connected) and edge != deleted:
                dfs_helper(edge[1], edge, connected)
            elif edge[1] == vertex and not (edge[0] in connected) and edge != deleted:
                dfs_helper(edge[0], deleted, connected)

    def is_cut_edge(deleted):
        """Checks if an edge (set of doors between two rooms) is a cut edge"""
        connected = []
        dfs_helper(deleted[0], deleted, connected)
        if len(connected) == r - 1:
            return False
        else:
            return True

    for i in range(world_size):
        world[0, i] = -2
        world[world_size - 1, i] = -2
        world[i, 0] = -2
        world[i, world_size - 1] = -2

    nodes = []
    r = 1
    while check_valid():
        # randomly select seed locations until one that a valid room can grow from is chosen
        while True:
            x = random.randint(1, world_size - 2)
            y = random.randint(1, world_size - 2)
            if check_single(x, y) and (r == 1 or (y - 2 >= 0 and world[y - 2, x] > 0) or
                                       (y + 2 <= world_size - 1 and world[y + 2, x] > 0) or
                                       (x - 2 >= 0 and world[y, x - 2] > 0) or
                                       (x + 2 <= world_size - 1 and world[y, x + 2] > 0)):
                break

        # try to grow into room of random dimensions until a valid room is generated
        while True:
            max_x = random.randint(1, max_room_dim)
            x_padding = int((max_x - 1) / 2)
            max_y = random.randint(1, max_room_dim)
            y_padding = int((max_y - 1) / 2)

            x_vals, y_vals = grow(x, y, x_padding, y_padding)

            room_size = len(y_vals)
            if (all(xs == x_vals[0] for xs in x_vals) or all(
                    ys == y_vals[0] for ys in y_vals)) and room_size >= min_room_size:
                corr = 1
                break
            elif all(not (is_tail(x_vals[j], y_vals[j])) for j in range(len(x_vals))) and room_size >= min_room_size:
                corr = 0
                break
            for i in range(len(x_vals)):
                world[y_vals[i], x_vals[i]] = 0

        # surround room with walls
        for a in range(max(y - y_padding, 1), min(y + y_padding + 1, world_size - 1)):
            for b in range(max(x - x_padding, 1), min(x + x_padding + 1, world_size - 1)):
                if world[a - 1, b] == 0 and world[a, b] == r:
                    world[a - 1, b] = -1
                if world[a + 1, b] == 0 and world[a, b] == r:
                    world[a + 1, b] = -1
                if world[a, b - 1] == 0 and world[a, b] == r:
                    world[a, b - 1] = -1
                if world[a, b + 1] == 0 and world[a, b] == r:
                    world[a, b + 1] = -1
                if world[a - 1, b - 1] == 0 and world[a, b] == r:
                    world[a - 1, b - 1] = -1
                if world[a + 1, b + 1] == 0 and world[a, b] == r:
                    world[a + 1, b + 1] = -1
                if world[a - 1, b + 1] == 0 and world[a, b] == r:
                    world[a - 1, b + 1] = -1
                if world[a + 1, b - 1] == 0 and world[a, b] == r:
                    world[a + 1, b - 1] = -1
        nodes.append((r, x, y, room_size, corr))
        r = r + 1

    # fill map edges and unused space with walls
    for i in range(world_size):
        world[0, i] = -1
        world[world_size - 1, i] = -1
        world[i, 0] = -1
        world[i, world_size - 1] = -1

    for i in range(world_size):
        for j in range(world_size):
            if world[i, j] == 0:
                world[i, j] = -1

    # add doors between all adjacent rooms
    door_options = {}
    doors = []
    for y in range(1, world_size - 1):
        for x in range(1, world_size - 1):
            if world[y, x] == -1 and world[y - 1, x] > 0 and world[y + 1, x] > 0 and world[y, x - 1] == -1 and \
                    world[y, x + 1] == -1 and world[y - 1, x] != world[y + 1, x]:
                pair = (int(min(world[y - 1, x], world[y + 1, x])), int(max(world[y - 1, x], world[y + 1, x])))
                if not (pair in door_options):
                    door_options[pair] = [(y, x)]
                else:
                    door_options[pair].append((y, x))
            if world[y, x] == -1 and world[y - 1, x] == -1 and world[y + 1, x] == -1 and world[y, x - 1] > 0 and world[
                y, x + 1] > 0 and world[y, x - 1] != world[y, x + 1]:
                pair = (int(min(world[y, x - 1], world[y, x + 1])), int(max(world[y, x - 1], world[y, x + 1])))
                if not (pair in door_options):
                    door_options[pair] = [(y, x)]
                else:
                    door_options[pair].append((y, x))
    edges = []
    for pair in door_options.keys():
        (y, x) = random.choice(door_options[pair])
        world[y, x] = -9
        doors.append((x, y))
        count = 1
        for (y, x) in door_options[pair]:
            if random.random() < extra_door_probability and not ((x, y) in doors):
                world[y, x] = -9
                doors.append((x, y))
                count = count + 1
        if nodes[pair[0] - 1][4] == 1 and nodes[pair[1] - 1][4] == 1:
            corridor = 3
        elif nodes[pair[0] - 1][4] == 1:
            corridor = 1
        elif nodes[pair[1] - 1][4] == 1:
            corridor = 2
        else:
            corridor = 0
        edges.append((pair[0], pair[1], count, corridor))

    # remove some unnecessary sets of doors (non-cut edges)
    randomized_edges = random.sample(edges, len(edges))
    for edge in randomized_edges:
        if not (is_cut_edge(edge)) and random.random() < door_removal_probability:
            for (y, x) in door_options[(edge[0], edge[1])]:
                world[y, x] = -1
                if (x, y) in doors:
                    doors.remove((x, y))
            edges.remove(edge)

    # replace spaces assigned to specific room numbers or doors with empty space
    world_final = world.copy()
    for i in range(world_size):
        for j in range(world_size):
            if world_final[i, j] > 0 or world_final[i, j] == -9:
                world_final[i, j] = 0

    # print world and node, door, and edge information
    print(world)
    print(" \nNodes (index, x, y, size, corridor): \n", nodes)
    print(" \nDoors (x, y): \n", doors)
    print(" \nEdges (node1, node2, number of doors, corridor as endpoint): \n", edges)

    # create graph representation and random a* path
    G = nx.Graph()
    for edge in edges:
        G.add_edge(edge[0], edge[1])

    start = random.randint(1, r - 1)
    end = random.randint(1, r - 1)

    print(" \nAgent start node:", start)
    print("Target node:", end)

    path = nx.astar_path(G, start, end)
    path_edges = list(zip(path, path[1:]))
    print("A* path:", path)

    # visualization
    plt.figure(1)
    plt.imshow(world)
    plt.figure(2)
    plt.imshow(world_final)
    plt.figure(3)
    pos = nx.spring_layout(G)
    nx.draw_networkx(G, pos)
    nx.draw_networkx_nodes(G, pos, nodelist=path, node_color='r')
    nx.draw_networkx_edges(G, pos, edgelist=path_edges, edge_color='r')
    plt.show()


make_map()
