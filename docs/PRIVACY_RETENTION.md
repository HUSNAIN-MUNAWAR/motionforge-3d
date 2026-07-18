# Privacy and Retention

Subjects may use anonymous codes. Height, weight, year of birth, notes, and consent fields are optional. Organizations should collect only data needed for the stated workflow.

A production deletion job should mark a session pending deletion, remove source media and derived artifacts, retry failed object deletion, anonymize or delete operational metadata, and retain only the minimum audit record required by policy. The repository models retention classification and auditability; automated legal-hold and deletion orchestration are documented extension points.
