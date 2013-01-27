import numpy as np
from itertools import product as cartesian_product
#from utils import positive
from strongchicken.utils  import MonteCarloEstimation
from strongchicken.utils  import positive
from strongchicken.uncertainties import ForwardSimulator
from strongchicken.assets import payoff
from strongchicken.utils import *
NB_SIMULATION_BLOCK = 10000


class Asset:
    """ Object representing an asset
    """
    def cash_flows(self, market_assumptions, buckets_timeline, nb_simulations=10000):
        """ Returns a big matrix with the cashflows yield in each bucket of the timeline
        
        rows is simulation
        col is the number of the bucket. 
        """
        raise NotImplementedError("You need to implement a cash flow function on your asset.")

    def valuation(self, market_assumptions, nb_simulations=10000, time_horizon=None):
        """ Returns the Mark to market of the asset.
        """
        time_horizon = time_horizon or self.exercise_times[-1] + 1.
        cash_flows = self.cash_flows(market_assumptions, np.array([0., time_horizon]), nb_simulations)
        return  MonteCarloEstimation(cash_flows.reshape(nb_simulations))


class EuropeanOption(Asset):
    def __init__(self, T, strike, market):
        """ European option
        
        T is the maturity of the option
        """
        self.market = market
        self.T = T
        self.strike = strike

    def valuation(self, market_assumptions, nb_simulations=1000000):
        simulator = ForwardSimulator(
                        market_assumptions.uncertainty_system,
                        [0., self.T],
                        nb_simulations,
                        antithetic=True)
        simulator.go_end()
        discount_factor = market_assumptions.discount_factor(self.T)
        return MonteCarloEstimation(self.get_payoff(simulator) * discount_factor)

    def get_spot(self, simulator):
        return simulator.state[self.market]

class EuropeanPut(EuropeanOption):
    def get_payoff(self, simulator):
        return positive(self.strike - self.get_spot(simulator))

class EuropeanCall(EuropeanOption):
    def get_payoff(self, simulator):
        return positive(self.get_spot(simulator) - self.strike)


class Command:
   """ Command class
   
   Optional assets allow asset managers to
   choose between a set of command at defined 
   exercise dates.
   
   These command basically consists of a triplet:
   (asset, stock, payoff)
   """
   def __init__(self, dest_state, payoff):
       self.dest_state = dest_state
       self.payoff = payoff

   def __repr__(self,):
       return "command going to " + str(self.dest_state)

   @property
   def dest_state(self,):
       return self.dest_state




class OptionalAssetState():


    def __init__(self, parent):
        self.parent = parent

    def extract_markov_state(self, simulator):
        return self.parent.extract_markov_state(simulator)

    def get_commands(self, t):
        return NotImplementedError

    def get_final_value(self, tid):
        return lambda simulator: np.zeros((1, simulator.nb_simulations))

    def get_conditional_expectancy(self, tid, store):
        return store.get(tid, self,)




class OptionalAsset:

    @property
    def exercise_times(self,):
        return self.exercise_times

    @property
    def initial_state(self,):
        state_accessible_at_t0 = self.get_accessible_states(0)
        assert len(state_accessible_at_t0) == 1 # there should be only one state
        return state_accessible_at_t0[0]

    def get_accessible_states(self, t_id):
        raise


class GenericState(OptionalAssetState):

    def __init__(self, parent, commands=[]):
        OptionalAssetState.__init__(self, parent)
        self.commands = commands

    def get_commands(self, t):
        return self.commands


class Sink(GenericState):

    def __init__(self, parent):
        GenericState.__init__(self, parent, [ Command(self, payoff.null) ])

    def get_conditional_expectancy(self, tid, store):
        return payoff.null


class GenericSwingOption(OptionalAsset):

    def __init__(self, nb_exercise_min, nb_exercise_max, exercise_times):
        self.asset_states = [ Sink(self) ]
        for i in range(nb_exercise_max):
            new_state = GenericState(self,[])
            new_state.commands += [ Command(self.asset_states[-1], self.payoff),
                                    Command(new_state, payoff.null) ]
            self.asset_states.append(new_state)
        self.exercise_times = exercise_times

    def get_accessible_states(self, tid):
        # todo get rid of inaccessible states because of the min limit
        return self.asset_states[-(tid + 1):]

    def payoff(self, simulator):
        raise NotImplementedError("You need to implement the payoff")


"""
class SimpleGasStorage(StockAsset):

  def __init__(self,
               exercise_freq,
               time_horizon,
               total_volume,
               exercise_volume,
               injection_cost,
               withdrawal_cost,
               market):
      self.total_volume = total_volume
      self.exercise_times = np.arange(0., time_horizon + exercise_freq, exercise_freq)
      self.exercise_volume = exercise_volume
      self.injection_cost = injection_cost
      self.withdrawal_cost = withdrawal_cost
      self.market = market
      self.nb_volume_levels = self.total_volume / self.exercise_volume
      self.volume_level = self.total_volume / self.nb_volume_levels
      # initial state
      self.initial_stock = 0

  def get_spot(self, simulator):
      return simulator.get(self.market)

  def get_computation_grid(self, t):
      return {self : range(0, self.nb_volume_levels + 1) }

  def get_commands(self, t, stock):
      commands = [ Command(self, stock, zero_payoff) ]
      if stock > 0 :
          commands.append(Command(self, stock - 1, self.get_withdrawal_payoff))
      elif stock < self.nb_volume_levels:
          commands.append(Command(self, stock + 1, self.get_injection_payoff))
      return commands

  def get_injection_payoff(self, simulator):
      return self.volume_level * (-self.get_spot(simulator) - self.injection_cost)

  def get_withdrawal_payoff(self, simulator):
      return self.volume_level * (self.get_spot(simulator) - self.withdrawal_cost)

  def extract_markov_state(self, simulator):
      spots = self.get_spot(simulator)
      (nb_simulation) = spots.shape
      return self.get_spot(simulator).reshape((1, nb_simulation))
"""




class AmericanPut(GenericSwingOption):

    def __init__(self, start, end, strike, market, bermudean_interval=7.*UNIT.DAY):
        exercise_dates = set(np.arange(start, end, bermudean_interval))
        exercise_dates.add(end)
        exercise_dates = sorted(exercise_dates)
        GenericSwingOption.__init__(self, 0, 1, exercise_dates)
        self.market = market
        self.strike = strike

    def payoff(self, uncertainty_states):
        return positive(self.strike - uncertainty_states[self.market])

    def extract_markov_state(self, uncertainty_states):
        return uncertainty_states[self.market]




