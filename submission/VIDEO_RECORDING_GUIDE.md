# Demo video and presentation notes

`PULSE_Demo.mp4` is an actual browser recording, without narration. It shows the synthetic Northstar Studio workspace. The financial API is real and browser requests were not mocked. The n8n editor is also supplied as screenshot 12.

Suggested live narration, following the visible screens:

1. Introduce PULSE as a financial copilot for SMEs and open the sign-in screen.
2. Show company onboarding and the dashboard. Explain that current cash is EUR 7,020, but a positive balance today does not guarantee future liquidity.
3. Open the forecast and risk alert: the baseline reaches EUR -2,308 and spends seven days below zero.
4. Ask the copilot about runway. Explain that this demonstration uses deterministic mode and obtains figures from the financial engine.
5. Open the Digital Twin. Compare the baseline with a 15-day supplier delay: the minimum becomes EUR 2,064 with no days below zero. This is a scenario to discuss with a supplier, not an automatically executed change.
6. Review the proposed invoice reminder and explicitly approve it. Show the audit history. External delivery is disabled in this synthetic run, so the action remains queued rather than falsely marked sent.
7. Close with the shared Supabase PostgreSQL architecture, human approval and transparent uncertainty.

The PowerPoint contains a separate speaker script in each slide's notes. The deck is designed for an approximately ten-minute pitch including the demonstration.
