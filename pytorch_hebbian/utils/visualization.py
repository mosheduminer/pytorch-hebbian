import math

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors
import torchvision
import torch


def show_image(image, title=None):
    np_img = image.numpy()
    plt.imshow(np.transpose(np_img, (1, 2, 0)))
    if title is not None:
        plt.title(title)
    plt.show()


def draw_synapse(synapse, shape):
    mat = np.reshape(synapse, shape)
    im = plt.matshow(mat, cmap='bwr', interpolation='nearest')
    plt.colorbar(im, ticks=[np.amin(mat), 0, np.amax(mat)])
    plt.show()


def draw_weights(synapses, shape, height, width):
    if len(shape) == 1:
        dim = int(np.sqrt(int(shape[0])))
        shape = (dim, dim)

    fig, axs = plt.subplots(height, width,
                            sharex='col',
                            sharey='row',
                            gridspec_kw={'hspace': 0, 'wspace': 0})
    fig.suptitle('Weights')

    mats = []
    index = 0
    for i in range(height):
        for j in range(width):
            synapse = synapses[index]
            index += 1
            mat = np.reshape(synapse, shape)
            mats.append(axs[i, j].matshow(mat, cmap='bwr'))

    for ax in fig.get_axes():
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        ax.tick_params(bottom=False, top=False, labelbottom=False)

    # Find the min and max of all colors for use in setting the color scale.
    images = mats
    vmin = min(image.get_array().min() for image in images)
    vmax = max(image.get_array().max() for image in images)
    norm = colors.Normalize(vmin=-vmax, vmax=vmax)
    for im in images:
        im.set_norm(norm)

    fig.colorbar(images[0],
                 ax=axs,
                 orientation='horizontal',
                 fraction=.1,
                 ticks=[vmin, 0, vmax])
    plt.show()


def draw_weights_update(fig, synapses, shape, height=None, width=None):
    plt.pause(0.001)

    # TODO: support grids with non-square sizes
    if height is None or width is None:
        height = int(math.sqrt(synapses.shape[0]))
        width = height

    dim_y, dim_x, depth = shape

    yy = 0
    data = np.zeros((dim_y * height, dim_x * width, depth))

    for y in range(height):
        for x in range(width):
            data[y * dim_y:(y + 1) * dim_y, x * dim_x:(x + 1) * dim_x, :] = synapses[yy, :].reshape(dim_y, dim_x, depth)
            yy += 1

    plt.clf()

    if depth > 1:
        plt.imshow((data - np.amin(data)) / (np.amax(data) - np.amin(data)))
    else:
        nc = np.amax(np.absolute(data))
        im = plt.imshow(data, cmap='bwr', vmin=-nc, vmax=nc)
        fig.colorbar(im, ticks=[np.amin(data), 0, np.amax(data)])

    plt.axis('off')
    fig.canvas.draw()


def draw_weights_update2(fig, synapses, shape):
    plt.pause(0.001)

    h, w, d = shape

    synapses = np.array([torch.from_numpy(synapse.reshape(h, w, d)) for synapse in synapses])
    print(synapses.shape)

    data = torchvision.utils.make_grid(synapses)

    plt.clf()

    if d > 1:
        plt.imshow((data - np.amin(data)) / (np.amax(data) - np.amin(data)))
    else:
        nc = np.amax(np.absolute(data))
        im = plt.imshow(data, cmap='bwr', vmin=-nc, vmax=nc)
        fig.colorbar(im, ticks=[np.amin(data), 0, np.amax(data)])

    plt.axis('off')
    fig.canvas.draw()


def show_image_grid(patches):
    plt.figure(figsize=(6, 5))
    for i, patch in enumerate(patches[:100]):
        plt.subplot(10, 10, i + 1)
        plt.imshow(patch, interpolation='nearest', cmap='gray')
        plt.xticks(())
        plt.yticks(())

    plt.suptitle('Data')
    plt.show()
