#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : Exploratory Data Analysis Framework                                                 #
# Version    : 0.1.19                                                                              #
# Python     : 3.10.12                                                                             #
# Filename   : /d8analysis/visual/rv_continuous.py                                                 #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john.james.ai.studio@gmail.com                                                      #
# URL        : https://github.com/john-james-ai/d8analysis                                         #
# ------------------------------------------------------------------------------------------------ #
# Created    : Friday August 11th 2023 06:37:59 pm                                                 #
# Modified   : Friday August 11th 2023 09:35:57 pm                                                 #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2023 John James                                                                 #
# ================================================================================================ #
"""Continuous Random Variable Probability Distributions"""

import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from scipy import stats

from d8analysis.visual.base import Plot
from d8analysis.visual.config import Canvas
from d8analysis.quantitative.statistical.centrality.ttest import TTestResult


# ------------------------------------------------------------------------------------------------ #
#                            STUDENT'S T CONTINUOUS RANDOM VARIABLE                                #
# ------------------------------------------------------------------------------------------------ #
class StudentsTPDF(Plot):  # pragma: no cover
    """Plots a Student's t probability density function (PDF) for a student's t-test.

    Parameterized by the t-statistic, degrees of freedom and the signficance level, this
    object plots the PDF and the hypothesis test reject region.

    Args:
        result (TTestResult): A Student's t-test result object.
        ax (plt.Axes): A matplotlib Axes object. Optional. If  If not none, the ax parameter
            overrides the default set in the base class.
        title (str): The visualization title. Optional
        canvas (Canvas): A dataclass containing the configuration of the canvas
            for the visualization. Optional.
        args and kwargs passed to the underlying seaborn histplot method.
            See https://seaborn.pydata.org/generated/seaborn.histplot.html for a
            complete list of parameters.
    """

    def __init__(
        self,
        result: TTestResult,
        ax: plt.Axes = None,
        title: str = None,
        canvas: Canvas = None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(canvas=canvas)
        self._result = result
        self._ax = ax
        self._title = title
        self._args = args
        self._kwargs = kwargs

        self._legend_config = None
        sns.set_style(self._canvas.style)

    def plot(self) -> None:
        self._ax = self._ax or self.config_axes()

        # Render the probability distribution
        x = np.linspace(
            stats.t.ppf(0.001, self._result.dof), stats.t.ppf(0.999, self._result.dof), 500
        )
        y = stats.t.pdf(x, self._result.dof)
        self._ax = sns.lineplot(x=x, y=y, markers=False, dashes=False, sort=True, ax=self._ax)

        # Compute reject region
        lower = x[0]
        upper = x[-1]
        lower_alpha = self._result.alpha / 2
        upper_alpha = 1 - (self._result.alpha / 2)
        lower_critical = stats.t.ppf(lower_alpha, self._result.dof)
        upper_critical = stats.t.ppf(upper_alpha, self._result.dof)

        self._fill_reject_region(
            lower=lower, upper=upper, lower_critical=lower_critical, upper_critical=upper_critical
        )

        self._ax.set_title(
            f"{self._result.result}",
            fontsize=self._canvas.fontsize_title,
        )

        # ax.set_xlabel(r"$X^2$")
        self._ax.set_ylabel("Probability Density")
        plt.tight_layout()

        if self._legend_config is not None:
            self.config_legend()

    def _fill_reject_region(
        self,
        lower: float,
        upper: float,
        lower_critical: float,
        upper_critical: float,
    ) -> None:
        """Fills the area under the curve at the value of the hypothesis test statistic."""

        # Fill lower tail
        xlower = np.arange(lower, lower_critical, 0.001)
        self._ax.fill_between(
            x=xlower,
            y1=0,
            y2=stats.t.pdf(xlower, self._result.dof),
            color=self._canvas.colors.crimson,
        )

        # Fill Upper Tail
        xupper = np.arange(upper_critical, upper, 0.001)
        self._ax.fill_between(
            x=xupper,
            y1=0,
            y2=stats.t.pdf(xupper, self._result.dof),
            color=self._canvas.colors.crimson,
        )

        # Plot the statistic
        line = self._ax.lines[0]
        xdata = line.get_xydata()[:, 0]
        ydata = line.get_xydata()[:, 1]
        statistic = round(self._result.value, 4)
        try:
            idx = np.where(xdata > self._result.value)[0][0]
            x = xdata[idx]
            y = ydata[idx]
            _ = sns.regplot(
                x=np.array([x]),
                y=np.array([y]),
                scatter=True,
                fit_reg=False,
                marker="o",
                scatter_kws={"s": 100},
                ax=self._ax,
                color=self._canvas.colors.dark_blue,
            )
            self._ax.annotate(
                f"t = {str(statistic)}",
                (x, y),
                textcoords="offset points",
                xytext=(0, 10),
                ha="center",
            )

            self._ax.annotate(
                "Critical Value",
                (lower_critical, 0),
                textcoords="offset points",
                xytext=(20, 15),
                ha="left",
                arrowprops={"width": 2, "shrink": 0.05},
            )

            self._ax.annotate(
                "Critical Value",
                (upper_critical, 0),
                xycoords="data",
                textcoords="offset points",
                xytext=(-20, 15),
                ha="right",
                arrowprops={"width": 2, "shrink": 0.05},
            )
        except IndexError:
            pass
