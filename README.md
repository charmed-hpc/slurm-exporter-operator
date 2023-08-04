# Prometheus Slurm Exporter Charm

[Prometheus Slurm Exporter](https://github.com/vpenso/prometheus-slurm-exporter)
exposes [Slurm](https://slurm.schedmd.com/) metrics.

## Quickstart

Deploy the `slurm-exporter` and relate it to your
[slurmrestd](https://charmhub.io/slurmrestd) node:

```bash
$ juju deploy slurm-exporter
$ juju realate slurmrestd:juju-info slurm-exporter:juju-info
```

The charm can register it's scrape target with the [Prometheus
charm](https://charmhub.io/prometheus2) with the relation:

```bash
$ juju relate prometheus2:scrape slurm-exporter:prometheus
```

The [Grafana Dashboard 4323](https://grafana.com/dashboards/4323) provides a
visualization of the information exposed via this charm.

## Developing

We supply a `Makefile` with a target to build the charm and the resources
needed:

```bash
$ make charm
```

Once you have built the charm, use Juju to deploy it:

```bash
$ juju deploy ./slurm-exporter_ubuntu-20.04-amd64_ubuntu-22.04-amd64_centos-7-amd64_centos-8-amd64.charm --resource slurm-exporter=./slurm-exporter.tar.gz
```

## Contact

**We want to hear from you!**

Email us @ [info@omnivector.solutions](mailto:info@omnivector.solutions)

## Bugs

In the case things aren't working as expected, please
[file a bug](https://github.com/omnivector-solutions/charm-slurm-exporter/issues).

## License

The charm is maintained under the GPLv3 license. See `LICENSE` file in this
directory for full preamble.

Copyright &copy; Omnivector Solutions 2022
