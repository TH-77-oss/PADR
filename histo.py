from game import Game
from datetime import datetime

class Historique:
    """
    Auteur : Dubedout Thomas
    Cette classe écrit les informations d'une partie dans un fichier texte
    pour conserver un historique.
    """

    def __init__(self, game: Game):
        self.game = game
        self.difficulty = game.difficulty
        self.players = game.players
        self.date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def ecriture_partie(self, txt):
        with open(txt, "a") as file:
            file.write(f"\n--- Partie du {self.date} ---\n")
            file.write(f"Difficulte : {self.difficulty}\n")

            for i, player in enumerate(self.players):
                score = player.score
                objectifs_reussis=len(player.accomplished_objectives)

                file.write(
                    f"Joueur {i + 1} : {player.name} - Score : {score} - "
                    f"Objectifs reussis : {objectifs_reussis}\n"
                )

            winner = max(self.players, key=lambda p: p.score)
            file.write(f"Gagnant : {winner.name} avec {winner.score} points\n")
            file.write("\n")


