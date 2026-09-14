#!/usr/bin/env python3
"""Plesk deploy: explicit FTPS on port 21 only (never 990)."""
from __future__ import annotations

import os
import ssl
import sys
from ftplib import FTP, FTP_TLS, error_perm
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
TIMEOUT = 60
FILES = [
    (ROOT / "index.html", "index.html"),
    (ROOT / "index.php", "index.php"),
    (ROOT / "includes" / "header-nav.inc", "includes/header-nav.inc"),
]


def load_env() -> dict[str, str]:
    load_dotenv(ROOT / ".env")
    load_dotenv()
    cfg = {
        "host": os.getenv("PLESK_FTP_HOST", "").strip(),
        "port": os.getenv("PLESK_FTP_PORT", "21").strip() or "21",
        "user": os.getenv("PLESK_FTP_USER", "").strip(),
        "password": os.getenv("PLESK_FTP_PASS", "").strip().strip('"').strip("'"),
        "path": os.getenv("PLESK_FTP_PATH", "/httpdocs").strip() or "/httpdocs",
    }
    missing = [k for k in ("host", "user", "password") if not cfg[k]]
    if missing:
        print("Missing in .env:", ", ".join(missing))
        sys.exit(1)
    try:
        cfg["port_n"] = str(int(cfg["port"]))
    except ValueError:
        print("PLESK_FTP_PORT must be an integer")
        sys.exit(1)
    return cfg


def user_variants(user: str) -> list[str]:
    return [user]


class ExplicitFTP_TLS(FTP_TLS):
    """Explicit FTPS on port 21; reuse TLS session for the data channel (IIS/Plesk)."""

    def ntransfercmd(self, cmd, rest=None):
        conn, size = FTP.ntransfercmd(self, cmd, rest)
        if self._prot_p:
            conn = self.context.wrap_socket(
                conn,
                server_hostname=self.host if self.host and not self.host[0].isdigit() else None,
                session=self.sock.session,
            )
        return conn, size

    def storbinary(self, cmd, fp, blocksize=8192, callback=None, rest=None):
        self.voidcmd("TYPE I")
        with self.transfercmd(cmd, rest) as conn:
            while True:
                buf = fp.read(blocksize)
                if not buf:
                    break
                conn.sendall(buf)
                if callback:
                    callback(buf)
            try:
                conn.unwrap()
            except (TimeoutError, OSError, ssl.SSLError):
                pass
        return self.voidresp()


def try_ftps(host: str, port: int, user: str, password: str):
    ctx = ssl._create_unverified_context()
    ftp = ExplicitFTP_TLS(context=ctx)
    ftp.connect(host, port, timeout=TIMEOUT)
    welcome = ftp.getwelcome()
    ftp.login(user, password)
    ftp.prot_p()
    ftp.set_pasv(True)
    return ftp, welcome


def try_ftp(host: str, port: int, user: str, password: str):
    ftp = FTP()
    ftp.connect(host, port, timeout=TIMEOUT)
    welcome = ftp.getwelcome()
    ftp.login(user, password)
    ftp.set_pasv(True)
    return ftp, welcome


def diagnose(cfg: dict[str, str]):
    port = int(cfg["port_n"])
    password = cfg["password"]
    hosts = []
    for host in (cfg["host"], "ftp.colddirect.co.uk"):
        if host and host not in hosts:
            hosts.append(host)

    print("ENV: host=%s port=%s user=%s pass=set(%d chars) path=%s" % (
        cfg["host"], cfg["port_n"], cfg["user"], len(password), cfg["path"],
    ))
    print("Diagnose explicit FTPS then plain FTP on port %s (no 990)" % port)

    for host in hosts:
        host_dead = False
        for user in user_variants(cfg["user"]):
            if host_dead:
                break
            for mode, fn in (("FTPS", try_ftps), ("FTP", try_ftp)):
                label = f"{mode} {host}:{port} user={user}"
                try:
                    ftp, welcome = fn(host, port, user, password)
                    print("OK", label)
                    print("welcome:", welcome.splitlines()[0] if welcome else "")
                    print("connected")
                    return ftp
                except error_perm as exc:
                    print("FAIL", label, "->", exc)
                except (TimeoutError, OSError) as exc:
                    print("NET", label, "->", exc)
                    continue
                except ssl.SSLError as exc:
                    print("SSL", label, "->", exc)
    return None


def upload(ftp, local: Path, remote: str) -> None:
    remote = remote.replace("\\", "/")
    parent, name = os.path.split(remote)
    if parent:
        ftp.cwd(parent)
    with local.open("rb") as fh:
        ftp.storbinary("STOR " + name, fh)
    if parent:
        ftp.cwd("..")
    print("uploaded", remote)


def list_dir(ftp, path: str) -> None:
    print("Remote check", path)
    for name in ("index.html", "index.php"):
        try:
            print("MDTM", name, ftp.sendcmd("MDTM " + name))
        except Exception as exc:
            print("MDTM", name, exc)
        try:
            print("SIZE", name, ftp.size(name))
        except Exception as exc:
            print("SIZE", name, exc)


def main() -> int:
    cfg = load_env()
    print("Files before upload:")
    present: list[tuple[Path, str]] = []
    for local, remote in FILES:
        if local.is_file():
            print(f"  {local.name} -> {remote} ({local.stat().st_size} bytes)")
            present.append((local, remote))
        else:
            print("MISSING", local)

    ftp = diagnose(cfg)
    if ftp is None:
        print("No login succeeded. Password was not changed. Check Plesk FTP Access / Additional FTP accounts.")
        return 1

    try:
        ftp.cwd(cfg["path"])
        print("cwd", cfg["path"])
        for local, remote in present:
            upload(ftp, local, remote)
        list_dir(ftp, cfg["path"])
    finally:
        try:
            ftp.quit()
        except Exception:
            ftp.close()
    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
