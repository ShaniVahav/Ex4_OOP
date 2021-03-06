from math import sqrt

def nodesDict(nodes_list):
    nodes = {}
    for dict in nodes_list:
        node_id = str(dict['id'])
        x, y, _ = dict['pos'].split(',')
        pos = (float(x), float(y))
        nodes[node_id] = pos
    return nodes


def edgesDict(edges_list):
    edges = {}
    for dict in edges_list:
        src = str(dict['src'])
        dest = dict['dest']
        w = dict['w']
        if src not in edges.keys():
            edges[src] = []
        edges[src].append((dest, w))
    return edges


class Graph:
    def __init__(self, nodes_list, edges_list):
        self.nodes = nodesDict(nodes_list)
        self.edges = edgesDict(edges_list)

    def dis(self, a, b):  # a, b are lists
        x1 = a[0]
        x2 = b[0]
        y1 = a[1]
        y2 = b[1]
        return abs(sqrt(pow((x1 - x2), 2) + pow((y1 - y2), 2)))

    def findPokemon(self, pos, type):
        x, y, _ = pos.split(',')
        pos = (float(x)), (float(y))
        for src_id in self.edges.keys():
            src = self.nodes[src_id]
            for dest_node in self.edges[src_id]:
                dest_id = dest_node[0]
                if int(src_id) < int(dest_id) and type >= 0 or int(src_id) > int(dest_id) and type <= 0:
                    dest = self.nodes[str(dest_id)]
                    dis_srcToDest = self.dis(src, dest)
                    dis_pokemonToNodes = self.dis(src, pos) + self.dis(pos, dest)
                    if (abs(dis_srcToDest - dis_pokemonToNodes)) < 0.00001:
                        return src_id, dest_id

        return None

    def updatePokemons(self, agent_nodesListKeys, pokemons, isTarget_pokemon):
        for dict in pokemons:
            false_flag = False
            agent_flag = False
            pos = dict['Pokemon']['pos']
            type = dict['Pokemon']['type']

            for list in isTarget_pokemon['false']:
                if str(pos) == str(list[0]):
                    false_flag = True
                    break

            for list in agent_nodesListKeys:
                if str(list[0]) == str(pos):
                    agent_flag = True
                    break

            if false_flag == False and agent_flag == False:
                pokemon = Graph.findPokemon(self, pos, type)
                l = (pos, pokemon)
                isTarget_pokemon['false'].insert(0, l)

        return isTarget_pokemon

    def shortestPath(self, A, B):  # A - src of agent, B - edge(src_node, dest_node)
        src_node = int(B[0])
        if src_node == A:
            return [B[1]]
        dest_node = B[1]
        path = [src_node, dest_node]
        # initialize distance from A (src)
        d = [1000000] * len(self.nodes)
        d[A] = 0

        phi = [0] * len(self.nodes)  # list of a pointers to the previews node in the path (to keep the path)
        visited = [False] * len(self.nodes)  # control the visited nodes
        allVisited = False

        while not allVisited:
            # find the minimum dis node from src that not visited
            id_min = 0
            for i in range(len(self.nodes)):
                if not visited[i]:
                    id_min = i
                    break
            for j in range(len(self.nodes)):
                if d[j] < d[id_min] and not visited[j]:
                    id_min = j

            # update all its sons if necessary
            for node_dest in self.edges[str(id_min)]:
                dest = node_dest[0]
                w = node_dest[1]
                if d[id_min] + w < d[dest]:
                    d[dest] = d[id_min] + w
                    phi[dest] = id_min
            visited[id_min] = True

            # check if all visited
            allVisited = True
            for i in range(len(visited)):
                if not visited[i]:
                    allVisited = False
                    break

        i = src_node  # src node
        while i != A:
            path.insert(0, phi[i])
            i = phi[i]

        return path
