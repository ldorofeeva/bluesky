import tempfile

import mypy.api
import pytest

from bluesky import abc as bs_abc
from ophyd import sim


def test_status():
    assert isinstance(sim.NullStatus(), bs_abc.Status)
    assert isinstance(sim.StatusBase(), bs_abc.Status)


def test_readable():
    assert isinstance(sim.motor1, bs_abc.Readable)
    assert isinstance(sim.det1, bs_abc.Readable)
    assert not isinstance(sim.flyer1, bs_abc.Readable)


def test_configurable():
    assert isinstance(sim.det_with_conf, bs_abc.Configurable)


def test_movable():
    assert isinstance(sim.motor1, bs_abc.Movable)
    assert not isinstance(sim.det1, bs_abc.Movable)
    assert not isinstance(sim.flyer1, bs_abc.Movable)


def test_flyable():
    assert isinstance(sim.flyer1, bs_abc.Flyable)
    assert not isinstance(sim.det1, bs_abc.Flyable)
    assert not isinstance(sim.motor1, bs_abc.Flyable)


def test_stageable():
    assert isinstance(sim.det1, bs_abc.Stageable)


def test_pausable():
    assert isinstance(sim.det1, bs_abc.Pausable)


def test_subscribable():
    assert isinstance(sim.det1, bs_abc.Subscribable)
    assert isinstance(sim.motor1, bs_abc.Subscribable)
    assert not isinstance(sim.flyer1, bs_abc.Subscribable)


def test_checkable():
    assert isinstance(sim.motor1, bs_abc.Checkable)


# I think the commented out tests pass because __getattr__ is implemented, but not sure
@pytest.mark.skip(reason="ophyd missing py.typed to communicate type hints to mypy")
@pytest.mark.parametrize(
    "type_, hardware, pass_",
    [
        ("Readable", "ABDetector(name='hi')", True),
        ("Readable", "SynAxis(name='motor1')", True),
        ("Readable", "TrivialFlyer()", False),
        ("Configurable", "ABDetector(name='hi')", True),
        # ("Movable", "ABDetector(name='hi')", False),  # mypy passed when it shouldn't
        ("Movable", "SynAxis(name='motor1')", True),
        ("Movable", "TrivialFlyer()", False),
        ("Stageable", "ABDetector(name='hi')", True),
        ("Pausable", "ABDetector(name='hi')", True),
        ("Checkable", "SynAxis(name='motor1')", True),
        # ("Flyable", "ABDetector(name='hi')", False),  # mypy passed when it shouldn't
        # ("Flyable", "SynAxis(name='motor1')", False),  # mypy passed when it shouldn't
        ("Flyable", "TrivialFlyer()", True),
        ("Subscribable", "SynAxis(name='motor1')", True),
    ],
)
def test_mypy(type_, hardware, pass_):
    template = f"""
from bluesky import abc as bs_abc
from ophyd import sim

var: bs_abc.{type_} = sim.{hardware}
"""

    with tempfile.NamedTemporaryFile("wt") as f:
        f.write(template)
        f.seek(0)
        stdout, stderr, exit = mypy.api.run([f.name])
        # pass true means exit 0, pass false means nonzero exit
        try:
            assert exit != pass_
        except AssertionError:
            print(stdout)
            print(stderr)
            raise
