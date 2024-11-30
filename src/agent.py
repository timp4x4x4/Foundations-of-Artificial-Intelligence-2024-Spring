from game.players import BasePokerPlayer
import random
import joblib
import os

pre_flop_win_rates = {
    'AA': 0.85, 'KK': 0.82, 'QQ': 0.80, 'JJ': 0.77, 'TT': 0.75, '99': 0.73, '88': 0.70, '77': 0.68, '66': 0.65, '55': 0.62,
    '44': 0.60, '33': 0.57, '22': 0.55,
    'AKs': 0.67, 'AQs': 0.65, 'AJs': 0.63, 'ATs': 0.61, 'A9s': 0.59, 'A8s': 0.57, 'A7s': 0.55, 'A6s': 0.53, 'A5s': 0.52, 'A4s': 0.50, 'A3s': 0.49, 'A2s': 0.48,
    'KQs': 0.55, 'KJs': 0.54, 'KTs': 0.53, 'QJs': 0.52, 'QTs': 0.51, 'JTs': 0.50,
    'AK': 0.64, 'AQ': 0.62, 'AJ': 0.60, 'AT': 0.58, 'A9': 0.56, 'A8': 0.54, 'A7': 0.52, 'A6': 0.50, 'A5': 0.49, 'A4': 0.48, 'A3': 0.47, 'A2': 0.46,
    'KQ': 0.51, 'KJ': 0.50, 'KT': 0.49, 'QJ': 0.48, 'QT': 0.47, 'JT': 0.46,
    'K9s': 0.49, 'Q9s': 0.48, 'J9s': 0.47, 'T9s': 0.46, '98s': 0.45, '87s': 0.44, '76s': 0.43, '65s': 0.42, '54s': 0.41, '43s': 0.40, '32s': 0.39,
    'K9': 0.48, 'Q9': 0.47, 'J9': 0.46, 'T9': 0.45, '98': 0.44, '87': 0.43, '76': 0.42, '65': 0.41, '54': 0.40, '43': 0.39, '32': 0.38,
    # ... Continue filling in more combinations as needed ...
}

suits = ['D', 'H', 'S', 'C']
ranks = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
        
deck_of_cards = [rank + suit for suit in suits for rank in ranks]

def transform_number(card_num):
    if card_num == 'A':
        card_num = '1'
    elif card_num == 'T':
        card_num = '10'
    elif card_num == 'J':
        card_num = '11'
    elif card_num == 'Q':
        card_num = '12'
    elif card_num == 'K':
        card_num = '13'
    return int(card_num)
def community(community_): # if 1 means it is 亂
    kinds = {}
    numbers = []
    for card in community_:
        if card[0] not in list(kinds.keys()):
            kinds[card[0]] = 1
        else:
            kinds[card[0]] += 1
        
        numbers.append(transform_number(card[1]))
        numbers = sorted(numbers)
        gap = 0
        for i in range(1, len(numbers)):
            gap += numbers[i] - numbers[i-1]
        gap_rate = gap / 12
        kind_rate = len(kinds) / 4
        
        return gap_rate * kind_rate
        
def first_round_win_rate(hole_cards):
    # Extract ranks and suits
    rank1, suit1 = hole_cards[0][1], hole_cards[0][0]
    rank2, suit2 = hole_cards[1][1], hole_cards[1][0]
    
    # Sort the hole cards by rank for consistency
    if rank1 < rank2:
        rank1, rank2 = rank2, rank1
        suit1, suit2 = suit2, suit1
    
    # Check if the hole cards are suited
    suited = suit1 == suit2
    hole_cards_key = rank1 + rank2 + ('s' if suited else '')

    # Check for the reverse combination if not suited
    reverse_hole_cards_key = None
    if not suited:
        reverse_hole_cards_key = rank2 + rank1
    
    # Return the pre-computed win rate if available, otherwise a default value
    return 100 * pre_flop_win_rates.get(hole_cards_key, pre_flop_win_rates.get(reverse_hole_cards_key, 0.50))

def can_form_straight(cards):
    ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K']
    need = []
    for i in range(len(ranks)-4):
        sub_rank = ranks[i:i+5]
        set1 = set(sub_rank)
        set2 = set(cards)

        # Find elements that are in set1 or set2 but not both
        different_elements = set1.symmetric_difference(set2)
        if len(different_elements) == 1 and different_elements[0] not in need:
            need.append(different_elements[0])
    return need
        
    
