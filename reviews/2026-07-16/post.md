HINDCAST closes a leak in how we test language models as forecasters, grading them on foresight instead of recall.

Researchers from Arizona State University built a test that replays resolved prediction markets against a frozen snapshot of public Reddit, letting a model read only what was posted before the market closed. The model's forecast is scored against both the actual outcome and the market's own price at that past time. On this leakage-free test, retrieval-augmented forecasting lowers the error score for eight of nine models tested.

The gain is narrower than it sounds. Retrieval only helps where the Reddit archive contained factual discussion about the event beforehand. On markets where the archive carried mostly speculation, such as in entertainment, retrieval actually makes the forecasts worse. The system's performance is constrained by the quality of signal available in the past.

For teams building or buying forecasting systems, the implication is that evidence quality matters more than model size alone. A test that simulates a past decision point, like HINDCAST, is a better gauge of real-world usefulness than one contaminated by future knowledge. This shifts the evaluation focus from what a model knows to what it could have known when it mattered.

Worth reading if you evaluate AI systems for decision-making under uncertainty.

Paper: Hindcast: Replaying Prediction Markets to Evaluate LLM Forecasters, Ye et al.
https://arxiv.org/abs/2607.14051

#AI #Forecasting #Evaluation #ModelRisk #Hindcast