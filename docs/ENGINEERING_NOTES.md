# Engineering Notes

## 1. What part of this assignment was easiest for you?

Writing the feature extraction logic was the most straightforward
part. I already had a mental model for what makes a URL look
suspicious from my final-year project (PhishGuard AI), so translating
that into clean, testable functions came fairly naturally. Getting
each feature to have a clear, defensible reason attached to it (rather
than just generating columns) was something I could reason through
without much friction.

## 2. What part was hardest?

Environment setup, honestly — not the machine learning or the API
code itself. I ran into a long sequence of tooling issues: Git not
being installed correctly, PowerShell's execution policy blocking
conda activation, files repeatedly landing in the wrong nested
folders, a local Docker install that couldn't run at all due to a
virtualization limitation on my laptop's hardware, and finally a
payment-verification wall on the cloud platforms I tried for
deployment. None of these were about understanding the concepts —
they were about getting my actual development environment to
cooperate, which ate a disproportionate amount of time relative to
writing the actual application logic.

## 3. What did you have to learn?

I hadn't worked with FastAPI, Pydantic schemas, or Docker in a real
project context before this assessment — I understood the concepts
loosely but had to actually build with them for the first time here.
I also had to properly learn Git/GitHub Desktop workflows beyond the
basics, since I discovered partway through that several of my early
commits had never actually been pushed to GitHub, which forced me to
understand the difference between a local commit and a pushed one in
a very concrete way.

## 4. What technical decision did you initially get wrong?

My model selection logic initially picked the final model purely by
highest recall, without accounting for ties. Two of my three models
tied on recall, and the code just silently picked whichever one came
first in the dictionary rather than making a real decision. I caught
this myself when comparing the full metrics table and noticed
XGBoost actually beat the tied competitor on every other metric — I
fixed the logic to explicitly break ties using F1 score and recorded
the reasoning in both the code's saved metadata and this document,
rather than leaving an arbitrary tie-break baked into the model
selection.

## 5. What would you improve with another week?

I'd finish the cloud deployment properly rather than documenting it
as a limitation — the payment verification requirement on Render and
Koyeb was the actual blocker, not anything about the Docker
configuration itself, which I did get working and verified locally.
I'd also add the optional production enhancements I didn't get to:
rate limiting, request size limits, and a CI/CD pipeline via GitHub
Actions. And I'd go back and migrate the FastAPI startup handling
from `@app.on_event` (deprecated) to the newer lifespan-handler
pattern, which I noticed but didn't have time to properly address.

## 6. Which part of your implementation would you not be comfortable supporting in production?

The deployment story, currently — since I couldn't get a live cloud
deployment working within the timeframe, I can't speak from firsthand
experience about how this service behaves under real network
conditions, concurrent load, or actual production traffic patterns.
Everything I've verified has been local or containerized-but-local.
I'd want to actually run this in a real cloud environment, watch it
handle real traffic, and see what breaks before I'd call it
production-ready.