import matplotlib.pyplot as plt
import matplotlib.patches as patches

def PlotTerrain2D(sizeX, sizeY, sourceY):
    fig, ax = plt.subplots()
    ax.set_xlim(0, sizeX)
    ax.set_ylim(0, sizeY)
    ax.set_title('Simulation of Water Flow')
    ax.set_xticks([])
    ax.set_yticks([sourceY+0.5])
    ax.set_yticklabels(["Source \nof water"])
    
    # Add a rectangle to represent the terrain
    rectangle = plt.Rectangle((0, 0), sizeX, 0.1*sizeY, linewidth=2, edgecolor='black', facecolor='gray')
    ax.add_patch(rectangle)
    plt.plot([0, sizeX, sizeX, 0, 0], [0, 0, sizeY, sizeY, 0], color='black', linewidth=4)
    plt.plot([0.01, 0.01], [sourceY, sourceY+1], color='red', linewidth=8)
    plt.show()

