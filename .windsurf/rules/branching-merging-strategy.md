---
trigger: manual
---

# Code Branching Strategy

This is a set of instructions to the AI Assistant for branching and merging strategy.

1. Before making code changes
1.1. Grab the latest code from the `main` branch
1.2. Create a new branch
1.3. Switch to the newly created branch, and perform code changes there
1.4. Create and activate a python virtual environment
2. While making code changes
2.1. Write unit test to satisfy the requirement
2.2. Write code, until all unit tests pass
3. Completing making code changes
3.1. Commit all changes to repo
3.2. Push repo to Github.com
3.3. Create a PR from the newly create branch to the `main` branch
3.4. Assign the new PR to `raseniero`