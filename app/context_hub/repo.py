from __future__ import annotations

from pathlib import Path

from git import InvalidGitRepositoryError, Repo

from app.config import settings


class ContextHubRepo:
    def __init__(self) -> None:
        self.path = Path(settings.context_hub_path)

    def pull_latest(self) -> None:
        try:
            repo = Repo(self.path)
        except InvalidGitRepositoryError:
            return

        if not repo.remotes:
            return

        repo.remotes[0].pull(rebase=True)

    def commit_and_push(self, message: str) -> None:
        try:
            repo = Repo(self.path)
        except InvalidGitRepositoryError:
            return

        if repo.is_dirty(untracked_files=True):
            repo.git.add(all=True)
            repo.index.commit(message)

        if repo.remotes:
            repo.remotes[0].push()

