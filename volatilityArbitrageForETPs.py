import pandas as pd
import matplotlib.pyplot as plt; plt.rcdefaults()
from tqdm import tqdm
from itertools import chain
from typing import Union, Optional, Callable
import warnings
warnings.simplefilter(action='ignore', category=pd.errors.PerformanceWarning)


def minMaxScaler(frame: pd.DataFrame,
                 lower: Optional[float] = 0,
                 upper: Optional[float] = 1) -> pd.DataFrame:

    '''
    Scales a dataframe to a range specified by the parameters.
    
    Parameters
    ----------
    frame : pd.DataFrame
        The DataFrame to be scaled.
    lower : float
        The global minimum of the data is to be rescaled to this number.
    upper : float
        The global maxmimum of the data is to be rescaled to this number.
    '''
    
    freshlyScaled = []
    for i in frame:
        newLower, newUpper, oldLower, oldUpper =  lower, upper, frame[i].min(), frame[i].max()
        freshlyScaled.append((frame[i] - oldLower) / (oldUpper - oldLower) * (newUpper - newLower) + newLower)

    return (pd.DataFrame(freshlyScaled).T)


def batcher(sineWaveData: Union[pd.Series, pd.DataFrame],
            subframeLength: int, 
            gapToNextFrame: int) -> list:
    
    '''
    Function used for batching up a pandas DataFrame or Series object. The output data will be used for feature
    extrapolation in polyPointArb()
    
    Parameters
    ----------   
    sineWaveData : pd.Series
        The input data for batching.
    subframeLength: int
        Determines how long each subframe should be.
    gapToNextFrame: int
        Determines the spacing between the start of one subframe and the next. 
    '''

    if isinstance(sineWaveData, pd.Series):
        originalData = list(zip(sineWaveData))
    else:
        originalData = list(zip(*[sineWaveData[col] for col in sineWaveData.columns[1:]]))

    fullSeries = []
    for t, j in enumerate(originalData):
        subSeries = [] 
        for i in range(0, subframeLength, gapToNextFrame):
            try:
                subSeries.append(originalData[t-i])
            except IndexError:
                continue
            
        fullSeries.append(list(chain(*[list(row) for row in subSeries[::-1]])))
        
    return fullSeries


def multiAssetArbPlot(datasets: list[pd.DataFrame],
                      volArbType: Optional[str] = 'Type1',
                      methodology: Optional[Callable[Union[pd.DataFrame.std, pd.DataFrame.var], int]] = pd.DataFrame.std, 
                      windowForMethodology: Optional[int] = 10) -> None:

    '''
    Can be used for scanning (visually) multiple tickers for volatility arbitrage.
        
    Parameters
    ----------
    datasets : list[pd.DataFrame]
        Takes in a list of time series dataframes for a number of assets to perform computations on. These would all be tickers based off of the same underlying ideally.
    volArbType : Optional[str]
        Determines which type of volatility arbitrage to perform.
        Takes one of three inputs:
           'Type1' ... Normalizes the time series (using min-max scaling) after the desired computations have been applied to the series. Uses a raw price series.
           'Type2' ... Normalizes the time series (using min-max scaling) after the desired computations have been applied to the series. Uses a percentage change series.
           'Type3' ... Assumes the user to be trading a leveraged ETP and it's non-leveraged counterpart (say SPXL and SPY). Simply divides leveraged ETP at each step by leverage factor.
                       Nothing is done with this volArbType outside of this method. 
    methodology : Optional[Callable[Union[pd.DataFrame.std, pd.DataFrame.var], int]]
        Defines whether to use standard deviation or variance for the computation. Conveniently, also works for stuff like pd.DataFrame.kurtosis, or pd.DataFrame.median. 
    windowForMethodology : Optional[int]
        Passes the size of the moving window to the rolling function. Default is 10.
    '''
    
    for index, dataset in enumerate(datasets):
        
        if (volArbType == 'Type1'):
            plt.plot(minMaxScaler(pd.DataFrame(dataset.Close.rolling(window = windowForMethodology).apply(methodology))), label = tickerSymbols[index])
        if (volArbType == 'Type2'):
            plt.plot(minMaxScaler(pd.DataFrame(dataset.Close.pct_change().rolling(window = windowForMethodology).apply(methodology))), label = tickerSymbols[index])
        if (volArbType == 'Type3'):
            toBeAdjustedManually = ['SPXL', 3] # This is the only line that would need to be adjusted to use Type3 volArbType for a different pair of products. SPXL is a triple (3x) leveraged ETF. 
            if (toBeAdjustedManually[0] not in tickerSymbols):
                raise ValueError('Note: Type3 volArbType requires the user to input parameters directly into the source code.')
            # Might be wise to just have a csv file going with all leveraged ETPs and their leverage factors if this type is something you want to explore further.
            if tickerSymbols[index] == toBeAdjustedManually[0]:
                plt.plot(((pd.DataFrame(dataset.Close.pct_change() / toBeAdjustedManually[1])).rolling(window = windowForMethodology).apply(methodology)), label = tickerSymbols[index])
            else:
                plt.plot(((pd.DataFrame(dataset.Close.pct_change())).rolling(window = windowForMethodology).apply(methodology)), label = tickerSymbols[index])
                
        # If you want to set your own custom colors, something like this works:
        if (len(datasets) == 2):
            if ((index % 2) == 0):
                plt.gca().get_lines()[-1].set_color('red')
            else:
                plt.gca().get_lines()[-1].set_color('blue')
        
        plt.title(('volArbType = ' + str(volArbType)), loc = 'left', fontsize = 16)

    plt.xticks([])
    plt.yticks([])
    plt.legend(loc = 'upper left', fontsize = 13)
    plt.axis('off')
    fig = plt.gcf()
    fig.set_size_inches(14.275, 4.762)


