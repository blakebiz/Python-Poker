import random
from PlayingCards import Card
from Players import Player
from PokerTable import Table

class Turn:
    def __init__(self, turn=0):
        self.turn = turn

class Poker:

    # Game Initiation

    def __init__(self, shuffle=False):
        self.suits = ['spades', 'clubs', 'hearts', 'diamonds']
        self.cards = ['2', '3', '4', '5', '6', '7', '8' ,'9', '10', 'J', 'Q', 'K', 'A']
        self.ranks = [self.check_royal_flush, self.check_straight_flush, self.check_four, self.check_FH,
                      self.check_flush, self.check_straight, self.check_three, self.check_two_pair, self.check_two]
        if shuffle: self.shuffle()

    def shuffle(self):
        self.deck = list()
        for suit in self.suits:
            for card in self.cards:
                self.deck.append(Card(card, suit))

    def start_game(self, player_count=3, starting_money=1000, starting_bid=None, small_blind=None, linear=True,
                   increasing=0, inc_per_x_rounds=3):
        players = [Player([], f'Player {x}', starting_money) for x in range(player_count)]
        if small_blind == None:
            small_blind = random.randint(0, player_count-1)
        turn = Turn(small_blind)
        playing = True
        round_count = 0
        while playing:
            self.start_round(players, turn)

            if round_count != 0 and round_count % inc_per_x_rounds == 0:
                if linear:
                    starting_bid += increasing
                elif increasing != 0:
                    starting_bid *= increasing
            round_count += 1
            if len(players) < 2:
                playing = False
        print(f'Congratulations {players[0].name}, you won and are taking home ${players[0].bank}!')

    def start_round(self, players, turn, starting_bid=10):
        status = {'actives': [], 'inactives': []}
        for player in players:
            player.share = 0
            status['actives'].append(player)
        # Initialization
        hand_size = 2
        flop_size = 3
        self.shuffle()

        # Deal hands
        for _ in range(hand_size):
            for player in players:
                player.hand.append(self.draw())

        # Establish table
        table = Table(starting_bid, turn.turn, len(players))

        # Take first bets
        print('Now taking first Bets')
        print(f'Small blind is {starting_bid//2}, paid by {players[table.turn].name}')
        table.level = players[table.turn].bet(starting_bid//2)
        table.next_turn()
        print(f'Big blind is {starting_bid}, paid by {players[table.turn].name}')
        big = players[table.turn].bet(starting_bid)
        if big > table.level:
            table.level = big
        table.next_turn()

        # First turn
        self.take_bets(status, table)
        print()

        # Flop
        for _ in range(flop_size):
            table.cards.append(self.draw())
        print(f'The Flop: {table}\n')

        # Flop bets
        self.take_bets(status, table)
        print()

        # Turn
        table.cards.append(self.draw())
        print(f'The Turn: {table}\n')

        # Turn bets
        self.take_bets(status, table)
        print()

        # River
        table.cards.append(self.draw())
        print(f'The River: {table}\n')

        # River bets
        self.take_bets(status, table)
        print()

        # Figure out splitting pay
        winners = self.find_winner(table, players)
        total_bids = 0
        for i in range(len(status['actives'])):
            status['inactives'].append(status['actives'].pop())
        shares = []
        for winner in winners['winners']:
            shares.append(winner[0].share)
        checking = True
        while checking:
            for i, winner in enumerate(winners['winners']):
                winner[0].reward = 0
                for player in status['inactives']:
                    if player.share > 0:
                        share = shares[i] / len(winners)
                        winner[0].reward += share
                        player.share -= share
            checking = False
            for player in status['inactives']:
                if player.share > 0:
                    checking = True
        for winner in winners['winners']:
            print(f'Player {winner[0].name} won {winner[0].reward} with {winner[1]} for a {winners["win_condition"]}')
            winner[0].bank += winner[0].reward
        i = 0
        while i < len(players):
            if players[i].bank <= 0:
                if i < turn.turn:
                    turn.turn -= 1
                player = players.pop(i)
                table.player_count -= 1
                print(f'Player {player.name} went broke! Thank you for playing.')
            else:
                i += 1











    # Hand rankings

    def check_royal_flush(self, hand):
        royalty = ['10', 'J', 'Q', 'K', 'A']
        suits = dict()
        cards = []
        for suit in self.suits:
            suits[suit] = []
        for card in hand:
            suits[card.suit].append(card)

        for suit in suits.values():
            if len(suit) >= 5:
                for card in suit:
                    if card.card in royalty:
                        royalty.remove(card.card)
                        cards.append(card)
        if len(royalty) == 0:
            return cards
        return False

    def check_straight_flush(self, hand):
        flush = self.check_flush(hand)
        if flush:
            return self.check_straight(sorted(flush))

    def check_straight(self, hand):
        cons = self.getConsecutives(sorted(hand))
        for con in cons:
            if len(con) > 4:
                return con
        return False

    def check_flush(self, hand):
        suits = self.split_by_suits(hand)
        for value in suits.values():
            if len(value) >= 5:
                return value
        return False

    def check_FH(self, hand):
        pairs = self.get_pairs(hand, count=2)
        if pairs == False:
            return False
        pair3, pair2 = False, False
        for pair in pairs:
            if len(pair) == 3:
                pair3 = pair
            if len(pair) == 2:
                pair2 = pair
        if pair2 == False or pair3 == False:
            return False
        return pair3, pair2

    def check_four(self, hand):
        return self.get_pairs(hand, count=4)


    def check_three(self, hand):
        return self.get_pairs(hand, count=3)

    def check_two(self, hand):
        return self.get_pairs(hand, count=2)

    def check_two_pair(self, hand):
        return self.get_pairs(hand, count=2)

    def split_by_suits(self, hand):
        suits = {'spades': [], 'clubs': [], 'diamonds': [], 'hearts': []}
        for card in hand:
            suits[card.suit].append(card)
        return suits

    # Finding a winner

    def find_winner(self, table, players):
        win_conditions = ['Royal Flush', 'Straight Flush', 'Four of a Kind', 'Full House', 'Flush', 'Straight',
                          'Three of a Kind', 'Two Pairs', 'Pair', 'High Card']
        passed = []
        for ind, rank in enumerate(self.ranks):
            for player in players:
                ptable = table.cards.copy()
                ptable.extend(player.hand)
                if rank(ptable):
                    passed.append(player)
                    index = ind
            if len(passed) > 0:
                break
        if len(players) == 0:
            return {'winners': self.nothing_winners(table, passed), 'win_condition': win_conditions[index]}
        elif len(players) == 1:
            return {'winners': [passed, self.check_royal_flush(passed)], 'win_condition': win_conditions[index + 1]}
        elif index == 0:
            return passed
        else:
            checks = [self.sf_winners, self.fok_winners, self.fh_winners, self.flush_winners, self.straight_winners,
                      self.three_winners, self.tp_winners, self.pair_winners]

            return {'winners': checks[index-1](table, passed), 'win_condition': win_conditions[index]}

    def sf_winners(self, table, passed):
        best = 0
        for player in passed:
            ptable = table.cards.copy()
            ptable.extend(player.hand)
            largest = self.check_straight_flush(ptable)

            if largest[-1].get_rank() > best:
                winners = [[player, largest]]
                best = largest.get_rank()
            elif largest[-1].get_rank() == best:
                winners.append([player, largest])
        return winners

    def fok_winners(self, table, passed):
        best = 0
        for player in passed:
            ptable = table.cards.copy()
            ptable.extend(player.hand)
            four = self.check_four(ptable)
            if four[0].get_rank() > best:
                high = 0
                for card in ptable:
                    if card.get_rank() > high and card not in four[0]:
                        high = card.get_rank()
                        highest = card
                four.append(highest)
                winners = [[player, four]]
                best = four[0].get_rank()
        return winners

    def fh_winners(self, table, passed):
        best = 0
        for player in passed:
            ptable = table.cards.copy()
            ptable.extend(player.hand)
            fh = self.check_FH(ptable)
            for cards in fh:
                if len(cards) == 3:
                    if cards[0].get_rank() > best:
                        winners = [[player, fh]]
                        best = cards[0].get_rank()
                    elif cards[0].get_rank() == best:
                        winners.append([player, fh])
        if len(winners) > 1:
            best = 0
            for player in winners:
                for pairs in player[1]:
                    if len(pairs) == 2:
                        if pairs[0].get_rank() > best:
                            best = pairs[0].get_rank()
                            wins = [player]
                        elif pairs[0].get_rank() == best:
                            wins.append(player)
            return wins
        return winners

    def flush_winners(self, table, passed):
        best = 0
        for player in passed:
            ptable = table.cards.copy()
            ptable.extend(player.hand)
            flush = sorted(self.check_flush(ptable))
            if flush[-1].get_rank() > best:
                winners = [[player, flush]]
                best = flush[-1].get_rank()
            elif flush[-1].getrank() == best:
                winners.append(best)
        if len(winners) > 1:
            for hand in range(5, 0, -1):
                best = 0
                for player in winners:
                    if player[1][0-hand].get_rank() > best:
                        best = player[1][0-hand].get_rank()
                        wins = [player]
                    elif player[1][0-hand].get_rank() == best:
                        wins.append(player)
                if len(wins) == 1:
                    break
            return wins
        return winners

    def straight_winners(self, table, passed):
        best = 0
        for player in passed:
            ptable = table.cards.copy()
            ptable.extend(player.hand)
            straight = self.check_straight()
            if isinstance(straight[-1], list):
                high = straight[-1][0]
            else:
                high = straight[-1]
            if high.get_rank() > best:
                best = high.get_rank()
                winners = [[player, straight]]
            elif high.get_rank() == best:
                winners.append([player, straight])
        return winners

    def three_winners(self, table, passed):
        best = 0
        for player in passed:
            ptable = table.cards.copy()
            ptable.extend(player.hand)
            three = self.check_three(ptable)
            other_high = sorted(self.get_highest(ptable, exclude_num=three[0]))
            if other_high[-1].get_rank() > best:
                best = other_high[-1].get_rank()
                three.extend(other_high)
                winners = [[player, three]]
            elif other_high[-1].get_rank() == best:
                three.extend(other_high)
                winners.append([player, three])
        return winners

    def tp_winners(self, table, passed):
        winners = []
        for player in passed:
            ptable = table.cards.copy()
            ptable.extend(player.hand)
            pairs = self.get_pairs(ptable)
            topTwo = []
            for _ in range(2):
                best = 0
                for pair in pairs:
                    if pair[0].get_rank() > best:
                        best = pair[0].get_rank()
                        winner = pair
                topTwo.append(winner)
            winner = topTwo[0].copy()
            winner.extend(topTwo[1])
            winner.extend(self.get_highest(ptable, count=1, exclude_num=winner))
            if len(winners) == 0:
                winners.append([player, winner])
            else:
                new_high, new_low = winner[:2], winner[2:4]
                old_high, old_low = winners[0][1][:2], winners[0][1][2:4]
                if new_high[0] > old_high[0] or new_low[0] > old_low[0] or winner[4] > winners[0][1][4]:
                    winners = [[player, winner]]
                else:
                    winners.append([player, winner])
        return winners

    def pair_winners(self, table, passed):
        best = 0
        winners = []
        for player in passed:
            ptable = table.cards.copy()
            ptable.extend(player.hand)
            pair = self.get_pairs(ptable)[0]
            if pair[0].get_rank() > best:
                best = pair[0].get_rank()
                winner = pair
                winner.extend(self.get_highest(ptable, count=3, exclude_num=pair))
                if len(winners) == 0:
                    winners.append([player, winner])
                else:
                    for ind, card in enumerate(winners[0][1][2:]):
                        if winner[ind+2] > card:
                            winners = [[player, winner]]
                            break
                        elif winner[ind+2] < card:
                            break
                    else:
                        winners.append([player, winner])
        return winners

    def nothing_winners(self, table, passed):
        winners = []
        for player in passed:
            ptable = table.cards.copy()
            ptable.extend(player.hand)
            winner = self.get_highest(ptable, 5)
            if len(winners) == 0:
                winners.append([player, winner])
            else:
                for ind, card in enumerate(winners[0][1]):
                    if winner[ind] > card:
                        winners = [[player, winner]]
                        break
                    elif winner[ind] < card:
                        break
                else:
                    winners.append([player, winner])
        return winners




    # Helper functions

    def draw(self):
        return self.deck.pop(random.randint(0, len(self.deck) - 1))

    def choose_hand(self, size):
        return random.sample(self.deck, size)

    def getConsecutives(self, cards):
        tracking = False
        track = []
        results = []
        for ind, card in enumerate(cards):
            try:
                if not tracking:
                    if card.get_rank() + 1 == cards[ind + 1].get_rank():
                        tracking = True
                        if len(track) == 0:
                            track.extend(cards[ind:ind + 2])
                        else:
                            track.append(cards[ind + 1])
                    elif card.get_rank() == cards[ind + 1].get_rank():
                        if len(track) == 0:
                            track.append([card, cards[ind + 1]])
                        else:
                            track[0].append(cards[ind + 1])

                else:
                    if card.get_rank() + 1 == cards[ind + 1].get_rank():
                        track.append(cards[ind + 1])
                    elif card.get_rank() == cards[ind + 1].get_rank():
                        if isinstance(track[-1], list):
                            track[-1].append(cards[ind + 1])
                        else:
                            track[-1] = [track[-1], cards[ind + 1]]
                    else:
                        tracking = False
                        results.append(track)
                        track = []
            except IndexError:
                if len(track) > 0:
                    results.append(track)
        return results

    def get_pairs(self, hand, count=2):
        cards = dict()
        for card in hand:
            if card.card not in cards:
                cards[card.card] = [card]
            else:
                cards[card.card].append(card)
        results = [x for x in cards.values() if len(x) > count-1]
        if len(results) > 0:
            return results
        return False

    def get_highest(self, hand, count=1, exclude_num=None, exclude=None):
        highest = []
        hand = hand.copy()
        while len(highest) < count and len(hand) > 0:
            high = 0
            for card in hand:
                if card.get_rank() > high:
                    passed = True
                    if exclude_num:
                        if card in exclude_num:
                            passed = False
                    if exclude:
                        if card.strict_in(exclude):
                            passed = False
                    if passed:
                        high = card.get_rank()
                        winner = card
            hand.remove(winner)
            highest.append(winner)
        return highest

    def ask_move(self, player, table):
        if player.bank < 1:
            return -2
        print(f'\nWhat would you like to do, {player.name}?')
        print(f'(Your hand: {player.hand}, your bank: {player.bank}, currently invested in pot: {player.share})')
        while True:
            if table.raised:
                low = table.last_raise * 2
            else:
                low = table.min
            if player.share == table.level:
                if player.bank > 0:
                    choice = input(f'Check, Fold, or Raise (min raise: {low}): ').split()
                    if len(choice) == 0:
                        print('Error, invalid input!')
                    elif choice[0].lower() == 'check':
                        return 0
                    elif choice[0].lower() == 'fold':
                        return -1
                    elif choice[0].lower() == 'raise' or choice[0].lower() == 'all' or choice[0].lower() == 'bet':
                        if len(choice) == 1:
                            print('Error, invalid input!')
                        elif choice[1].lower() == 'all' or choice[0].lower() == 'all':
                            return player.bank
                        elif choice[1].isnumeric():
                            bet = int(choice[1])
                            if bet > player.bank:
                                print("You don't have that much money!")
                            elif bet >= low:
                                return bet
                            else:
                                print(f'Bet must be at least {low}')
                        else:
                            print('Error, invalid input!')
                    else:
                        print('Invalid input, input options are "Check", "Fold", "Raise <amount>", "Raise all", "All in", Call')
                else:
                    return -2
            else:
                if player.bank > 0:
                    gap = table.level - player.share
                    if player.bank - gap > 0:
                        choice = input(f'Call, Fold, or Raise (min raise: {low}): ').split()
                        if choice[0].lower() == 'call':
                            return gap
                        elif choice[0].lower() == 'fold':
                            return -1
                        elif choice[0].lower() == 'raise' or choice[0].lower() == 'all':
                            if choice[1].lower() == 'all' or choice[0].lower() == 'all':
                                return player.bank
                            elif choice[1].isnumeric():
                                bet = int(choice[1])
                                if bet + gap > self.bank:
                                    print("You don't have that much money!")
                                elif bet >= low:
                                    return bet + gap
                                else:
                                    print(f'Bet must be at least {low}')
                            else:
                                print('Error, invalid input!')

                    else:
                        choice = input(f'Fold or All in for {player.bank}: ').split()
                        if choice[0].lower() == 'fold':
                            return -1
                        elif choice[0].lower() == 'all' or choice[0].lower() == 'raise':
                            return player.bank
                        else:
                            print('Invalid input, input options are "Fold", or "All in"')
                else:
                    return -2


    def take_bets(self, status, table):
        for _ in range(len(status['actives'])):
            player = status['actives'][table.turn]
            owed = table.level - player.share
            move = self.ask_move(player, table)
            if move == -1:
                print(f'Player {player.name} folds.')
                status['inactives'].append(status['actives'].pop(table.turn))
            elif move == 0:
                print(f'Player {player.name} checks.')
            elif move > 0:
                if move == owed:
                    print(f'Player {player.name} calls for {move}.')
                    player.bet(move)
                elif move < owed:
                    print(f'Player {player.name} is all in for {move}.')
                    player.bet(move)
                else:
                    print(f'Player {player.name} Raises for {move - owed}.')
                    table.raised = True
                    table.last_raise = move - owed
                    player.bet(move)
                    table.level += (move - owed)
            table.next_turn()

            print()
        table.raised = False
        table.last_raise = None