def compute_win_rate(state):
    print("Computing win rate for state:", state)  # Debugging output

    if len(state[1]) == 0:  # first round
        win_rate = first_round_win_rate(state[0])
        print("First round win rate:", win_rate)  # Debugging output
        return win_rate
    else:  # preflop
        kinds = {}
        numbers = {}
        possible_hit = []
        combine = state[0] + state[1]
        
        # Count kinds and numbers
        for card in combine:
            if card[0] not in kinds.keys():
                kinds[card[0]] = 1
            else:
                kinds[card[0]] += 1
            
            if card[1] not in numbers.keys():
                numbers[card[1]] = 1
            else:
                numbers[card[1]] += 1
        
        print("Kinds:", kinds)  # Debugging output
        print("Numbers:", numbers)  # Debugging output
        
        max_kind_key = max(kinds, key=kinds.get)
        max_kind_value = kinds[max_kind_key]
        
        max_num_key = max(numbers, key=numbers.get)
        max_num_value = numbers[max_num_key]
        
        iHave = 0
        for card in state[0]:
            if card[0] == max_kind_key:
                iHave += 1
        
        print("Max kind key:", max_kind_key, "Max kind value:", max_kind_value, "iHave:", iHave)  # Debugging output
        
        if max_kind_value == 5:
            return 99
        elif max_kind_value == 4:
            possible_hit += [card for card in deck_of_cards if card not in combine and card[0] == max_kind_key]
        
        possible_cards = can_form_straight(combine)
        if len(possible_cards) != 0:
            possible_hit += [card for card in possible_cards if card not in possible_hit]
            print("Possible hit cards:", possible_hit)  # Debugging output
        print('Done')
        community_situation = community(state[1])
        print("Community situation:", community_situation)  # Debugging output
        
        if len(state[1]) == 3:
            if len(possible_hit) == 0:
                two_pair = 0
                for key in numbers.keys():
                    if numbers[key] >= 2:
                        two_pair += 1
                
                if max_num_value == 3:
                    return 80
                print("Two pair count:", two_pair)  # Debugging output
                if two_pair >= 2:
                    return 70
                elif state[0][0][1] == state[0][1][1]:  # one pair on hand
                    return 60
            
            return len(possible_hit) * 4
        elif len(state[1]) == 4:
            if len(possible_hit) == 0: 
                two_pair = 0
                for key in numbers.keys():
                    if numbers[key] >= 2:
                        two_pair += 1
                        
                if max_num_value == 3:
                    return 70        
                print("Two pair count:", two_pair)  # Debugging output
                if two_pair >= 2:
                    return 60
                elif state[0][0][1] == state[0][1][1]:  # one pair on hand
                    return 50
            
            return len(possible_hit) * 2
        else:
            sorted_ranks = sorted(numbers.keys())
            cnt = 0
            for i in range(1, len(sorted_ranks)):
                if transform_number(sorted_ranks[i]) - transform_number(sorted_ranks[i-1]) == 1:
                    cnt += 1
                    if cnt == 4:
                        break
                else:
                    cnt = 0
            print("Straight count:", cnt)  # Debugging output
            if cnt == 4 and max_kind_value == 5:
                return 99
            elif cnt == 4:
                return 70
            
            iHit = 0
            for card in state[0]:
                if card[0] == max_kind_key:
                    iHit += 1
            if max_kind_value == 3 and iHit >= 1:
                return 60
            elif max_kind_value == 4 and iHit >= 2:
                return 95
            elif max_kind_value == 4 and iHit >= 1:
                return 80

            two_pair = 0
            for key in numbers.keys():
                if numbers[key] >= 2:
                    two_pair += 1
                    
            print("Two pair count:", two_pair)  # Debugging output
            if two_pair >= 2:
                return 50
            elif state[0][0][1] == state[0][1][1]:  # one pair on hand
                return 40
        
            return 0
            
