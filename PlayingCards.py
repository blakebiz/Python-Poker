import termcolor

class Card:
    def __init__(self, card, suit, symbols=True):
        self.symbols = symbols
        if symbols:
            self.syms = {'spades': '♠', 'hearts': '♥', 'diamonds': '♦', 'clubs': '♣'}
        self.rankings = {'2':1, '3':2, '4':3, '5':4, '6':5, '7':6, '8':7, '9':8, '10':9, 'J':10, 'Q':11, 'K':12, 'A':13}
        self.card = card
        self.suit = suit

    def __gt__(self, other):
        return self.rankings[self.card] > self.rankings[other.card]

    def __ge__(self, other):
        return self.rankings[self.card] >= self.rankings[other.card]

    def __lt__(self, other):
        return self.rankings[self.card] < self.rankings[other.card]

    def __le__(self, other):
        return self.rankings[self.card] <= self.rankings[other.card]

    def __eq__(self, other):
        return self.card == other.card

    def __ne__(self, other):
        return self.card != other.card

    def __str__(self):
        if self.symbols:
            if self.suit in {'spades', 'clubs'}:
                return termcolor.colored(f'{self.card} of {self.syms[self.suit]}', 'white')
            return termcolor.colored(f'{self.card} of {self.syms[self.suit]}', 'red')
        return f'{self.card} of {self.suit}'

    def __repr__(self):
        if self.symbols:
            if self.suit in {'spades', 'clubs'}:
                return termcolor.colored(f'{self.card} of {self.syms[self.suit]}', 'white')
            return termcolor.colored(f'{self.card} of {self.syms[self.suit]}', 'red')
        return f'{self.card} of {self.suit}'

    def get_rank(self):
        return self.rankings[self.card]

    def strict_in(self, list):
        for card in list:
            if card.card == self.card and card.suit == self.suit:
                return True
        return False