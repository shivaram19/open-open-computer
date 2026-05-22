# tests/engines/test_compute_substrate.py
"""Tests for ComputeSubstrate implementations."""

import pytest
from engines.compute_substrate import (
    LocalSandboxSubstrate,
    MockVMSubstrate,
    DockerSubstrate,
    ExecutionEnvironment,
)


class TestMockVMSubstrate:
    def test_create_and_destroy(self):
        sub = MockVMSubstrate()
        env = sub.create(template="test")
        assert env.env_id.startswith("mock-")
        assert env.substrate_type == "mock"
        assert env.status == "running"

        assert len(sub.list_environments()) == 1
        sub.destroy(env)
        assert env.status == "destroyed"
        assert len(sub.list_environments()) == 0

    def test_execute_echo(self):
        sub = MockVMSubstrate()
        env = sub.create()
        result = sub.execute(env, "echo hello world")
        assert result["stdout"] == "hello world"
        assert result["return_code"] == 0

    def test_execute_unknown_command(self):
        sub = MockVMSubstrate()
        env = sub.create()
        result = sub.execute(env, "unknown-cmd")
        assert result["return_code"] == 127

    def test_file_io(self):
        sub = MockVMSubstrate()
        env = sub.create()
        sub.write_file(env, "/app/test.txt", "hello")
        assert sub.read_file(env, "/app/test.txt") == "hello"

    def test_read_missing_file(self):
        sub = MockVMSubstrate()
        env = sub.create()
        with pytest.raises(FileNotFoundError):
            sub.read_file(env, "/missing.txt")

    def test_checkpoint_and_restore(self):
        sub = MockVMSubstrate()
        env = sub.create()
        sub.write_file(env, "/data.txt", "v1")

        cp_id = sub.checkpoint(env)
        assert cp_id is not None
        assert env.checkpoint_count == 1

        sub.write_file(env, "/data.txt", "v2")
        assert sub.read_file(env, "/data.txt") == "v2"

        assert sub.restore(env, cp_id) is True
        assert sub.read_file(env, "/data.txt") == "v1"

    def test_hibernate_and_wake(self):
        sub = MockVMSubstrate()
        env = sub.create()
        sub.write_file(env, "/state.txt", "active")

        assert sub.hibernate(env) is True
        assert env.status == "hibernated"

        assert sub.wake(env) is True
        assert env.status == "running"
        assert sub.read_file(env, "/state.txt") == "active"

    def test_multiple_environments_isolated(self):
        sub = MockVMSubstrate()
        env1 = sub.create()
        env2 = sub.create()
        sub.write_file(env1, "/file.txt", "A")
        sub.write_file(env2, "/file.txt", "B")
        assert sub.read_file(env1, "/file.txt") == "A"
        assert sub.read_file(env2, "/file.txt") == "B"


class TestLocalSandboxSubstrate:
    def test_create_execute_destroy(self, tmp_path):
        sub = LocalSandboxSubstrate(workspace_root=str(tmp_path / "sandboxes"))
        env = sub.create(template="test")
        assert env.substrate_type == "local"

        result = sub.execute(env, "echo hello")
        assert result["stdout"].strip() == "hello"
        assert result["return_code"] == 0

        sub.write_file(env, "/test.txt", "content")
        assert sub.read_file(env, "/test.txt") == "content"

        sub.destroy(env)
        assert env.status == "destroyed"

    def test_timeout(self, tmp_path):
        sub = LocalSandboxSubstrate(workspace_root=str(tmp_path / "sandboxes"))
        env = sub.create()
        result = sub.execute(env, "sleep 5", timeout=1)
        assert result["return_code"] == -1
        assert "Timeout" in result["stderr"]
        sub.destroy(env)

    def test_checkpoint_restore(self, tmp_path):
        sub = LocalSandboxSubstrate(workspace_root=str(tmp_path / "sandboxes"))
        env = sub.create()
        sub.write_file(env, "/data.txt", "v1")

        cp_id = sub.checkpoint(env)
        sub.write_file(env, "/data.txt", "v2")
        assert sub.read_file(env, "/data.txt") == "v2"

        assert sub.restore(env, cp_id) is True
        assert sub.read_file(env, "/data.txt") == "v1"
        sub.destroy(env)

    def test_hibernate_wake(self, tmp_path):
        sub = LocalSandboxSubstrate(workspace_root=str(tmp_path / "sandboxes"))
        env = sub.create()
        sub.write_file(env, "/state.txt", "saved")

        assert sub.hibernate(env) is True
        assert env.status == "hibernated"

        assert sub.wake(env) is True
        assert env.status == "running"
        assert sub.read_file(env, "/state.txt") == "saved"
        sub.destroy(env)


