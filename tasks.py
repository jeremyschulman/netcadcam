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
