#!/usr/bin/env python3
"""
cotrade — Root Application Runner
==================================
Unified entry point to run the MetaTrader 5 gateway daemon, research lab,
bot backtests, and database management.

Usage:
  python run.py                     # Start the gateway daemon and web control panel
  python run.py server              # Explicit daemon server start
  python run.py bot sweep EURUSD    # Run strategy sweep over instrument data
  python run.py bot scan EURUSD     # Run pattern detector over instrument data
  python run.py db                  # Show database statistics and integrity
"""

import sys
import os
import argparse

# Wire backend into sys.path
_root = os.path.dirname(os.path.abspath(__file__))
_backend = os.path.join(_root, "backend")
_gateway = os.path.join(_backend, "gateway")

for _dir in (_root, _backend, _gateway):
    if _dir not in sys.path:
        sys.path.insert(0, _dir)


def cmd_server(args):
    """Start the Cotrade gateway daemon and dashboard."""
    if args.port:
        os.environ["CONY_PORT"] = str(args.port)
    if args.host:
        os.environ["CONY_HOST"] = str(args.host)
    if args.log_level:
        os.environ["CONY_LOG_LEVEL"] = str(args.log_level).upper()

    from deamon.__main__ import main as daemon_main
    return daemon_main()


def cmd_db(args):
    """Inspect the SQLite database stats and verify integrity."""
    from database.store import Store
    with Store() as store:
        print("Database stats:")
        for k, v in store.stats().items():
            print(f"  {k:<16}: {v}")
        integrity = store.check_integrity()
        print(f"  integrity check : {integrity}")
    return 0


def cmd_bot(args):
    """Delegate to the bot runner."""
    from tools.bot.runner import main as bot_main
    return bot_main(args.bot_args)


def main():
    parser = argparse.ArgumentParser(
        description="Cotrade — MetaTrader 5 gateway & trading dashboard"
    )
    sub = parser.add_subparsers(dest="command")

    # Server runner
    srv = sub.add_parser("server", help="Start the gateway server and dashboard")
    srv.add_argument("--port", "-p", type=int, default=None, help="Port to bind (default: 8890)")
    srv.add_argument("--host", "-H", default=None, help="Host to bind (default: 127.0.0.1)")
    srv.add_argument("--log-level", default=None, help="Logging level (DEBUG, INFO, WARNING)")

    # Database inspector
    sub.add_parser("db", help="Show database statistics and verify integrity")

    # Bot runner
    bot = sub.add_parser("bot", help="Run strategy backtests, sweeps, and pattern scans")
    bot.add_argument("bot_args", nargs=argparse.REMAINDER, help="Arguments passed to bot.runner")

    # Default to server if no sub-command passed
    if len(sys.argv) == 1:
        from deamon.__main__ import main as daemon_main
        return daemon_main()

    args = parser.parse_args()
    if args.command == "server":
        return cmd_server(args)
    elif args.command == "db":
        return cmd_db(args)
    elif args.command == "bot":
        return cmd_bot(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
