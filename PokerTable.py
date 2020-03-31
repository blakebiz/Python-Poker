


class Table:
    def __init__(self, min, turn, player_count, full=True):
        if full:
            self.min, self.level, self.last_raise, self.raised, self.cards, self.player_count = min, 0, 0, False, [], player_count
        self.turn = turn

    def __str__(self):
        return str(self.cards)

    def __repr__(self):
        return str(self.cards)

    def next_turn(self):
        if self.turn >= self.player_count - 1:
            self.turn = 0
        else:
            self.turn += 1



