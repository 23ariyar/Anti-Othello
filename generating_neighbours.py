def getNeighbours(pos):
    size = 8 * 8
    w = 8
    h = 8
    neighbours = []

    if pos - w >= 0:
        neighbours.append(pos - w)
    if pos % w != 0:
        neighbours.append(pos - 1)

    if (pos + 1) % w != 0:
        neighbours.append(pos + 1)
        
    if pos + w < size:
        neighbours.append(pos + w)

    if ((pos - w - 1) >= 0) and (pos % w != 0):
        neighbours.append(pos - w - 1)

    if ((pos - w + 1) >= 0) and ((pos + 1) % w != 0):
        neighbours.append(pos - w + 1)

    if ((pos + w - 1) < size) and (pos % w != 0):
        neighbours.append(pos + w - 1)

    if ((pos + w + 1) < size) and ((pos + 1) % w != 0):
        neighbours.append(pos + w + 1)

    return neighbours

my_list = [getNeighbours(i) for i in range(64)]
print(my_list)