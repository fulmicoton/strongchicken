from collections import defaultdict
from asset import Asset
from regression import linear_regression, polynomial_regression
from strongchicken.uncertainties import BidirectionalSimulator, ForwardSimulator
from strongchicken.utils import compose, MagicDic, MonteCarloEstimation
import numpy as np


class ConditionalExpectancyStore:
    """
    In this we store for time ti
    E(Sum CF_t, t>ti / F_ti)

    note that CF at ti is not stored.
    """
    def __init__(self):
        self._data = MagicDic()

    def set(self, time_id, asset_state, conditional_expectancy):
        self._data[time_id][asset_state] = conditional_expectancy

    def get(self, time_id, asset_state):
        return self._data[time_id][asset_state]



class ManagedAsset(Asset):
    def __init__(self, asset, conditional_expectancy_store):
        self._ce_store = conditional_expectancy_store
        self._asset = asset




def compute_expected_value_given_command(state,
                                         command,
                                         conditional_expectancy_store,
                                         discount_factor):
    dest_state = command.dest_state
    conditional_expectancy = dest_state.get_conditional_expectancy(
                                        state.tid,
                                        conditional_expectancy_store)

    # TODO make it simulator.states
    conditional_expectancies = conditional_expectancy(state)
    payoffs = discount_factor(state.t) * command.payoff(state)
    assert (conditional_expectancies + payoffs).shape[-1] == \
            state.nb_simulations
    return conditional_expectancies + payoffs


def compute_expected_value_foreach_command(asset_state,
                                           state,
                                           conditional_expectancy_store,
                                           discount_factor):
    S = state.nb_simulations
    commands = asset_state.get_commands(state.tid)
    bellman_values_if_command = np.zeros((len(commands), S))
    for (i, command) in enumerate(commands):
        bellman_values_if_command[i, :] = compute_expected_value_given_command(
                                        state,
                                        command,
                                        conditional_expectancy_store,
                                        discount_factor)[0, :]
    return bellman_values_if_command


def compute_optimal_command(asset_state,
                            simulator,
                            conditional_expectancy_store,
                            discount_factor):
    expected_values_foreach_command = compute_expected_value_foreach_command(
                                            asset_state,
                                            simulator,
                                            conditional_expectancy_store,
                                            discount_factor)
    return np.argmax(expected_values_foreach_command, axis=0)




class OptimizedAsset(Asset):

   def __init__(self, optional_asset, conditional_expectation_store, optimization_value):
       self.optional_asset = optional_asset
       self.conditional_expectation_store = conditional_expectation_store
       self.optimization_value = optimization_value

   @property
   def exercise_times(self,):
       return self.optional_asset.exercise_times

   def show(self, market_assumptions):
       exercise_times = list(self.optional_asset.exercise_times)
       simulation_timeline = sorted(set([0.] + exercise_times))
       simulator = market_assumptions.get_simulator(simulation_timeline)
       for t in exercise_times[1:]:
           simulator.go_next()
           t_id = simulator.t_id
           spot_values = self.optional_asset.extract_markov_state(simulator)
           asset_values = self.conditional_expection_store.get(t_id, self.optional_asset, 1)(simulator)

   def simulate(self, market_assumptions, nb_simulations, antithetic=False):
       """
       Returns a generator yielding for each simulation timestep
       a map of the type :
           (asset, state) -> command -> simulation_ids
       """
       exercise_times = list(self.optional_asset.exercise_times)
       simulation_timeline = sorted(set([0.] + exercise_times))
       asset_states = { self.optional_asset.initial_state : np.arange(0, nb_simulations, dtype=np.int32) }
       states_and_command = {}
       simulator = ForwardSimulator(market_assumptions.uncertainty_system,
                                    simulation_timeline,
                                    nb_simulations=nb_simulations,
                                    antithetic=antithetic)
       # simulator.go_to(exercise_times[0]) # todo handle stuff not beginning at t0
       for t in exercise_times:
           tid = simulator.tid
           new_asset_states = {}
           for (asset_state, sim_ids) in asset_states.items():
               if sim_ids.shape != (0,):
                   asset_stock_optimal_command_ids = {}
                   cur_masked_state = simulator.state.mask(sim_ids)
                   optimal_command_ids = compute_optimal_command(asset_state,
                                cur_masked_state,
                                self.conditional_expectation_store,
                                market_assumptions.discount_factor)

                   commands = asset_state.get_commands(t)
                   for (command_id, command) in enumerate(commands):
                       # simulation indexes on which the command is optimal 
                       sim_indexes = np.where(optimal_command_ids == command_id)[0]
                       optimal_command_sim_ids = sim_ids[sim_indexes]
                       asset_stock_optimal_command_ids[command] = optimal_command_sim_ids
                       cur_masked_state_for_command = simulator.state.mask(optimal_command_sim_ids)
                       former_simulation_ids = new_asset_states.get(command.dest_state, np.array([], dtype=np.int32))
                       new_asset_states[ command.dest_state ] = np.union1d(former_simulation_ids, optimal_command_sim_ids)
                       asset_states = new_asset_states
                   states_and_command[asset_state] = asset_stock_optimal_command_ids
           yield (simulator.state, states_and_command)
           simulator.go_next()

   def cash_flows(self, market_assumptions, buckets_timeline, nb_simulations=10000, antithetic=False):
       nb_buckets = len(buckets_timeline) - 1
       assert nb_buckets >= 1
       cash_flows = np.zeros((nb_buckets, nb_simulations))
       discount_factor = market_assumptions.discount_factor
       for (state, states_and_command) in self.simulate(market_assumptions, nb_simulations, antithetic):
           t = state.t
           if buckets_timeline[0] <= t:
               if buckets_timeline[-1] < t:
                   break
               discount_factor_t = discount_factor(t)
               bucket_id = np.searchsorted(buckets_timeline, t + .001) - 1
               for (asset, command_dic) in states_and_command.items():
                   for (command, simulation_ids) in command_dic.items():
                       #simulator.simulation_range = simulation_ids
                       masked_state = state.mask(simulation_ids)
                       cash_flows[bucket_id, simulation_ids] += discount_factor_t * command.payoff(masked_state)[0]
       return cash_flows



