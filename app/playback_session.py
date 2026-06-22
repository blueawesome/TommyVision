from __future__ import annotations

import json
import os
import socket
import subprocess
import tempfile
import time
from pathlib import Path

from app.player import PlaybackError


STOP_EXIT_CODE = 42


class PlaybackSession:
    def __init__(self, config: dict, path: Path, start_seconds: float | None = None) -> None:
        player_config = config["player"]
        self.command = str(player_config.get("command", "mpv"))
        self.extra_args = list(player_config.get("extra_args", []))
        self.path = path
        self.start_seconds = start_seconds
        self.socket_path = _socket_path()
        self.input_conf_path = _input_conf_path()
        self.stop_snapshot_path = _stop_snapshot_path()
        self.stop_script_path = _stop_script_path()
        self.process: subprocess.Popen | None = None
        self.latest_position = None
        self.latest_duration = None

    def start(self) -> None:
        command = self._command(use_ipc=True)
        self._popen(command)
        socket_ready = self._wait_for_socket()
        if not socket_ready and self.process is not None and self.process.poll() is not None:
            self.cleanup()
            self._popen(self._command(use_ipc=False))

    def _command(self, use_ipc: bool) -> list[str]:
        self._write_input_helpers()
        command = [
            self.command,
            *self.extra_args,
            f"--input-conf={self.input_conf_path}",
            f"--script={self.stop_script_path}",
        ]
        if use_ipc:
            command.append(f"--input-ipc-server={self.socket_path}")
        if self.start_seconds and self.start_seconds > 0:
            command.append(f"--start={self.start_seconds}")
        command.append(str(self.path))
        return command

    def _popen(self, command: list[str]) -> None:
        try:
            self.process = subprocess.Popen(command)
        except FileNotFoundError as exc:
            raise PlaybackError(f"Could not find player command: {self.command}") from exc
        except OSError as exc:
            raise PlaybackError(f"Could not start playback: {exc}") from exc

    def is_running(self) -> bool:
        return self.process is not None and self.process.poll() is None

    def wait(self) -> None:
        if self.process is not None:
            self.process.wait()
        self.load_stop_snapshot()
        self.cleanup()

    def returncode(self) -> int | None:
        if self.process is None:
            return None
        return self.process.returncode

    def stop_and_save(self, resume_state) -> None:
        self.refresh_position()
        self.save_latest(resume_state)
        if not self.command_json(["quit"]):
            self.terminate()

    def refresh_position(self) -> None:
        position = self.get_property("time-pos")
        duration = self.get_property("duration")
        if position is not None:
            self.latest_position = position
        if duration is not None:
            self.latest_duration = duration

    def load_stop_snapshot(self) -> None:
        path = Path(self.stop_snapshot_path)
        if not path.exists():
            return
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except OSError:
            return
        if lines:
            self.latest_position = _number_or_none(lines[0])
        if len(lines) > 1:
            self.latest_duration = _number_or_none(lines[1])

    def save_latest(self, resume_state) -> None:
        resume_state.save_playback(self.path, self.latest_position, self.latest_duration)

    def play_pause(self) -> None:
        self.command_json(["cycle", "pause"])

    def seek(self, seconds: int) -> None:
        self.command_json(["seek", seconds, "relative"])

    def get_property(self, name: str):
        response = self.command_json(["get_property", name])
        if not isinstance(response, dict):
            return None
        if response.get("error") != "success":
            return None
        return response.get("data")

    def command_json(self, command: list) -> dict | None:
        if not Path(self.socket_path).exists():
            return None
        payload = json.dumps({"command": command}).encode("utf-8") + b"\n"
        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
                client.settimeout(0.5)
                client.connect(self.socket_path)
                client.sendall(payload)
                raw = client.recv(4096)
        except OSError:
            return None

        try:
            return json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return None

    def terminate(self) -> None:
        if self.process is not None and self.process.poll() is None:
            self.process.terminate()

    def cleanup(self) -> None:
        try:
            os.unlink(self.socket_path)
        except FileNotFoundError:
            pass
        except OSError:
            pass
        try:
            os.unlink(self.input_conf_path)
        except FileNotFoundError:
            pass
        except OSError:
            pass
        try:
            os.unlink(self.stop_script_path)
        except FileNotFoundError:
            pass
        except OSError:
            pass
        try:
            os.unlink(self.stop_snapshot_path)
        except FileNotFoundError:
            pass
        except OSError:
            pass

    def _wait_for_socket(self) -> bool:
        deadline = time.monotonic() + 2.0
        socket_file = Path(self.socket_path)
        while time.monotonic() < deadline and self.is_running():
            if socket_file.exists():
                return True
            time.sleep(0.05)
        return socket_file.exists()

    def _write_input_helpers(self) -> None:
        try:
            Path(self.input_conf_path).write_text(
                "SPACE cycle pause\n"
                "RIGHT seek 10 relative\n"
                "LEFT seek -10 relative\n"
                "q quit\n",
                encoding="utf-8",
            )
        except OSError:
            pass
        try:
            Path(self.stop_script_path).write_text(_stop_lua(self.stop_snapshot_path), encoding="utf-8")
        except OSError:
            pass


def _socket_path() -> str:
    timestamp = int(time.time() * 1000)
    temp_root = Path("/private/tmp")
    if not temp_root.exists():
        temp_root = Path(tempfile.gettempdir())
    return str(temp_root / f"tommyvision-mpv-{os.getpid()}-{timestamp}.sock")


def _input_conf_path() -> str:
    timestamp = int(time.time() * 1000)
    temp_root = Path("/private/tmp")
    if not temp_root.exists():
        temp_root = Path(tempfile.gettempdir())
    return str(temp_root / f"tommyvision-mpv-input-{os.getpid()}-{timestamp}.conf")


def _stop_snapshot_path() -> str:
    timestamp = int(time.time() * 1000)
    temp_root = Path("/private/tmp")
    if not temp_root.exists():
        temp_root = Path(tempfile.gettempdir())
    return str(temp_root / f"tommyvision-mpv-stop-{os.getpid()}-{timestamp}.txt")


def _stop_script_path() -> str:
    timestamp = int(time.time() * 1000)
    temp_root = Path("/private/tmp")
    if not temp_root.exists():
        temp_root = Path(tempfile.gettempdir())
    return str(temp_root / f"tommyvision-mpv-stop-{os.getpid()}-{timestamp}.lua")


def _stop_lua(snapshot_path: str) -> str:
    return f"""
local snapshot_path = [=[{snapshot_path}]=]

local function write_snapshot()
    local position = mp.get_property_number("time-pos")
    local duration = mp.get_property_number("duration")
    local file = io.open(snapshot_path, "w")
    if file then
        file:write(tostring(position or ""))
        file:write("\\n")
        file:write(tostring(duration or ""))
        file:write("\\n")
        file:close()
    end
    mp.commandv("quit", "{STOP_EXIT_CODE}")
end

mp.add_forced_key_binding("x", "tommyvision-stop", write_snapshot)
mp.add_forced_key_binding("X", "tommyvision-stop-shift", write_snapshot)
""".lstrip()


def _number_or_none(value) -> float | None:
    if value is None or value == "":
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if number != number:
        return None
    return number
