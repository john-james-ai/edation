#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : Exploratory Data Analysis Framework                                                 #
# Version    : 0.1.19                                                                              #
# Python     : 3.10.10                                                                             #
# Filename   : /d8analysis/quantitative/descriptive/categorical.py                                 #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john.james.ai.studio@gmail.com                                                      #
# URL        : https://github.com/john-james-ai/d8analysis                                         #
# ------------------------------------------------------------------------------------------------ #
# Created    : Thursday June 8th 2023 02:56:56 am                                                  #
# Modified   : Saturday August 19th 2023 06:23:02 pm                                               #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2023 John James                                                                 #
# ================================================================================================ #
from dataclasses import dataclass
import statistics
from typing import Union

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from dependency_injector.wiring import inject, Provide

from d8analysis.quantitative.descriptive.base import DescriptiveOne
from d8analysis.container import D8AnalysisContainer
from d8analysis.visual.base import Canvas


# ------------------------------------------------------------------------------------------------ #
@dataclass
class CategoricalStats(DescriptiveOne):
    name: str  # Name of variable
    length: int  # total  length of variable
    count: int  # number of non-null values
    size: float  # total number of bytes
    mode: Union[int, str]
    unique: int

    @classmethod
    def describe(cls, x: Union[pd.Series, np.ndarray], name: str = None) -> None:
        name = name or cls.get_name(x=x)
        return cls(
            name=name,
            length=len(x),
            count=len(list(filter(None, x))),
            size=x.__sizeof__(),
            mode=statistics.mode(x),
            unique=len(np.unique(x)),
        )


# ------------------------------------------------------------------------------------------------ #
class CategoricalFreqDistribution:
    """Computes the frequency distribution of a categorical random variable

    data (Union[pd.DataFrame, pd.Series]): DataFrame or Series that has a value_counts method.
    x (str): A key in the DataFrame or Series.
    caps (bool): Whether to capitalize first letter of variables. Default = True
    canvas (Canvas): Configuration for the plot method

    """

    @inject
    def __init__(
        self,
        data: Union[pd.DataFrame, pd.Series],
        x: str,
        caps: bool = True,
        canvas: Canvas = Provide[D8AnalysisContainer.canvas.seaborn],
    ) -> None:
        self._data = data
        self._x = x
        self._caps = caps
        self._canvas = canvas
        self._freq = None

    def compute(self) -> pd.DataFrame:
        abs = (
            self._data[self._x].value_counts(normalize=False, sort=False, ascending=True).to_frame()
        )
        rel = (
            self._data[self._x].value_counts(normalize=True, sort=False, ascending=True).to_frame()
        )
        self._freq = abs.join(rel, on=self._x)
        self._freq.loc["Total"] = self._freq.sum()
        self._freq["cumulative"] = self._freq["proportion"].cumsum()

        if self._caps:
            self._x = self._x.capitalize()
            self._freq.columns = [col.capitalize() for col in self._freq.columns]

        self._freq.loc[self._freq.index[-1], self._freq.columns[-1]] = " "
        return self._freq

    def plot(self, title: str = None, ax: plt.Axes = None) -> None:  # pragma: no cover
        if ax is None:
            _, ax = self._canvas.get_figaxes()

        if title is None:
            title = "Distribution of " + self._x

        sns.set_palette(palette=self._canvas.palette)
        sns.set_style(self._canvas.style)

        sns.countplot(data=self._data, x=self._x)

        ax.set_title(label=title)
