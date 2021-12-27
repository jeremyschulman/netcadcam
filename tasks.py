#  Copyright (c) 2021 Jeremy Schulman
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from invoke import task


@task
def precheck(ctx):
    ctx.run("black .")
    ctx.run("pre-commit run -a")
    ctx.run("interrogate -c pyproject.toml", pty=True)


@task
def clean(ctx):
    ctx.run("python setup.py clean")
    ctx.run("rm -rf netcfgbu.egg-info")
    ctx.run("rm -rf .pytest_cache .pytest_tmpdir .coverage")
    ctx.run("rm -rf htmlcov")
