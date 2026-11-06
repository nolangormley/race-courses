# deploy

The weekly crawl runs on a machine outside the cloud.
Many organizer sites answer 403 to the IP ranges of GitHub Actions and other clouds, also when the user agent says what the crawler is.
It runs as a systemd user timer on yasmodeus (a CMU workstation) and pushes with a deploy key that can write only to this repository.

- `weekly-crawl.sh`: `uv sync`, `race-courses crawl`, then commit and push what changed.
- `race-courses-crawl.service`: resets the checkout in `~/race-courses` to `origin/main` (it holds no work of its own), then runs the script, at nice 10 and for at most 5 hours.
- `race-courses-crawl.timer`: Monday 03:23 New York time; `Persistent=true` runs a missed crawl after a reboot.

Setup on a new machine (the user needs lingering, `loginctl enable-linger`, so the timer runs without a login):
1. `ssh-keygen -t ed25519 -f ~/.ssh/race_courses_deploy -N ""`, and add the public key to the repository as a deploy key with write access.
2. Clone with `GIT_SSH_COMMAND="ssh -i ~/.ssh/race_courses_deploy -o IdentitiesOnly=yes" git clone git@github.com:nolangormley/race-courses.git ~/race-courses`.
   In the clone, set `core.sshCommand` to that same command, and `user.name` and `user.email` for the crawl's commits.
3. `systemctl --user link ~/race-courses/deploy/race-courses-crawl.service`, then `systemctl --user enable --now ~/race-courses/deploy/race-courses-crawl.timer`.
   `systemctl --user start race-courses-crawl` crawls now.

Logs: `journalctl --user -u race-courses-crawl`.
