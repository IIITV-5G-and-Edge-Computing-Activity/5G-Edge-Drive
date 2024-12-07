from heapq import heappop, heappush

def a_star(graph, start, goal):
    open_set = []
    heappush(open_set, (0, start))
    came_from = {}
    cost_so_far = {start: 0}

    while open_set:
        _, current = heappop(open_set)

        if current == goal:
            break

        for neighbor, weight in graph[current]:
            new_cost = cost_so_far[current] + weight
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                priority = new_cost
                heappush(open_set, (priority, neighbor))
                came_from[neighbor] = current

    path = []
    current = goal
    while current != start:
        path.append(current)
        current = came_from[current]
    path.append(start)
    path.reverse()
    return path
