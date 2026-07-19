# Demo Walkthrough

1. Run `make model` to download the MoveNet ONNX model.
2. Run `make download-data` and `make public-demo` to generate the public Wikimedia squat demo artifacts.
3. Start the API and create/login a user.
4. Create an organization and copy its ID into `X-Organization-ID`.
5. Create a subject and session.
6. Upload MP4 or WebM media.
7. Run the worker or explicit local job endpoint.
8. Open analysis summary and compressed pose endpoints.
9. In the web app, set `mf_token` and `mf_org` in local storage, then open `/analysis/<session-id>`.
10. Seek the shared cursor and inspect the 3D skeleton, timeline, score breakdown, and events.
11. Add a timestamped note, review an event, and generate the PDF report.
12. Open `/preview` or `/analysis/demo` to view the packaged public dataset demo.
