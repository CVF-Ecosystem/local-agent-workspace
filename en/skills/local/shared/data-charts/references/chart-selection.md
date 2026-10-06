# Choosing a chart by the shape of the data

Suggestions for deciding how to present; not mandatory rules.

| What the reader should see | Usually fits | Avoid |
|---|---|---|
| Comparison between groups | Horizontal bars (long labels) or vertical bars, sorted by value | A pie chart with many slices |
| Change over time | Line; bars if only a few periods | Stacked bars with many groups, hard to compare |
| Composition (5 parts or fewer) | Stacked bar, donut or pie | 3D, too many slices |
| Composition changing by period | Stacked bars with the total above each bar | Many similar colour layers |
| One key number | KPI card with a comparison period | A decorative dial |
| Detailed list where figures must be looked up | Table, with small bars or a filter if needed | A chart when the reader needs exact figures |
| Relationship between two quantities | Scatter plot, only when there are many points | Joining the points with a line |

The template `assets/basic-charts.html` has ready KPI cards, line, horizontal bars, stacked bars,
donut and a table with bars. Other forms (scatter, map, network chart) must be built separately.

## Common mistakes

- Bars start at 0. A line chart may cut the axis but must state where the axis starts.
- Each chart makes one point; the title says what to see, not just the name of the indicator.
- State the unit, the reporting period and the source. A cell with no data shows "-" and breaks the line; it is not drawn as 0.
- Use few colours (about 5 or fewer) and add direct labels so it does not rely on colour alone.
- A closing balance is not added across periods; a rate is the total numerator divided by the total denominator.
- Percentages on a small sample mislead easily: add the absolute number.
- A chart shows a trend; it does not prove a cause.
