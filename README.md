# BeckerChecklistApp

## Abstract

Simple job progress tracking application. In use for Becker Home Maintinence and Becker Builders.

## Note

There is some hacky stuff going on here. The app runs as an ephemeral GCP cloud run instance and uses sqlite file db (cheap cheap). So the db is actually persisted between containers/instances, the app syncs the db file to cloud storage on every create, update, and delete.
