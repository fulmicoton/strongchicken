
Tutorial 1:  The basics.
===================================================================




Introduction
--------------------------------------

Apart from some core functions, strongchicken is divided into two big packages.

  - *uncertainties*, in which your will find everything you need to simulate
    a bunch of uncertainties (market prices, load curves, temperatures...).
    This module can be used completely independantly.
    It includes a small (but growing) catalog of uncertainty model you can use out-of-the-box, but you will eventually want to extend it with your own models.
  
  - and *assets*, which will allow you to create a portfolio, put some assets in it, optimize
    them, simulate them, and play with them. This module is pretty dependant on the uncertainties
    module since optimization and simulation requires to instance a simulator.


In this tutorial, we will learn how to use of models/assets that are available in the catalog of strongchicken.




Uncertainties
--------------------------------------


First let's try and create a good old black-scholes model and plot its different paths.

To do so, we will need to :
	#. define the market we want to plot
	#. define the timeline on which we want to operate the simulation
	#. create a simulator
	#. iterate and plot the result

.. literalinclude:: tutorial1_1_plot.py
    :language: python
    :linenos:

#. The timeline
	
	.. :	
	
		timeline = np.arange(0., UNIT.YEAR, UNIT.DAY)
	
	In strongchicken non-regular timeline are just defined by either a list or a numpy array. *The first element of a simulation timeline MUST be the initial time t0=0. (And hopefully we will find the same value). 

	You may want to express these quantities in
	any unit you want. For a better readibility and
	in order to avoid bugs, it is strongly advised to explicitely express the unit by multiplying your value by the value in the UNIT dictionary,
	as shown in the example.
	
	At the moment, unit consistency is not really checked
	and this operation will only convert your value into days, but this may change in the near future. 


	Here we defined the timeline (day 0, day 1, ..., day 365).

#. The market

	.. :
		from strongchicken.uncertainties import BlackScholes
		...
		market = BlackScholes(36., .06*INV.YEAR, .2*INV.SQRT.YEAR)

	
	All of the models available in strongchicken
	can be imported from strongchicken.uncertainties.

	Here we instanciate a BlackScholes object with 
	an initial value S_t0=55.

	Once again we used INV.YEAR (year^-1) and INV.SQRT.YEAR (year^-1/2) as units for respectively the drift and the volatility of the market.
	
#.  The simulator

	.. :
		from strongchicken.uncertainties import ForwardSimulator as Simulator
		from strongchicken.uncertainties import UncertaintySystem

		uncertainty_system = UncertaintySystem([market])
		# and the simulator, we're all set to begin the simulation!
		nb_paths = 1000
		simulator = Simulator(uncertainty_system, timeline, nb_paths)
	
	We then need to build a simulator, which basically acts as an iterator (= a remote control ) to help browse through the simulation timeline.

	Most of the time, you will use the ForwardSimulator.
	It makes it possible to browse forward through all the simulations, once timestep by one timestep.

	Computations are done as you call the .go_next() method, and former timestep simulation results are forgotten to release memory. As a downside, it is not possible to go backward.
	
	Once a timestep is reached, one may get the state of an uncertaines handled by the simulator
	by using the .state dictionary-like property.

	It will return a matrix where the columns is the simulation number, and the row is the dimension of the state of the uncertainty : which is basically the dimension of the markov state of your model.

	e.g.: for a 2-factor model, that would be 2.

	Actually, strongchicken only handles markovian models. In other words, all the model implemented should follow the following rule.

	The state of the uncertainty system at t+1, may only depends on the state of the uncertainty system at t.
	
	In order to plot 10 paths we may write for instance:

	paths = np.zeros((len(timeline), 10))
	for (t_id,t) in enumerate(timeline):
		paths[t_id,:] = simulator.state[market][:10]
		simulator.go_next()
	plt.plot(paths)

	and obtain the following result :

	..:
		add the fig here.


Well done!




Assets
--------------------------------------

