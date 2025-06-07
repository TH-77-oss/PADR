from .player import Player
import random
from data.data import WAGON_COLORS
from collections import Counter

class AIPlayer(Player):
    def __init__(self, name, color, game, strategy):
        super().__init__(name, color, is_ai=True)
        self.game = game
        self.strategy = strategy

    def coups_possibles(self):
        return self.strategy.coups_possibles(self.game)

    def play_move(self):
        return self.strategy.play_move(self.game)

    def draw_objective(self):
        return self.strategy.draw_objective(self.game)

class RandomAIStrategy:
    def coups_possibles(self, game):
        player = game.current_player
        possible_moves = []

        # Pioche carte wagon face cachée
        if game.train_deck:
            possible_moves.append(("draw_train_card", None))

        # Pioche carte visible
        for idx, card in enumerate(game.visible_cards):
            possible_moves.append(("draw_visible_card", idx))

        # Pioche cartes destination
        if len(game.destinations) >= 3:
            possible_moves.append(("draw_destinations", None))

        cards_counter = Counter([c.lower() for c in player.train_cards])
        locos = cards_counter.get("locomotive", 0)
        print(f"[DEBUG] {player.name} a {len(player.train_cards)} cartes : {cards_counter}")

        for route in game.routes:
            city1, city2 = route.city1, route.city2
            length = route.length
            color = route.color.lower()

            if route.claimed_by is not None:
                print(f"[DEBUG] Route {city1} - {city2} déjà prise")
                continue

            if player.is_ai and route in player.destination_cards and self.is_route_useful(player, city1, city2):
                continue

            if len(player.train_cards) < length:
                continue

            if color == "gray":
                for c in WAGON_COLORS:
                    if c == "locomotive":
                        continue
                    count = cards_counter.get(c, 0)
                    if count + locos >= length:
                        print(f"[DEBUG] Peut revendiquer route {city1}-{city2} avec {c}: {count} + {locos} locos >= {length}")
                        possible_moves.append(("claim_route", (city1, city2, c, length)))
                        break
            else:
                count = cards_counter.get(color, 0)
                if count + locos >= length:
                    print(f"[DEBUG] Peut revendiquer route {city1}-{city2} avec {color}: {count} + {locos} locos >= {length}")
                    possible_moves.append(("claim_route", (city1, city2, color, length)))

        print(f"[DEBUG] {player.name} peut revendiquer :")
        for move in possible_moves:
            if move[0] == "claim_route":
                print("   ->", move)

        return possible_moves

    def play_move(self, game):
        player = game.current_player

        if len(player.destination_cards) == 0:
            game.draw_objectives()  # Ne pas return immédiatement

        possible_moves = self.coups_possibles(game)
        if not possible_moves:
            return

        move = random.choice(possible_moves)
        action, param = move

        if action == "draw_train_card":
            nb_tirages = random.randint(1, 2)
            for _ in range(nb_tirages):
                game.draw_card(0)

        elif action == "draw_visible_card":
            nb_tirages = random.randint(1, 2)
            for _ in range(nb_tirages):
                idx = random.randint(0, 4)
                game.draw_visible_card(idx, 0)

        elif action == "draw_destinations":
            game.draw_objectives()

        elif action == "claim_route":
            city1, city2, color, length = param
            for route in game.routes:
                if route.is_between(city1, city2) and route.claimed_by is None:
                    if player.is_ai and route in player.destination_cards and self.is_route_useful(player, city1, city2):
                        continue  # sécurité supplémentaire
                    game.claim_route(city1, city2, [route])
                    break

    def draw_objective(self, game):
        pass

    def is_route_useful(self, player, city1, city2):
        print(f"[DEBUG] Test utilité de la route {city1}-{city2}")
        for obj in player.destination_cards:
            print(f"[DEBUG] Objectif IA : {obj}")

        # Graphe des routes actuelles du joueur
        graph = {}
        for route in player.routes:
            c1, c2 = route.city1, route.city2
            graph.setdefault(c1, set()).add(c2)
            graph.setdefault(c2, set()).add(c1)

        # Ajout temporaire de la route candidate
        graph.setdefault(city1, set()).add(city2)
        graph.setdefault(city2, set()).add(city1)

        def dfs(start, end):
            visited = set()
            stack = [start]
            while stack:
                node = stack.pop()
                if node == end:
                    return True
                if node not in visited:
                    visited.add(node)
                    stack.extend(neigh for neigh in graph.get(node, []) if neigh not in visited)
            return False

        for obj in player.destination_cards:
            start = obj.get("city1")
            end = obj.get("city2")
            if not start or not end:
                continue

            if not dfs(start, end):
                if (start == city1 and end == city2) or (start == city2 and end == city1):
                    print(f"[DEBUG] -> Route {city1}-{city2} jugée UTILE (exact match)")
                    return True
                #print(f"[DEBUG] -> Route {city1}-{city2} jugée UTILE (intermédiaire)")
                #return True

        print(f"[DEBUG] -> Route {city1}-{city2} jugée INUTILE")
        return False