def optimize(optional_asset,
             market_assumptions,
             nb_simulations=1000,
             regression=polynomial_regression):
    
    discount_factor = market_assumptions.discount_factor
    exercise_times = list(optional_asset.exercise_times)
    simulation_timeline = sorted(set([0.] + exercise_times))

    # create a simulator, we will go backward
    # TODO only simulate required uncertainties.
    simulator = BidirectionalSimulator(market_assumptions.uncertainty_system,
                                       simulation_timeline,
                                       nb_simulations,
                                       antithetic=True)
    simulator.go_end()

    bellman_values_shape = (1, simulator.nb_simulations)
    next_bellman_values = defaultdict(lambda: np.zeros(bellman_values_shape))

    # set terminal values
    # conditional_expectancy_store contains for a given t,
    # the expected return of the asset at t+, knowing the state of the asset
    # at t+
    conditional_expectancy_store = ConditionalExpectancyStore()

    nb_exercises = len(exercise_times) - 1
    t_final = simulation_timeline[-1]
    # considering the state accessible at the last exercise date...
    for asset_state in optional_asset.get_accessible_states(nb_exercises - 1):
        # we check all the accessible state at the next step :
        for command in asset_state.get_commands(t_final):
            final_state = command.dest_state
            conditional_expectancy_store.set(simulator.tid,
                                final_state,
                                final_state.get_final_value(simulator.tid,))
    bellman_values = np.zeros((1, simulator.nb_simulations))

    # backward optimization
    for t in exercise_times[::-1]:
        discount_factor_t = discount_factor(t)
        cur_bellman_values = defaultdict(lambda:defaultdict(lambda :0.))
        t_id = simulator.tid
        # TODO differentiate simulation timeline and asset timeline.
        for asset_state in optional_asset.get_accessible_states(t_id):
            # returns the bellman values for all simulations
            bellman_values_if_commands = compute_expected_value_foreach_command(
                                             asset_state,
                                             simulator.state    ,
                                             conditional_expectancy_store,
                                             market_assumptions.discount_factor)
            # optimal command
            optimal_command_id = compute_optimal_command(asset_state,
                                             simulator.state,
                                             conditional_expectancy_store,
                                             discount_factor)
            bellman_values = 0.
            commands = asset_state.get_commands(t)
            bellman_values_if_command = np.zeros((len(commands), simulator.nb_simulations))
            for (command_id, command) in enumerate(commands):
                bellman_values_if_command[command_id:command_id+1, :] = command.payoff(simulator.state) * discount_factor_t + next_bellman_values[command.dest_state]
            bellman_values = bellman_values_if_command[optimal_command_id, np.arange(simulator.nb_simulations)].reshape(1, simulator.nb_simulations)
            cur_bellman_values[asset_state] = bellman_values
            regression_information = asset_state.extract_markov_state(simulator.previous)
            conditional_expectancy = compose(regression(regression_information, bellman_values), optional_asset.extract_markov_state)
            conditional_expectancy_store.set(t_id - 1, asset_state, conditional_expectancy)

        next_bellman_values = cur_bellman_values
        simulator.go_back()

    mtm = MonteCarloEstimation(bellman_values,antithetic=antithetic)

    return OptimizedAsset(optional_asset, conditional_expectancy_store, mtm)
