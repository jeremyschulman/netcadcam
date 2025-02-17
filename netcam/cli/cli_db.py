import os

from netcad.logger import get_logger
from netcam import db

from .cli_netcam_main import cli


@cli.group("db")
def clig_netcam_db():
    """database commands"""
    pass


@clig_netcam_db.command("init")
def cli_db_init():
    """initialize the database"""
    db_name = os.environ["NETCAD_DESIGN"]
    db.db_init(db_name)
    get_logger().info(f"Database {db_name} initialized")


@clig_netcam_db.command("reset")
def cli_db_reset():
    """initialize the database"""
    db_name = os.environ["NETCAD_DESIGN"]
    db.db_erase(db_name)
    get_logger().info(f"Database {db_name} reset")


@clig_netcam_db.command("delete")
def cli_db_delete():
    """initialize the database"""
    db_name = os.environ["NETCAD_DESIGN"]
    db.db_delete(db_name)
    get_logger().info(f"Database {db_name} removed")