import heapq


# class OptiAIStrategy:
#     """
#         Cette classe a pour but de créer une stratégie qui
#         cherche le chemin le plus court par l'utilisation
#         de l'algorithme de Dijkstra
#     """
#     def __init__(self, game):
#         self.game = game
#
#     def is_route_useful(self, player, city1, city2):
#         # Construction du graphe actuel des routes du joueur
#         graph = {}
#         for route in player.routes:
#             city1 = route.city1
#             city2 = route.city2
#             graph.setdefault(city1, set()).add(city2)
#             graph.setdefault(city2, set()).add(city1)
#
#         # Ajout temporaire de la route candidate
#         graph.setdefault(city1, set()).add(city2)
#         graph.setdefault(city2, set()).add(city1)
#
#         # Fonction de recherche simple
#         def dfs(start, end):
#             visited = set()
#             stack = [start]
#             while stack:
#                 node = stack.pop()
#                 if node == end:
#                     return True
#                 if node not in visited:
#                     visited.add(node)
#                     stack.extend(neigh for neigh in graph.get(node, []) if neigh not in visited)
#             return False
#
#         # Vérifie chaque objectif complexe
#         for obj in player.destination_cards:
#             cities = obj.get("cities")
#             if not cities or len(cities) < 2:
#                 continue
#
#             for i in range(len(cities) - 1):
#                 start = cities[i]
#                 end = cities[i + 1]
#                 if not dfs(start, end):
#                     # Si ce lien n'existe pas encore, la route candidate pourrait aider à le compléter
#                     if (start == city1 and end == city2) or (start == city2 and end == city1):
#                         return True  # C'est exactement le lien manquant
#                     # Même si ce n'est pas le lien direct, peut-être que cette route crée un chemin intermédiaire
#                     # => donc on peut être conservateur et renvoyer True dès qu’un segment est incomplet
#                     return True
#
#         return False  # Tous les segments sont déjà complétés => cette route n’aide pas
#
#     def build_graph_from_routes(self, routes):  # Création du graphe utile pour l'implémentation de l'algo de Dijkstra
#         graph = {}
#         for route in routes:
#             c1, c2 = route.city1, route.city2
#             length = route.length
#             graph.setdefault(c1, []).append((c2, length))
#             graph.setdefault(c2, []).append((c1, length))  # car bidirectionnel
#         return graph
#
    # def dijkstra(self, graph, start, end):
    #     # Initialisation
    #     dist = {node: float('inf') for node in graph}
    #     dist[start] = 0
    #     prev = {node: None for node in graph}
    #     non_visites = dict(dist)
    #
    #     while non_visites:
    #         # Trouver le nœud non visité avec la plus petite distance
    #         courant = min(non_visites, key=lambda node: non_visites[node])
    #         if courant == end:
    #             break
    #
    #         for voisin, poids in graph[courant]:
    #             if voisin in non_visites:
    #                 nouvelle_dist = dist[courant] + poids
    #                 if nouvelle_dist < dist[voisin]:
    #                     dist[voisin] = nouvelle_dist
    #                     prev[voisin] = courant
    #                     non_visites[voisin] = nouvelle_dist
    #
    #         del non_visites[courant]
    #
    #     # Reconstruire le chemin
    #     chemin = []
    #     courant = end
    #     while courant is not None:
    #         chemin.insert(0, courant)
    #         courant = prev[courant]
    #
    #     path = []
    #     for i in range(len(chemin) - 1):
    #         path.append((chemin[i], chemin[i + 1]))
    #
    #     return path, dist[end]