def twoAssetVolArbDifferences(datasets: list[pd.DataFrame],
                              volArbType: Optional[str] = 'Type1',
                              methodology: Optional[Callable[Union[pd.DataFrame.std, pd.DataFrame.var], int]] = pd.DataFrame.std, # works for stuff like .kurtosis too
                              windowForMethodology: Optional[int] = 10,
                              show: Optional[bool] = False) -> None:
    
    '''
    Used for taking the differences in deviation for two series of the respective volArbType. Supports two volArbTypes.
    Is used in monoPointArb(), tailComparison(), and polyPointArb().
    
    Parameters
    ----------
    datasets : list[pd.DataFrame]
        Takes in a list of time series dataframes for two to perform computations on.
    volArbType : Optional[str]
        Determines which type of volatility arbitrage to perform.
        Takes one of two inputs:
           'Type1' ... Normalizes the time series (using min-max scaling) after the desired computations have been applied to the series. Uses a raw price series.
           'Type2' ... Normalizes the time series (using min-max scaling) after the desired computations have been applied to the series. Uses a percentage change series.
    methodology : Optional[Callable[Union[pd.DataFrame.std, pd.DataFrame.var], int]]
        Defines whether to use standard deviation or variance for the computation. Conveniently, also works for stuff like pd.DataFrame.kurtosis, or pd.DataFrame.median. 
    windowForMethodology : Optional[int]
        Passes the size of the moving window to the rolling function. Default is 10.
    show : Optional[bool]
        Determines whether or not to use the function to compute and show the differences using a plot. Default is False.
    '''
    
    fullFrameValues = []

    for index, dataset in enumerate(datasets):
    
        if (volArbType == 'Type1'):
            fullFrameValues.append(minMaxScaler(pd.DataFrame(dataset.Close.rolling(window = windowForMethodology).apply(methodology))))
 
        if (volArbType == 'Type2'):
            fullFrameValues.append((minMaxScaler(pd.DataFrame(dataset.Close)).rolling(window = windowForMethodology).apply(methodology)))
  
    if (fullFrameValues == []):
        raise ValueError('Note: fullFrameValues is empty. This is likely to be the result of an invalid volArbType variable being passed.')
    else:
        if (show == True):
            ax1 = (fullFrameValues[0] - fullFrameValues[1]).plot(color = 'black', figsize = [ 14.725,9.525], legend = False)
            ax1.set_title('Difference between Standard Deviations for ' + str(windowForMethodology) + ' Period ' + str(volArbType) + ' Computation', fontsize = 16)
            ax1.axhline(0, linewidth = 1, color = 'firebrick')
            ax1.minorticks_on()
            ax1.grid(which = 'both', linestyle = '-', linewidth = '0.9', color = 'dimgrey')
            ax1.grid(which = 'minor', linestyle = ':', linewidth = '0.9', color = 'grey')
            plt.pause(0.01)
            
        if (show == False):
            return (fullFrameValues[0] - fullFrameValues[1]) 