class AiPlayer(BasePokerPlayer):
    def __init__(self, learning_rate=0.5, discount_factor=0.9, exploration_rate=1.0, exploration_decay=0.5):
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        self.exploration_decay = exploration_decay
        self.q_table = {}
        
        self.hand = []
        self.community_cards = []
        self.my_action = 'call'
        self.actions = ['fold', 'call', 'raise']
        self.win_rate = 0
        self.rate_str = ''   
        self.opponent = 'fold'
        self.oppo_raise = 0

    def update_exploration_rate(self):
        self.exploration_rate *= self.exploration_decay
        
    def choose_action(self, win_rate):
        if random.uniform(0, 1) < self.exploration_rate:
            # Explore by randomly choosing an action
            if win_rate < 40:
                action = 'fold'
            elif win_rate < 90:
                action = 'call'
            else:
                action = 'raise'
            print(f"Exploring: Win rate = {win_rate}, Choosing action: {action}")
            return action
        else:
            # Exploit by choosing the action with the highest Q-value
            if self.rate_str not in self.q_table:
                self.q_table[self.rate_str] = {action: 0 for action in self.actions}
            
            max_action = max(self.q_table[self.rate_str], key=self.q_table[self.rate_str].get)
            print(f"Exploiting: Win rate = {win_rate}, Choosing action: {max_action}")
            return max_action
    
    def learn(self, reward):
        state_str = self.rate_str
        if state_str not in self.q_table:
            self.q_table[state_str] = {'fold': 0, 'call': 0, 'raise': 0}
        
        td_target = reward
        td_error = td_target - self.q_table[state_str][self.my_action]
        self.q_table[state_str][self.my_action] += self.learning_rate * td_error
        print(f"Learning: Reward = {reward}, TD error = {td_error}, Q-value updated: {self.q_table[state_str]}")

    def update_exploration_rate(self):
        self.exploration_rate *= self.exploration_decay
        print(f"Exploration rate updated: {self.exploration_rate}")
        
    def declare_action(self, valid_actions, hole_card, round_state):
        try:
            print("Declared Started:")
            state = (hole_card, round_state['community_card'])
            win_rate = compute_win_rate(state)
            self.rate_str += f'{win_rate} | '
            self.my_action = self.choose_action(win_rate)

            amount = 0
            for action_info in valid_actions:
                if action_info['action'] == self.my_action:
                    amount = action_info['amount']
                    break

            if isinstance(amount, dict):
                amount = amount['min']

            fold_amount = amount
            
            if self.my_action == 'raise':
                amount = 5 * win_rate

            index = 0
            if self.my_action == 'fold':
                index = 0
            elif self.my_action == 'call':
                index = 1
            else:
                index = 2

            if win_rate == 0:
                if self.opponent == 'raise':
                    index, amount = 0, 0

            if self.opponent == "raise" and self.oppo_raise >= 300 and win_rate <= 90:
                index, amount = 0, 0 
            
            if win_rate != 0 and index == 0:
                if win_rate >= 40:
                    index, amount = 1, fold_amount
                    
            if index == 0 or index == 0:
                amount = 0         
            self.win_rate = win_rate
            print(f"Action declared: Action = {self.my_action}, Amount = {amount}, Win rate = {win_rate}")
            return valid_actions[index]["action"], amount
        except Exception as e:
            print("Error in declare_action:", e)
            return 'fold', 0


    def receive_game_start_message(self, game_info):
        self.load_model('q_learning_model.pkl')

    def receive_round_start_message(self, round_count, hole_card, seats):
        self.hand = hole_card
        self.hand = hole_card
        self.community_cards = []
        self.my_action = 'call'
        self.actions = ['fold', 'call', 'raise']
        self.win_rate = 0
        self.rate_str = ''
        self.opponent = 'fold'
        self.oppo_raise = 0

    def receive_street_start_message(self, street, round_state):
        self.street = street

    def receive_game_update_message(self, action, round_state):
        self.opponent = 'fold'
        self.oppo_raise = 0
        
        self.community_cards = round_state['community_card']
        self.opponent = action['action']
        if self.opponent == 'raise':
            self.oppo_raise = action['amount']
        
    def receive_round_result_message(self, winners, hand_info, round_state):
        round_cnt = round_state['round_count']
        
        strength_reward = {
            'HIGH_CARD': 1,
            'ONE_PAIR': 2,
            'TWO_PAIR': 3,
            'THREE_OF_A_KIND': 4,
            'STRAIGHT': 5,
            'FLUSH': 6,
            'FULL_HOUSE': 7,
            'FOUR_OF_A_KIND': 8,
            'STRAIGHT_FLUSH': 9,
            'ROYAL_FLUSH': 10
        }

        # Determine hand strength
        strength = None
        for info in hand_info:
            if info['uuid'] == self.uuid:
                strength = info['hand']['hand']['strength']
                break

        # Reward based on the strength of the hand
        reward_for_strength = strength_reward.get(strength, 1)

        # Base reward for winning or losing
        base_reward = 0
        for winner in winners:
            if winner['uuid'] == self.uuid:
                base_reward = reward_for_strength
                break
        else:
            base_reward = -1
            
        # Scale reward by round count
        reward = base_reward

        self.learn(reward)
        self.update_exploration_rate()

    def save_model(self, filepath='tmp2/b11705051/final_project/q_learning_model.pkl'):
        joblib.dump(self.q_table, filepath)
    
    def load_model(self, filepath='tmp2/b11705051/final_project/q_learning_model.pkl'):
        if os.path.exists(filepath):
            self.q_table = joblib.load(filepath)
            
def setup_ai():
    return AiPlayer()
