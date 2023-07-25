# map-generator
<p> This is a random map generator meant for building multi-agent pathfinding (MAPF) environments. The generator creates 2D numpy arrays filled with 1s and 0s, where 1s represent obstacles and 0s represent empty space. These maps can be used to train and test MAPF models. </p>

## Room Formation
<p> The generator is designed to create room and corridor-like spaces. This is achieved by randomly placing "seeds" one by one in an originally empty map. Each seed attemps to expand outwards to a room of random dimensions, growing around previously developed rooms. After expanding, each room is surrounded by obstacles. </p>

## Doors
<p> Once rooms are generated, doors (empty spaces that allow an agent to pass between adjacent rooms) are added by removing specific obstacles Initially, one door is placed between each pair of adjacent rooms to ensure full connectivity. Then, each obstacle separating any two rooms has an adjustable probability of becoming an additional door. Finally, certain sets of doors between rooms which are not necessary to achieve full connectivity between rooms are removed with an adjustable probability. </p>

## Graph Representation
<p> A graph representation of the generated map is also created, with nodes representing rooms and edges representing sets of doors between adjacent rooms. Each node contains the following information: index number, x coordinate (of the seed used to create the room), y coordinate (of the seed used to create the room), room size, and whether the room is a corridor. Each edge contains the following information: index of first connected node, index of second connected node, number of doors between the nodes, and whether either of the connected nodes is a corridor (and if so, which).  </p>

## Visualization
<p> Three figures are plotted for visualization. First, the map is shown with doors and different rooms highlighted. Second, the final map is shown. Third, the graph representation is plotted. An A* path between two random nodes is also added to the graph. </p>