class TestDockerSubstrate:
    """Tests for DockerSubstrate using real containers.

    These tests require Docker to be installed and running.
    They create real containers and clean them up after each test.
    """

    @pytest.fixture
    def docker_substrate(self):
        """Yield a DockerSubstrate and ensure cleanup after the test."""
        sub = DockerSubstrate()
        yield sub
        # Destroy any remaining environments
        for env in list(sub.list_environments()):
            sub.destroy(env)

    def test_create_and_destroy(self, docker_substrate):
        env = docker_substrate.create(template="test")
        assert env.env_id.startswith("docker-")
        assert env.substrate_type == "docker"
        assert env.status == "running"
        assert "container_id" in env.metadata

        assert len(docker_substrate.list_environments()) == 1
        docker_substrate.destroy(env)
        assert env.status == "destroyed"
        assert len(docker_substrate.list_environments()) == 0

    def test_execute_echo(self, docker_substrate):
        env = docker_substrate.create()
        result = docker_substrate.execute(env, "echo hello docker")
        assert result["stdout"].strip() == "hello docker"
        assert result["return_code"] == 0
        docker_substrate.destroy(env)

    def test_execute_with_error(self, docker_substrate):
        env = docker_substrate.create()
        result = docker_substrate.execute(env, "exit 42")
        assert result["return_code"] == 42
        docker_substrate.destroy(env)

    def test_file_io(self, docker_substrate):
        env = docker_substrate.create()
        docker_substrate.write_file(env, "/tmp/test.txt", "docker content")
        content = docker_substrate.read_file(env, "/tmp/test.txt")
        assert content == "docker content"
        docker_substrate.destroy(env)

    def test_read_missing_file(self, docker_substrate):
        env = docker_substrate.create()
        with pytest.raises(FileNotFoundError):
            docker_substrate.read_file(env, "/tmp/nonexistent.txt")
        docker_substrate.destroy(env)

    def test_checkpoint_and_restore(self, docker_substrate):
        env = docker_substrate.create()
        docker_substrate.write_file(env, "/tmp/data.txt", "v1")

        cp_id = docker_substrate.checkpoint(env)
        assert cp_id is not None
        assert env.checkpoint_count == 1

        docker_substrate.write_file(env, "/tmp/data.txt", "v2")
        assert docker_substrate.read_file(env, "/tmp/data.txt") == "v2"

        assert docker_substrate.restore(env, cp_id) is True
        # After restore the container is new; re-read file
        assert docker_substrate.read_file(env, "/tmp/data.txt") == "v1"
        docker_substrate.destroy(env)

    def test_hibernate_and_wake(self, docker_substrate):
        env = docker_substrate.create()
        docker_substrate.write_file(env, "/tmp/state.txt", "saved")

        assert docker_substrate.hibernate(env) is True
        assert env.status == "hibernated"

        assert docker_substrate.wake(env) is True
        assert env.status == "running"
        assert docker_substrate.read_file(env, "/tmp/state.txt") == "saved"
        docker_substrate.destroy(env)

    def test_multiple_environments_isolated(self, docker_substrate):
        env1 = docker_substrate.create()
        env2 = docker_substrate.create()
        docker_substrate.write_file(env1, "/tmp/file.txt", "A")
        docker_substrate.write_file(env2, "/tmp/file.txt", "B")
        assert docker_substrate.read_file(env1, "/tmp/file.txt") == "A"
        assert docker_substrate.read_file(env2, "/tmp/file.txt") == "B"
        docker_substrate.destroy(env1)
        docker_substrate.destroy(env2)

    def test_timeout(self, docker_substrate):
        env = docker_substrate.create()
        result = docker_substrate.execute(env, "sleep 10", timeout=1)
        assert result["return_code"] == -1
        assert "Timeout" in result["stderr"]
        docker_substrate.destroy(env)
