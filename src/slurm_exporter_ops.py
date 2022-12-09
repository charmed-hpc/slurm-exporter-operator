# Copyright 2022 Omnivector Solutions LLC
# See LICENSE file for licensing details.

"""Slurm Exporter Ops."""

import logging
import shlex
import shutil
import subprocess
import tarfile
from tempfile import TemporaryDirectory
from pathlib import Path

logger = logging.getLogger(__name__)


class SlurmExporterOps:
    """SlurmExporter system operations."""

    def __init__(self):
        """Initialize class."""
        self._template_dir = Path(__file__).parent.parent / "templates"

        self._systemd_service = "prometheus-slurm-exporter.service"
        self._environment_file = Path("/etc/default/prometheus-slurm-exporter")

        self._binary_path = Path("/usr/bin/prometheus-slurm-exporter")
        self._varlib_path = Path("/var/lib/slurm_exporter")
        self._slurm_exporter_user = "prometheus_slurm_exporter"
        self._slurm_exporter_group = "prometheus_slurm_exporter"

    def install(self, resource_path: Path):
        """Install slurm-exporter."""
        logger.debug("## Installing slurm-exporter")

        # extract resource tarball
        with TemporaryDirectory(prefix="omni") as tmp_dir:
            logger.debug(f"## extracting {resource_path} to {tmp_dir}")
            with tarfile.open(resource_path, 'r') as tar:
                
                import os
                
                def is_within_directory(directory, target):
                    
                    abs_directory = os.path.abspath(directory)
                    abs_target = os.path.abspath(target)
                
                    prefix = os.path.commonprefix([abs_directory, abs_target])
                    
                    return prefix == abs_directory
                
                def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
                
                    for member in tar.getmembers():
                        member_path = os.path.join(path, member.name)
                        if not is_within_directory(path, member_path):
                            raise Exception("Attempted Path Traversal in Tar File")
                
                    tar.extractall(path, members, numeric_owner=numeric_owner) 
                    
                
                safe_extract(tar, path=tmp_dir)

            logger.debug(f"## installing binary in {self._binary_path}")

            if self._binary_path.exists():
                logger.debug("## removing old binary")
                self._binary_path.unlink()
            shutil.copy2(Path(tmp_dir) / "prometheus-slurm-exporter", self._binary_path)

        self._create_slurm_exporter_user_group()
        self._create_systemd_service_unit()

    def uninstall(self):
        """Uninstall slurm-exporter."""
        logger.debug("## Stopping prometheus-slurm-exporter")
        self._systemctl("stop")
        self._systemctl("disable")

        logger.debug("## Uninstalling slurm-exporter")
        try:
            self._binary_path.unlink()
            shutil.rmtree(self._varlib_path)
        except FileNotFoundError:
            logger.debug("## Files already removed")

        # remove user and group
        subprocess.call(["userdel", self._slurm_exporter_user])
        subprocess.call(["groupdel", self._slurm_exporter_group])

        # remove systemd files
        Path(f"/etc/systemd/system/{self._systemd_service}").unlink()
        self._environment_file.unlink()
        self._systemctl("daemon-reload")

    def configure(self, params: dict):
        """Configure slurm-exporter and restart service."""
        logger.debug(f"## Writing {self._environment_file} with {params}")

        template_file = self._template_dir / "prometheus-slurm-exporter.tmpl"
        template = template_file.read_text()
        self._environment_file.write_text(template.format(**params))

        self._systemctl("restart")

    def start(self):
        """Start slurm-exporter."""
        self._systemctl("start")

    def _create_slurm_exporter_user_group(self):
        logger.debug("## Creating slurm_exporter group")
        group = self._slurm_exporter_group
        cmd = f"groupadd {group}"
        subprocess.call(shlex.split(cmd))

        logger.debug("## Creating slurm_exporter user")
        user = self._slurm_exporter_user
        home = self._varlib_path
        cmd = f"useradd --system --home-dir {home} --gid {group} --shell /usr/sbin/nologin {user}"
        subprocess.call(shlex.split(cmd))

    def _create_systemd_service_unit(self):
        logger.debug("## Creating systemd service unit for slurm-exporter")

        ctxt = dict()
        ctxt["binary_path"] = self._binary_path
        ctxt["environment_file"] = self._environment_file
        ctxt["username"] = self._slurm_exporter_user
        ctxt["groupname"] = self._slurm_exporter_group

        template_file = self._template_dir / f"{self._systemd_service}.tmpl"
        template = template_file.read_text()
        Path(f"/etc/systemd/system/{self._systemd_service}").write_text(template.format(**ctxt))

        self._systemctl("daemon-reload")
        self._systemctl("enable")

    def _systemctl(self, command: str):
        cmd = f"systemctl {command}"
        if command != "daemon-reload":
            cmd = cmd + " " + self._systemd_service

        logger.debug(f"## Running {cmd}")
        subprocess.call(shlex.split(cmd))