#
#     def coups_possibles(self, game, graph, start, end, player):
#         chemin_opti, point = self.dijkstra(graph, start, end)
#         for chemin in chemin_opti:
#             length = chemin.length
#             city1, city2 = chemin
#             if chemin.claimed_by is not None:
#                 continue
#
#             # Vérifier si l'IA a assez de wagons
#             if len(player.train_cards) < length:
#                 continue
#
#             cards_counter = Counter([c.lower() for c in player.train_cards])
#             locos = cards_counter.get("locomotive", 0)
#             color = chemin.color.lower()
#             # Pour les routes grises
#             if color == "gray":
#                 for c in WAGON_COLORS:
#                     if c == "locomotive":
#                         continue
#                     count = cards_counter.get(c, 0)
#                     if count + locos >= length:
#                         self.game.claim_route(city1,city2, c)
#                         #possible_moves.append(("claim_route", (city1, city2, c, length)))
#                         #print(f"Route possible (gris): {city1}-{city2} avec {c} ({count}+{locos} locos)")
#                         break
#             else:
#                 # Pour les routes colorées
#                 count = cards_counter.get(color, 0)
#                 if count + locos >= length:
#                     self.game.claim_route(city1, city2, color)
#                     #possible_moves.append(("claim_route", (city1, city2, color, length)))
#                     #print(f"Route possible ({color}): {city1}-{city2}")

class OptiAIStrategy:
    def __init__(self):
        pass

    def build_graph_from_routes(self, routes):
        graph = {}
        for route in routes:
            c1, c2 = route.city1, route.city2
            length = route.length
            graph.setdefault(c1, []).append((c2, length))
            graph.setdefault(c2, []).append((c1, length))
        return graph

    def dijkstra(self, graph, start, end):
        dist = {node: float('inf') for node in graph}
        dist[start] = 0
        prev = {node: None for node in graph}
        non_visites = dict(dist)

        while non_visites:
            courant = min(non_visites, key=lambda node: non_visites[node])
            if courant == end:
                break

            for voisin, poids in graph[courant]:
                if voisin in non_visites:
                    nouvelle_dist = dist[courant] + poids
                    if nouvelle_dist < dist[voisin]:
                        dist[voisin] = nouvelle_dist
                        prev[voisin] = courant
                        non_visites[voisin] = nouvelle_dist

            del non_visites[courant]

        chemin = []
        courant = end
        while courant is not None:
            chemin.insert(0, courant)
            courant = prev[courant]

        path = []
        for i in range(len(chemin) - 1):
            path.append((chemin[i], chemin[i + 1]))

        return path, dist[end]

    def play_move(self, game):
        player = game.current_player

        print("\nNouveau tour de l'IA")
        print(f"Cartes wagon du joueur : {player.train_cards}")
        print(f"Objectifs actuels : {player.destination_cards}")

        if not player.destination_cards:
            print("Pas d'objectif : pioche de nouveaux objectifs")
            game.draw_objectives()
            return

        graph_all_routes = self.build_graph_from_routes(game.routes)

        for objective in player.destination_cards:
            print(f"\nObjectif : {objective}")
            cities = [objective.get("city1"), objective.get("city2")]
            if None in cities:
                print("Objectif invalide (villes manquantes)")
                continue

            start, end = cities
            path, dist_tot = self.dijkstra(graph_all_routes, start, end)
            print(f"Chemin optimal : {path} (distance : {dist_tot})")

            for i in range(len(path)):
                city1 = path[i][0]
                city2 = path[i][1]

                route = next(
                    (r for r in game.routes if r.is_between(city1, city2) and r.claimed_by is None), None
                )
                if not route:
                    print(f"Route {city1} - {city2} déjà prise ou inexistante")
                    continue

                length = route.length
                color = route.color.lower()
                cards_counter = Counter([c.lower() for c in player.train_cards])
                locos = cards_counter.get("locomotive", 0)

                print(f"Tentative de revendication : {city1} - {city2} ({color}, {length})")

                if len(player.train_cards) < length:
                    print("Pas assez de cartes")
                    continue

                if color == "gray":
                    for c in WAGON_COLORS:
                        if c == "locomotive":
                            continue
                        count = cards_counter.get(c, 0)
                        if count + locos >= length:
                            print(f"Revendication réussie en utilisant {c} + locos")
                            game.claim_route(city1, city2, [route])
                            return
                else:
                    count = cards_counter.get(color, 0)
                    if count + locos >= length:
                        print(f"Revendication réussie en {color} + locos")
                        game.claim_route(city1, city2, [route])
                        return

        print("Aucune route revendiquée : l'IA pioche 2 cartes wagon")
        drawn = 0
        while drawn < 2 and game.train_deck:
            game.draw_card(0)
            drawn += 1

    def draw_objective(self, game):
        game.draw_objectives()

