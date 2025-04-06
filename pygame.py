import pygame, asyncio
import math
import heapq
import random

# Initialize pygame properly
pygame.init()

# Constants
WIDTH, HEIGHT = 1000, 800
GRID_SIZE = 5
NODE_RADIUS = 15
FONT_SIZE = 12
COLORS = {
    'WHITE': (255, 255, 255),
    'BLACK': (0, 0, 0),
    'RED': (255, 0, 0),
    'GREEN': (0, 255, 0),
    'BLUE': (0, 0, 255),
    'YELLOW': (255, 255, 0),
    'GRAY': (200, 200, 200),
    'BACKGROUND': (240, 240, 240)
}

async def main():
    try:
        # Set up display inside async context
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Dijkstra's Pathfinder")
        font = pygame.font.SysFont('Arial', FONT_SIZE)
        clock = pygame.time.Clock()

        class TrafficLight:
            def __init__(self):
                self.cycle_time = 20
                self.green_time = self.cycle_time / 2
                self.red_time = self.cycle_time / 2
                self.current_light = random.choice(['red', 'green'])
                self.last_change = pygame.time.get_ticks()

            def update(self):
                now = pygame.time.get_ticks()
                elapsed = (now - self.last_change) / 1000
                
                if (self.current_light == 'green' and elapsed > self.green_time) or \
                   (self.current_light == 'red' and elapsed > self.red_time):
                    self.current_light = 'red' if self.current_light == 'green' else 'green'
                    self.last_change = now

            def get_state(self):
                now = pygame.time.get_ticks()
                elapsed = (now - self.last_change) / 1000
                remaining = self.green_time - elapsed if self.current_light == 'green' else self.red_time - elapsed
                return max(0, remaining), self.current_light

        class Node:
            def __init__(self, x, y, name):
                self.x = x
                self.y = y
                self.name = name
                self.connections = {}
                self.traffic_light = TrafficLight() if random.random() < 0.7 else None

            def update(self):
                if self.traffic_light:
                    self.traffic_light.update()

            def get_delay(self):
                if not self.traffic_light:
                    return 0
                remaining, state = self.traffic_light.get_state()
                return remaining if state == 'red' else 0

            def draw(self, surface, selected=False):
                color = COLORS['BLUE']
                if selected:
                    color = COLORS['RED']
                elif self.traffic_light:
                    _, state = self.traffic_light.get_state()
                    color = COLORS['GREEN'] if state == 'green' else COLORS['RED']

                pygame.draw.circle(surface, color, (self.x, self.y), NODE_RADIUS)
                text = font.render(self.name, True, COLORS['BLACK'])
                text_rect = text.get_rect(center=(self.x, self.y - NODE_RADIUS - 5))
                surface.blit(text, text_rect)

                if self.traffic_light:
                    remaining, _ = self.traffic_light.get_state()
                    time_text = font.render(f"{remaining:.1f}s", True, COLORS['BLACK'])
                    time_rect = time_text.get_rect(center=(self.x, self.y + NODE_RADIUS + 5))
                    surface.blit(time_text, time_rect)

        class Graph:
            def __init__(self):
                self.nodes = []
                self.start = None
                self.end = None
                self.path = []
                self.distance = 0
                self.time = 0

            def add_node(self, node):
                self.nodes.append(node)

            def connect(self, node1, node2):
                dist = math.hypot(node1.x - node2.x, node1.y - node2.y)
                node1.connections[node2] = {'distance': dist, 'weight': dist}
                node2.connections[node1] = {'distance': dist, 'weight': dist}

            def update_weights(self):
                for node in self.nodes:
                    node.update()
                    for neighbor in node.connections:
                        node.connections[neighbor]['weight'] = (
                            node.connections[neighbor]['distance'] + 
                            neighbor.get_delay()
                        )

            def find_path(self):
                if not self.start or not self.end:
                    return False

                heap = [(0, self.start, [])]
                visited = set()
                distances = {node: float('inf') for node in self.nodes}
                distances[self.start] = 0

                while heap:
                    current_time, current_node, current_path = heapq.heappop(heap)
                    
                    if current_node in visited:
                        continue
                        
                    visited.add(current_node)
                    new_path = current_path + [current_node]

                    if current_node == self.end:
                        total_dist = sum(
                            new_path[i].connections[new_path[i+1]]['distance']
                            for i in range(len(new_path)-1)
                        )
                        self.path = new_path
                        self.distance = total_dist
                        self.time = current_time
                        return True

                    for neighbor, data in current_node.connections.items():
                        if neighbor not in visited:
                            new_time = current_time + data['weight']
                            if new_time < distances[neighbor]:
                                distances[neighbor] = new_time
                                heapq.heappush(heap, (new_time, neighbor, new_path))
                
                return False

            def draw(self, surface):
                # Draw connections
                for node in self.nodes:
                    for neighbor, data in node.connections.items():
                        color = COLORS['GRAY']
                        width = 2
                        if (node in self.path and neighbor in self.path and
                            abs(self.path.index(node) - self.path.index(neighbor)) == 1):
                            color = COLORS['YELLOW']
                            width = 4
                        pygame.draw.line(surface, color, (node.x, node.y), (neighbor.x, neighbor.y), width)
                        
                        mid_x = (node.x + neighbor.x) // 2
                        mid_y = (node.y + neighbor.y) // 2
                        dist_text = font.render(f"{data['distance']:.1f}", True, COLORS['BLACK'])
                        surface.blit(dist_text, (mid_x-10, mid_y-10))

                # Draw nodes
                for node in self.nodes:
                    selected = node in (self.start, self.end)
                    node.draw(surface, selected)

                # Draw info
                if self.path:
                    info = [
                        f"Path: {' → '.join(n.name for n in self.path)}",
                        f"Distance: {self.distance:.1f}",
                        f"Time: {self.time:.1f}"
                    ]
                    for i, text in enumerate(info):
                        text_surface = font.render(text, True, COLORS['BLACK'])
                        surface.blit(text_surface, (10, 10 + i*20))

        def create_graph():
            graph = Graph()
            spacing_x = WIDTH // (GRID_SIZE + 1)
            spacing_y = HEIGHT // (GRID_SIZE + 1)
            nodes = {}

            # Create nodes
            for row in range(GRID_SIZE):
                for col in range(GRID_SIZE):
                    x = (col + 1) * spacing_x
                    y = (row + 1) * spacing_y
                    name = f"{chr(65+row)}{col+1}"
                    node = Node(x, y, name)
                    graph.add_node(node)
                    nodes[(row, col)] = node

            # Connect nodes (each connects to 2 random neighbors)
            for (row, col), node in nodes.items():
                neighbors = []
                if row > 0: neighbors.append((row-1, col))
                if row < GRID_SIZE-1: neighbors.append((row+1, col))
                if col > 0: neighbors.append((row, col-1))
                if col < GRID_SIZE-1: neighbors.append((row, col+1))
                
                random.shuffle(neighbors)
                for r, c in neighbors[:2]:
                    if (r, c) in nodes and nodes[(r, c)] not in node.connections:
                        graph.connect(node, nodes[(r, c)])
            
            return graph

        graph = create_graph()
        running = True

        while running:
            screen.fill(COLORS['BACKGROUND'])
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    for node in graph.nodes:
                        if math.hypot(node.x-pos[0], node.y-pos[1]) <= NODE_RADIUS:
                            if event.button == 1:  # Left click
                                graph.start = node
                            elif event.button == 3:  # Right click
                                graph.end = node
                            graph.find_path()
                            break
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:  # Reset
                        graph = create_graph()
            
            graph.update_weights()
            graph.draw(screen)
            pygame.display.flip()
            await asyncio.sleep(0)
            clock.tick(30)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        pygame.quit()

# Run the game
asyncio.run(main())