Actually the model we just defined is the very same as the one used in the original Longstaff-Schwartz paper.

We will now use their algorithm to price the exact american put they studied (and hopefully get the same result).

The definition of the american option is pretty straightforward.

	american_put = AmericanPut(0., 1. * UNIT.YEAR, 40., market)

An important concept of strongchicken is the distinction
between assets and optional assets. Basically :

- an asset is something that yield cashflows depending only on the path followed by the uncertainties. One may then define the value of an asset as the expectancy of these discounted cashflows.

- an optional asset is something that will yield cashflows for its holder, depending on both *its management* of the asset, and on the path followed by the uncertainties.

Basically we have:

  Optional asset + Asset Manager = Asset

Practically, coupling an asset manager to the optional asset, most of the time consists in performing a relatively time-consuming optimization method (e.g. Longstaff-Staff, and creating a managed asset from it). 

One may define the value of an optional asset as the maximum value of the asset obtained when coupling it with a competent asset manager.

For different reasons, we purposefully avoid this shorcut in strongchicken. The main reason for this is 
that strongchicken has been tailored for risk management.

Consider it as a reminder that it is not good practise to hedge an asset without using the same optimization method / the same hypothesis as the asset manager.

We need to define an assumption set object, which
will include the hypothesis made on the market.
At the moment, it only consists on the uncertainty system and the risk-free rate.

uncertainty_system = UncertaintySystem([market])
assumption_set = AssumptionSet(uncertainty_system, interest_rate=.06 * INV.YEAR,)

We may now optimize our asset using the Longstaff Schwartz method.

.. :
	optimized_asset = longstaff_schwartz.optimize(
					american_put,
	                assumption_set,
	                nb_simulations=10000,
	                regression=force_positive_regression(polynomial_regression))
	print optimized_asset.valuation()


Here we regress the continuation value on the set of polynoms of the shape "1 + a.S + b.S^2". 

There is however one thing that differs from Longstaff-Schwartz paper.

At a given timestep t, if the spot price is higher than the strike, there is no reason one would want to exercise. Therefore for more accuracy they only use the paths for which exercise makes sense when regressing.
 
The implementation of the algorithm in strongchicken is more generic and applies to basically any asset. It does not detect rules such as "For obvious reasons, the continuation value must be positive".

Actually the polynomial regression is not exactly suited to fit the continuation value and we are very likely to encounter negative values on extrem values path. For these simulations, the algorithm will be sub-optimal.

We indeed find a value in simulation around 4.41 instead of the expected value of 4.472.

A correct way to avoid this problem is to chose a better
regression method such as local linear basis. Here we only considered the following "hack" :
resulting regressed functions f, are replace their forced positive version max(f,0).

We now want to get the price of this optimized_asset. The value of the optimized asset can be accurately computed by Monte-Carlo on a different set of paths.
This is done via :


.. ::
	
	print optimized_asset.valuation(assumption_set, nb_simulations=100000)

Optimization requires backward simulation. Strongchicken does not implement brownian bridge yet.
This means that all timestep are simulated and stored in memory.

Simulation on the other hand only uses a forward simulator. It is therefore possible to use a bigger
number of simulations for this step.

The optimization actually generates a price for the asset. You can it via :

.. ::
	print optimized_asset.optimization_value

Considering the two values is actually required to answer the difficult question of "how many simulation should I use?". Please refer to

..:
	TODO add page how many simulation to use
to understand how to choose the number of paths.

The complete source code is below :

.. literalinclude:: tutorial1_2_price.py
    :language: python
    :linenos:

Note that values obtained via Monte-Carlo are not float, but special objects encapsulating information about the accuracy of the result.]

printing these values therefore displays
the 80%, 90%, and the 95% confidence intervals:

.. :
	
	80.0% confidence : [4.4366,4.479709]
	90.0% confidence : [4.4254,4.490964]
	95.0% confidence : [4.4161,4.500257]

