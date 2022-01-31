The Rendered.ai example channel images toys in a container on a floor.  The objects are "dropped" via a simululation of gravity and rigid body physics, and the images are generated from a digital twin camera that senses simulated ambient light as well as a spotlight.
 
The properties of the dataset are controlled by the graph. Graphs are implemented left to right with object generators and modifiers feeding into the scene building (placement and drop physics), before ending in the render node that generates an run for the dataset.
![graph image](./RenderedaiExampleChannelGraph.png)

The graph in the image chooses 25 objects with equal probability from a group of 5 object types.  All object types other than the Rubik's cube are given a random color. A simulation is run where the objects are dropped into a random container which sits on a random floor before the scene is renedered into a 512x512 image. The objects that appear in the image are annotated for use in ML pipelines.

The nodes for the Rendered.ai example channel are listed in the table below.

|Node   |Subcagory   |Category   |Tooltip   |
|---|---|---|---|
|Container   |Generators   |Objects   |Container factory   |
|Floor   |Generators   |Objects   |Floor factory   |
|Yo-yo   |Generators   |Objects   |Yoyo factory   |
|Rubik's Cube   |Generators   |Objects   |Rubik's Cube factory   |
|Mix Cube   |Generators   |Objects   |Mixed up Rubik's Cube factory   |
|Playdough   |Generators   |Objects   |Play dough tub factory   |
|Bubbles   |Generators   |Objects   |Bubbles bottle factory   |
|Skateboard   |Generators   |Objects   |Toy skateboard factory   |
|Random Integer   |Generators   |Values   |Generate random integers between 'low' and 'high' (based on numpy.random.randint)   |
|Weight   |Branch   |Modifiers   |Change the weight of a generator   |
|Color Variation   |Color   |Modifiers   |Change the color variation between objects   |
|Random Placement   |Placement   |Modifiers   |Place objects in a scene   |
|Drop Objects   |Physics   |Modifiers   |Drop the passed objects into the container   |
|Render  |Image   |Render   |Render and image for the scene and create associated annotations and metadata  |

All the nodes that are generators can create an object in the code logic. This goes for 3d objects as well as random integers. The weight node modifies the graph tree by adjusting the likelyhood it's branch is chosen.  The color variiation modifies the color of input object generators. Think of the color variation modifier as modifying an object type as it outputs a generator for use at runtime. The drop objects node adds a floor and a container to the scene and bakes the physics, passing the final scene to the render node. The render node adds lighing and a camera before rendering the scene and writing the metadata and annotations.