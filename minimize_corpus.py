import click

from pathlib import Path

import subprocess

import os

import multiprocessing


FNULL = open(os.devnull, 'w')


def worker(fuzzed_app, infile, outfile, t=None, m=None, f=None):
    click.echo("Processing {}...".format(infile))
    cmd = ["afl-tmin"]

    if t:
        cmd.append("-t")
        cmd.append(t)

    if m:
        cmd.append("-m")
        cmd.append(m)

    if f:
        cmd.append("-f")
        cmd.append(f)

    cmd.append("-i")
    cmd.append(infile)

    cmd.append("-o")
    cmd.append(outfile)

    cmd.append("--")
    cmd.append(" ".join(fuzzed_app))

    subprocess.call(" ".join(cmd), shell=True, stdout=FNULL, stderr=FNULL)
    # subprocess.call(cmd)
    # click.echo(" ".join(cmd))


@click.command()
@click.argument("corpus", type=click.Path(exists=True))
@click.argument("outdir", type=click.Path())
@click.argument("fuzzed_app", nargs=-1)
@click.option("-n", type=int, default=1,
              help="Number of afl-tmin instances to launch")
@click.option("-t", help="afl-tmin -t option (timeout)")
@click.option("-m", help="afl-tmin -m option (memory limit)")
@click.option("-f", help="afl-tmin -f option (input file)")
def cli(corpus, outdir, fuzzed_app, n, t, m, f):
    click.echo("Spawning {} workers...".format(n))
    pool = multiprocessing.Pool(processes=n)

    if not os.path.exists(outdir):
        os.makedirs(outdir)

    p = Path(corpus)
    for case in p.iterdir():
        args = [fuzzed_app, str(case), "{}/{}".format(outdir, case.name)]
        kwargs = {}
        if t:
            kwargs["t"] = t
        if m:
            kwargs["m"] = m
        if f:
            kwargs["f"] = f

        pool.apply_async(worker, args, kwargs)

    pool.close()
    pool.join()


if __name__ == "__main__":
    cli()
