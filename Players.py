

class Player:
    def __init__(self, hand, name, bank):
        self.hand, self.name, self.bank, self.share = hand, name, bank, 0

    def bet(self, amt):
        if amt > self.bank:
            self.share += self.bank
            bnk = self.bank
            self.bank = 0
            return bnk
        self.bank -= amt
        self.share += amt
        return amt


    def __repr__(self):
        return f'{self.name}, {self.bank}, {self.share}'