def monoPointArb(datasets: list[pd.DataFrame],
                methodology: Optional[Callable[Union[pd.DataFrame.std, pd.DataFrame.var], int]] = pd.DataFrame.std, # works for stuff like .kurtosis too
                windowForMethodology: Optional[int] = 10) -> None:

    '''
    Used for calculating the level of arbitrage at the current time-step (the most recent unit in each dataframe). Uses a blend of differences computed from the processes for both the 'Type1' and 'Type2' volArbType argument.
    Returns a number to measure the level of arbitrage. Parity exists when this function's output is equal to  1.00.
    
    Parameters
    ----------
    datasets : list[pd.DataFrame]
        Takes in a list of time series dataframes for two to perform computations on.
    methodology : Optional[Callable[Union[pd.DataFrame.std, pd.DataFrame.var], int]]
        Defines whether to use standard deviation or variance for the computation. Conveniently, also works for stuff like pd.DataFrame.kurtosis, or pd.DataFrame.median. 
    windowForMethodology : Optional[int]
        Passes the size of the moving window to the rolling function. Default is 10.
    '''
    
    differenceFrames =  pd.concat([twoAssetVolArbDifferences(datasets, volArbType = 'Type1', methodology = methodology, windowForMethodology = windowForMethodology),
                                   twoAssetVolArbDifferences(datasets, volArbType = 'Type2', methodology = methodology, windowForMethodology = windowForMethodology)], axis = 1)
    medianOfTheMedians = differenceFrames.median(axis = 1).median(axis = 0)
    lastUnitOfMediansFrame = differenceFrames.median(axis = 1).iloc[-1]
        
    if ((abs(lastUnitOfMediansFrame) / abs(medianOfTheMedians)) < 1):
        return ((-(1 / (abs(lastUnitOfMediansFrame) / abs(medianOfTheMedians)))))
    elif ((abs(lastUnitOfMediansFrame) / abs(medianOfTheMedians)) >= 1):
        return (abs(lastUnitOfMediansFrame) / abs(medianOfTheMedians))


def polyPointArb(datasets: list[pd.DataFrame],
                 methodology: Optional[Callable[Union[pd.DataFrame.std, pd.DataFrame.var], int]] = pd.DataFrame.std) -> None:
   
    '''
    Used for calculating the level of arbitrage at the current time-step (the most recent unit in each dataframe), based on numerous combinations of parameters.
    Uses a blend of differences computed from the processes for the 'Type1' and 'Type2' volArbType argument, but uses instead a series of numbers for windowForMethodology.
    polyPointArb() also uses a series of numbers to call the batcher() function, which spaces the data units in different ways than just the space which was fed into input.
    In general, the function can be thought of as a nested, or double for-loop. I personally like how the tqdm progress bars are right now, but you may not. Turn them off if 
    this is the case by removing them from the start of the for-loops. Returns a series of numbers to measure the level of arbitrage for each combination the function generates. 
    It is worth noting that I've built this with blending this series of numbers eventually into 1 final value, like monoPointArb() in mind. I did this in hopes of finding a more 
    accurate measurement.

    
   Parameters
    ----------
    datasets : list[pd.DataFrame]
        Takes in a list of time series dataframes for two to perform computations on.
    methodology : Optional[Callable[Union[pd.DataFrame.std, pd.DataFrame.var], int]]
        Defines whether to use standard deviation or variance for the computation. Conveniently, also works for stuff like pd.DataFrame.kurtosis, or pd.DataFrame.median. 
    '''
     
    arbValues = []
    windows = list(range(2, round(len(datasets[0]) / 2)))
    
    for window in tqdm(windows):
        tempBatchesAssetOne, tempBatchesAssetTwo = [], []
        for datasetIndex, dataset in enumerate(datasets):
            batchedData = batcher(dataset.Close, (round(len(dataset) / 2)), window)
            batchedData = batchedData[window::]
            if (datasetIndex == 0):
                tempBatchesAssetOne.append(batchedData)
            elif (datasetIndex == 1):
                tempBatchesAssetTwo.append(batchedData)
                batchesForCurrentWindow = list((list1 + list2) for list1, list2 in zip(list(chain(*tempBatchesAssetOne)), list(chain(*tempBatchesAssetTwo))))
                batchForCurrentWindow = []
                for batchesIndex, batches in enumerate(batchesForCurrentWindow):
                    batchForCurrentWindow.append([(pd.DataFrame((batches[:(int(len(batches) / 2))]), columns = ['Close'])),
                                                  (pd.DataFrame((batches[(int(len(batches) / 2)):]), columns = ['Close']))])
            
        for batch in tqdm(batchForCurrentWindow):
            arbLevel = monoPointArb(batch, methodology = methodology)
            if (arbLevel != None):
                if ((arbLevel == 1.00) and (arbValues[-1] == 1.00)): # I figure that it's unlikely if not impossible that there will be 2 naturally occurring values back to back equal to 1.00.
                    break
                else:
                    arbValues.append(arbLevel)
        
    return pd.DataFrame(arbValues[:(len(arbValues) - 1)], columns = ['arbLevels'])


