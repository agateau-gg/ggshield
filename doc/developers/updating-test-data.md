# Updating test data

This document explains how to refresh the snapshots and cassettes used in ggshield test suite.

Remove --disable-socket from pyproject.toml. Otherwise [pytest-socket][] won't let us acces the network.

    sed -i 's/--disable-socket//' pyproject.toml

[pytest-socket]: https://pypi.org/project/pytest-socket/

Remove cassettes:

    rm -f tests/cassettes/*

Make sure `$TEST_GITGUARDIAN_API_KEY` is set.

Run `pytest` and make it update snapshots:

    pytest --snapshot-update

Fix any failures.

Add back --disable-socket:

    git checkout pyproject.toml
