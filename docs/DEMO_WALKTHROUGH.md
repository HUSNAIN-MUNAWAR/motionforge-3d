# Demo Walkthrough

1. Run `make verify` to create a measured controlled-video result and PDF.
2. Start the API and create/login a user.
3. Create an organization and copy its ID into `X-Organization-ID`.
4. Create a subject and session.
5. Upload MP4 media.
6. Run the worker or explicit local job endpoint.
7. Open analysis summary and compressed pose endpoints.
8. In the web app, set `mf_token` and `mf_org` in local storage, then open `/analysis/<session-id>`.
9. Seek the shared cursor and inspect the 3D skeleton, timeline, score breakdown, and events.
10. Add a timestamped note, review an event, and generate the PDF report.
