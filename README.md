# Script for Examining Discrepancies in Volatility

## Table of Contents
+ [General Description](#gendes)
+ [multiAssetArbPlot()](#maap)									
    + [Description](#maapde)
    + [Parameters](#maappa)
    + [Usage](#maapus)
    + [Output](#maapou)
 + [twoAssetVolArbDifferences()](#tad)
    + [Description](#taddes)
    + [Parameters](#tadpar)
    + [Usage](#tadusa)
    + [Output](#tadout)
 + [monoPointArb()](#mpa)
    + [Description](#mpades)
    + [Parameters](#mpapar)
    + [Usage](#mpausa)
    + [Output](#mpaout)
+ [polyPointArb()](#ppa)
    + [Description](#ppades)
    + [Parameters](#ppapar)
    + [Usage](#ppausa)
    + [Output](#ppaout)
+ [tailsComparison()](#tc)
    + [Description](#tcdesc)
    + [Parameters](#tcpara)
    + [Usage](#tcusag)
    + [Output](#tcoutp)

+ [Suggestions for Continuation](#sugcon)

## General Description <a name = "gendes"></a>

Script for examining discrepancies in volatility for ETPs with the same underlying asset(s). In theory, the script could be used for performing volatility arbitrage, though I would guess that transaction and data costs, in addition to slippage, would render this strategy infeasible. Provided two assets, this script can compute the degree of arbitrage represented as a number, with 1.00 representing parity. The script also has some functionality for observing the distribution of tails for the arbitrage degrees generated within. There are plotting features too, which can be used to either observe a number of assets to aid in deciding which pair of assets to choose for further examination, or for observing the differences in standard deviation for the chosen pair of the two assets. 

This script could perhaps benefit slightly from being structured as a class, since the parameters would not have to be specified as often for the functions, but I think it functions just fine as a script. It should be noted that a variable named tickerSymbols is defined at the bottom of the script, and that multiAssetArbPlot() uses this variable, which is not defined locally inside the function.

The script obtains data from the claydates package, which calls upon the Twelve Data API. For more information, navigate to the claydates package's [Github](https://github.com/ClaytonDuffin/claydates), or [PyPi](https://pypi.org/project/claydates/). For more information on the batcher() function, [visit where I wrote about it in a separate project](https://github.com/ClaytonDuffin/Complex-Plane-Analysis#batcher).

## multiAssetArbPlot() <a name = "maap"></a>

### Description <a name = "maapde"></a>

Can be used for scanning (visually) multiple tickers for volatility arbitrage.

### Parameters <a name = "maappa"></a>
* datasets : list[pd.DataFrame]
	- Takes in a list of time series dataframes for a number of assets to perform computations on. These would all be tickers based off of the same underlying ideally.
* volArbType : Optional[str]
	- Determines which type of volatility arbitrage to perform.
	- Takes one of three inputs:
		- 'Type1' ... Normalizes the time series (using min-max scaling) after the desired computations have been applied to the series. Uses a raw price series.
		- 'Type2' ... Normalizes the time series (using min-max scaling) after the desired computations have been applied to the series. Uses a percentage change series.
		- 'Type3' ... Assumes the user to be trading a leveraged ETP and it's non-leveraged counterpart (say SPXL and SPY). Simply divides leveraged ETP at each step by leverage factor. Nothing is done with this volArbType outside of this method. 
* methodology : Optional[Callable[Union[pd.DataFrame.std, pd.DataFrame.var], int]]
	- Defines whether to use standard deviation or variance for the computation. Conveniently, also works for stuff like pd.DataFrame.kurtosis, or pd.DataFrame.median. 
* windowForMethodology : Optional[int]
	- Passes the size of the moving window to the rolling function. Default is 10.

### Usage <a name = "maapus"></a>
```
from claydates import MultiTickerProcessor
tickerObjects = MultiTickerProcessor(['QQQ','TQQQ'], '1min', 100) 
fullDatasetForVolArb = tickerObjects.missingUnitsExcluded(matchDates = 'True')
tickerSymbols = tickerObjects._tickerSymbols

multiAssetArbPlot(datasets = fullDatasetForVolArb,
                  volArbType = 'Type1',
                  methodology = pd.DataFrame.std,
                  windowForMethodology = 10)

```
### Output <a name = "maapou"></a>

![multiAssetArbPlotOutput](https://user-images.githubusercontent.com/116965482/210121701-cee13cc4-1b60-4c56-b139-ae915ad5ac49.png)

## twoAssetVolArbDifferences() <a name = "tad"></a>

### Description  <a name = "taddes"></a>
Used for taking the differences in deviation for two series of the respective volArbType. Supports two volArbTypes. Is also used in monoPointArb(), tailComparison(), and polyPointArb().

### Parameters  <a name = "tadpar"></a>
* datasets : list[pd.DataFrame]
	- Takes in a list of time series dataframes for a number of assets to perform computations on. These would all be tickers based off of the same underlying ideally.
* volArbType : Optional[str]
	- Determines which type of volatility arbitrage to perform.
	- Takes one of two inputs:
		- 'Type1' ... Normalizes the time series (using min-max scaling) after the desired computations have been applied to the series. Uses a raw price series.
		- 'Type2' ... Normalizes the time series (using min-max scaling) after the desired computations have been applied to the series. Uses a percentage change series.
* methodology : Optional[Callable[Union[pd.DataFrame.std, pd.DataFrame.var], int]]
	- Defines whether to use standard deviation or variance for the computation. Conveniently, also works for stuff like pd.DataFrame.kurtosis, or pd.DataFrame.median. 
* windowForMethodology : Optional[int]
	- Passes the size of the moving window to the rolling function. Default is 10.
* show : Optional[bool]
	- Determines whether or not to use the function to compute and show the differences using a plot. Default is False.

### Usage <a name = "tadusa"></a>
```
from claydates import MultiTickerProcessor
tickerObjects = MultiTickerProcessor(['SPY','SPXL'], '1min', 100) 
fullDatasetForVolArb = tickerObjects.missingUnitsExcluded(matchDates = 'True')

twoAssetVolArbDifferences(datasets = fullDatasetForVolArb,
                          volArbType = 'Type1',
                          methodology = pd.DataFrame.std,
                          windowForMethodology = 10,
                          show = True)
```
### Output <a name = "tadout"></a>
Depending on the value of the 'show' parameter, the function either returns a pandas DataFrame, or a plot.

![twoAssetVolArbDifferencesOutput](https://user-images.githubusercontent.com/116965482/210121686-2f1e4d1e-a9b5-404e-8791-0c14af9e8920.png)

## monoPointArb() <a name = "mpa"></a>

### Description <a name = "mpades"></a>
Used for calculating the degree of arbitrage at the current time-step (the most recent unit in each dataframe). Uses a blend of differences computed from the processes for both the 'Type1' and 'Type2' volArbType argument. Returns a number to quantify the degree of arbitrage. Parity exists when this function's output is equal to  1.00.

### Parameters  <a name = "mpapar"></a>
* datasets : list[pd.DataFrame]
	- Takes in a list of time series dataframes for a number of assets to perform computations on. These would all be tickers based off of the same underlying ideally.
* methodology : Optional[Callable[Union[pd.DataFrame.std, pd.DataFrame.var], int]]
	- Defines whether to use standard deviation or variance for the computation. Conveniently, also works for stuff like pd.DataFrame.kurtosis, or pd.DataFrame.median. 
* windowForMethodology : Optional[int]
	- Passes the size of the moving window to the rolling function. Default is 10.

### Usage <a name = "mpausa"></a>
```
from claydates import MultiTickerProcessor
tickerObjects = MultiTickerProcessor(['SPY','SPXL'], '1min', 100) 
fullDatasetForVolArb = tickerObjects.missingUnitsExcluded(matchDates = 'True')

monoArbDegree = monoPointArb(datasets = fullDatasetForVolArb,
                            methodology = pd.DataFrame.std,
                            windowForMethodology = 10)

print(monoArbDegree)
```
### Output <a name = "mpaout"></a>
```
Returns a floating point number to measure the degree of arbitrage. Parity exists at 1.00.
```

## polyPointArb() <a name = "ppa"></a>

### Description <a name = "ppades"></a>
Used for calculating the degree of arbitrage at the current time-step (the most recent unit in each dataframe), based on numerous combinations of parameters. Uses a blend of differences computed from the processes for the 'Type1' and 'Type2' volArbType argument, but uses instead a series of numbers for windowForMethodology. polyPointArb() also introduces the batcher() function, which spaces the data units in different ways than just the space which was fed into input. The spaces are the same values for batcher() as they are for windowForMethodology, and in general, polyPointArb() can be thought of as a nested for-loop. I personally like how the tqdm progress bars are right now, but you may not. Turn them off if this is the case by removing them from the start of the for-loops. This function returns a series of numbers to measure the degree of arbitrage for each combination the function generates. It is worth noting that I've built this function with blending this series of numbers eventually into 1 final value, like monoPointArb(). I created polyPointArb() in hopes of finding a more accurate measurement for degree of arbitrage.

### Parameters <a name = "ppapar"></a>
* datasets : list[pd.DataFrame]
	- Takes in a list of time series dataframes for a number of assets to perform computations on. These would all be tickers based off of the same underlying ideally.
* methodology : Optional[Callable[Union[pd.DataFrame.std, pd.DataFrame.var], int]]
	- Defines whether to use standard deviation or variance for the computation. Conveniently, also works for stuff like pd.DataFrame.kurtosis, or pd.DataFrame.median. 

### Usage <a name = "ppausa"></a>
```
from claydates import MultiTickerProcessor
tickerObjects = MultiTickerProcessor(['SPY','SPXL'], '1min', 100) 
fullDatasetForVolArb = tickerObjects.missingUnitsExcluded(matchDates = 'True')

polyArbLevels = polyPointArb(datasets = fullDatasetForVolArb,
                             methodology = pd.DataFrame.std)

print(float(polyArbLevels.median()))
```

### Output <a name = "ppaout"></a>
```
Returns a pandas DataFrame of numbers to measure the degree of arbitrage for each combination the function generates. Parity exists at 1.00.
```

## tailsComparison() <a name = "tc"></a>

### Description <a name = "tcdesc"></a>

Multiplies the length of the polyPointArb() output by 12%, and then takes the nth largest/smallest numbers on both sides of the distribution ((len(polyPointArb()) * 0.12) numbers on each side of the distriution), and adds them up. Then, a comparison between the two is returned In terms of "smaller tails are _output_ times smaller than larger tails," if value is negative, or "smaller tails are _output_ times larger than larger tails," if positive. This function would probably be better off bundled into polyPointArb() for runtime purposes, but to improve readability I've written it as a separate function.

### Parameters <a name = "tcpara"></a>
* datasets : list[pd.DataFrame]
	- Takes in a list of time series dataframes for a number of assets to perform computations on. These would all be tickers based off of the same underlying ideally.
* methodology : Optional[Callable[Union[pd.DataFrame.std, pd.DataFrame.var], int]]
	- Defines whether to use standard deviation or variance for the computation. Conveniently, also works for stuff like pd.DataFrame.kurtosis, or pd.DataFrame.median. 

### Usage <a name = "tcusag"></a>
```
from claydates import MultiTickerProcessor
tickerObjects = MultiTickerProcessor(['SPY','SPXL'], '1min', 100) 
fullDatasetForVolArb = tickerObjects.missingUnitsExcluded(matchDates = 'True')

tailsRatio = tailsComparison(datasets = fullDatasetForVolArb,
                            methodology = pd.DataFrame.std)

print(tailsRatio)
```
### Output  <a name = "tcoutp"></a>
```
Returns a ratio, either positive or negative. If negative, the tails on the positive end outweigh the tails on the negative end, and vice versa.  
```

## Suggestions for Continuation <a name = "sugcon"></a>

1. I suggest actually digging into the options chains for the products you're looking at, to see if it is doable. 