def tailsComparison(datasets: list[pd.DataFrame],
                   methodology: Optional[Callable[Union[pd.DataFrame.std, pd.DataFrame.var], int]] = pd.DataFrame.std) -> None:
 
    '''
    Multiplies the length of the polyPointArb() output by 12%, and then takes the nth largest/smallest numbers on both sides of the
    distribution ((len(polyPointArb()) * 0.12) numbers on each side of the distriution), and adds them up. Then, a comparison 
    between the two is returned In terms of "smaller tails are __output__ times smaller than larger tails," if value is negative,
    or "smaller tails are __output__ times larger than larger tails," if positive. This function would probably be better off bundled
    into polyPointArb() for runtime purposes, but to improve readability I've written it as a separate function.'
 
    Parameters
    ----------
    datasets : list[pd.DataFrame]
        Takes in a list of time series dataframes for two to perform computations on.
    methodology : Optional[Callable[Union[pd.DataFrame.std, pd.DataFrame.var], int]]
        Defines whether to use standard deviation or variance for the computation. Conveniently, also works for stuff like pd.DataFrame.kurtosis, or pd.DataFrame.median. 
    '''
    
    polyArbLevels = polyPointArb(datasets = datasets,
                                 methodology = methodology)
    
    if ((float(abs(polyArbLevels.nsmallest(round(len(polyArbLevels) * 0.12), columns = ['arbLevels']).sum()) / abs(polyArbLevels.nlargest(round(len(polyArbLevels) * 0.12), columns = ['arbLevels']).sum()))) < 1):
        return (-(1 / (float(abs(polyArbLevels.nsmallest(round(len(polyArbLevels) * 0.12), columns = ['arbLevels']).sum()) / abs(polyArbLevels.nlargest(round(len(polyArbLevels) * 0.12), columns = ['arbLevels']).sum())))))
    else:
        return (float(abs(polyArbLevels.nsmallest(round(len(polyArbLevels) * 0.12), columns = ['arbLevels']).sum()) / abs(polyArbLevels.nlargest(round(len(polyArbLevels) * 0.12), columns = ['arbLevels']).sum())))


from claydates import MultiTickerProcessor
tickerObjects = MultiTickerProcessor(['SPY','SPXL'], '1min', 300) 
fullDatasetForVolArb = tickerObjects.missingUnitsExcluded(matchDates = 'True')
tickerSymbols = tickerObjects._tickerSymbols


# Usage 1
multiAssetArbPlot(datasets = fullDatasetForVolArb,
                  volArbType = 'Type1',
                  methodology = pd.DataFrame.std,
                  windowForMethodology = 10)

# Usage 2
differences = twoAssetVolArbDifferences(datasets = fullDatasetForVolArb,
                                        volArbType = 'Type1',
                                        methodology = pd.DataFrame.std,
                                        windowForMethodology = 10,
                                        show = True)

# Usage 3
monoArbLevel = monoPointArb(datasets = fullDatasetForVolArb,
                            methodology = pd.DataFrame.std,
                            windowForMethodology = 10)
print(monoArbLevel)

# Usage 4
polyArbLevels = polyPointArb(datasets = fullDatasetForVolArb,
                             methodology = pd.DataFrame.std)
print(float(polyArbLevels.median())) # to represent the series as a single number.


# Usage 5
tailsRatio = tailsComparison(datasets = fullDatasetForVolArb,
                            methodology = pd.DataFrame.std)
print(tailsRatio)

