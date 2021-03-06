"""
@author AchiyaZigi
OOP - Ex4
Very simple GUI example for python client to communicates with the server and "play the game!"
"""
import asyncio
import json
import sys
from pygame import *

import Algo
import GUI
from GUI import *
from client import Client


class controller:
    def __init__(self, agent):
        self.moveCounter = 0
        self.numberOfMoves = 0
        self.move = agent


"""""""""""""""""""""""
 Connection and Login
"""""""""""""""""""""""
# default port
PORT = 6666
# server host (default localhost 127.0.0.1)
HOST = '127.0.0.1'

client = Client()
client.start_connection(HOST, PORT)

graph_json = client.get_graph()
graph_info = json.loads(graph_json, object_hook=lambda json_dict: SimpleNamespace(**json_dict))

"""""""""""""""""""""""
    Building graph
"""""""""""""""""""""""
nodes_list = json.loads(client.get_graph())['Nodes']
edges_list = json.loads(client.get_graph())['Edges']
gameGraph = Algo.Graph(nodes_list, edges_list)
"""""""""""""""""""""""
    Plot the graph
"""""""""""""""""""""""
view = GUI.initializeView(graph_info)  # return (my_scale, screen, clock)
my_scale = view[0]
screen = view[1]
clock = view[2]

"""""""""""""""""""""""
Stop and Timer buttons
"""""""""""""""""""""""


def stop_button(stopButton):
    for event in pygame.event.get():
        if event.type == MOUSEBUTTONDOWN and stopButton.collidepoint(event.pos):
            print(client.get_info())
            client.stop()
            client.stop_connection()
            sys.exit()


"""""""""""""""""""""""""""""""""""
Add the agents & Set agent_nodesList 
"""""""""""""""""""""""""""""""""""
info = json.loads(client.get_info(), object_hook=lambda d: SimpleNamespace(**d)).GameServer
number_of_nodes = len(graph_info.Nodes)
number_of_agents = info.agents

# Adding the agents close to pokemon
pokemons = json.loads(client.get_pokemons())['Pokemons']
edgesWithPokemon = [Algo.Graph.findPokemon(gameGraph, dict['Pokemon']['pos'], dict['Pokemon']['type']) for dict in
                    pokemons]

for i in range(number_of_agents):
    if len(edgesWithPokemon) - 1 < i:
        break
    node = edgesWithPokemon[i][0]
    client.add_agent("{\"id\":" + str(node) + "}")

isTarget_pokemon = {'false': [], 'true': []}  # [(pos, (src_node, dest_node)), ... (...)]
agent_nodesList = {}

"""""""""""""""""""""""
    Move functions
"""""""""""""""""""""""
async def move_after(delay):
    await asyncio.sleep(delay)
    client.move()

async def movePokemons(agent):
    if agent.speed >= 4:
        await move_after(0.085)
        return
    if agent.speed == 3:
        await move_after(0.122)
        return
    if agent.speed <= 2:
        await move_after(0.16)
        return
    await move_after(0.18)


"""""""""""""""""""""""
   Start the 'game'!
"""""""""""""""""""""""
client.start()

agents = json.loads(client.get_agents())['Agents']
for dict in agents:
    id = dict['Agent']['id']
    if id not in agent_nodesList:
        agent_nodesList[str(id)] = {'list': [], 'pokemon': []}
agent = agents[0]
c = controller(agent)
while client.is_running() == 'true':
    agents = json.loads(client.get_agents(), object_hook=lambda d: SimpleNamespace(**d)).Agents
    p = json.loads(client.get_pokemons(), object_hook=lambda d: SimpleNamespace(**d)).Pokemons
    pokemons = json.loads(client.get_pokemons())['Pokemons']
    info = json.loads(client.get_info())

    update = GUI.display_update(agents, p, graph_info, my_scale, screen, clock, info,
                                client.time_to_end(), c.moveCounter, number_of_agents)

    agents = update[0]

    agents2 = json.loads(client.get_agents())['Agents']
    agents_pos = {}
    for dict in agents2:
        id = dict['Agent']['id']
        pos = dict['Agent']['pos']
        agents_pos[str(id)] = pos

    stopButton = update[2]
    stop_button(stopButton)

    isTarget_pokemon = Algo.Graph.updatePokemons(gameGraph, agent_nodesList.keys(), pokemons, isTarget_pokemon)

    for agent in agents:
        if agent.dest == -1:
            c.move = (agent)
            id = agent.id

            if len(agent_nodesList[str(id)]['list']) == 0:
                if len(isTarget_pokemon['false']) > 0:
                    A = int(agent.src)
                    B = isTarget_pokemon['false'][0][1]  # the edge he needs to pass through
                    agent_nodesList[str(id)]['list'] = (Algo.Graph.shortestPath(gameGraph, A, B))
                    agent_nodesList[str(id)]['pokemon'] = isTarget_pokemon['false'][0]
                    del isTarget_pokemon['false'][0]
                else:
                    agent_nodesList[str(id)]['list'] = [0]

            next_node = agent_nodesList[str(id)]['list'].pop(0)
            client.choose_next_edge('{"agent_id":' + str(agent.id) + ', "next_node_id":' + str(next_node) + '}')

            d = agent_nodesList[str(id)]['pokemon'][1][1]
            if next_node == d:
                if agent.speed >= 4:
                    client.move()
                c.move = agent
                break

    asyncio.run(movePokemons(c.move))
    stop_button(stopButton)
